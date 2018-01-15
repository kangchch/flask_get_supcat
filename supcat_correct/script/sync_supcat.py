#coding=gb18030
import sys
import os
import cx_Oracle
import pymongo
import datetime
import codecs
from tqdm import tqdm
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from ipdb import set_trace
import MySQLdb

os.system('export LANG=zh_CN.GB18030')
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.ZHS16GBK'

reload(sys)
sys.setdefaultencoding('gb18030')

def logInit(loglevel, log_file, backup_count=0, consoleshow=False):
	fileTimeHandler = TimedRotatingFileHandler(log_file, "D", 1, backup_count)
	formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s')
	fileTimeHandler.setFormatter(formatter)
	logging.getLogger('').addHandler(fileTimeHandler)
	logging.getLogger('').setLevel(loglevel)
	if consoleshow:
		console = logging.StreamHandler()
		console.setLevel(loglevel)
		console.setFormatter(formatter)
		logging.getLogger('').addHandler(console)

def insert_smanager_cut_table(mysql_db, keywords, source):
    cursor = mysql_db.cursor()
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    insert_ok_count = 0
    for keyword in keywords:
        select_sql = "select count(1) from s_optimal_query_keyword where query=%s"
        cursor.execute(select_sql, (keyword,))
        if cursor.fetchone()[0] == 0:
            insert_sql = '''
            insert into s_optimal_query_keyword(query,sydate,source)
            value(%s, %s, %s)
            '''
            cursor.execute(insert_sql, (keyword, dt, source))
            insert_ok_count += 1
    mysql_db.commit()
    cursor.close()
    return insert_ok_count

def process_keyword(oracle_db, mysql_db, source):
    oracle_cur = oracle_db.cursor()
    mysql_cur = mysql_db.cursor()

    # 0. get not match keyword
    keywords = oracle_cur.execute("SELECT KEYWORD FROM ALI_KEYWORD_NOT_MATCH where state = 0").fetchall()
    keywords = [keyword[0].decode('gb18030', 'replace').strip().encode('utf-8') for keyword in keywords]


    # 1. get keyword supcatid from smanager
    sql = '''
select a.keyword, b.cat_id
from s_optimal_keyword  a
left join s_optimal_keyword_category b
on a.id = b.kid
where a.keyword=%s
'''
    update_items = []
    nomatch_keywords = []
    catid_not_match_count = 0
    for keyword in keywords:
        mysql_cur.execute(sql, (keyword,))
        results = mysql_cur.fetchall()
        if results:
            keyword, catid = results[0]
        else:
            catid = ''

        if catid:
            mysql_cur.execute("select supcatid from s_optimal_category_supcat where cat_id=%d" % (catid))
            supcatid = mysql_cur.fetchone()
            if supcatid and supcatid[0]:
                update_items.append((supcatid[0], keyword.encode('gb18030')))
            else:
                catid_not_match_count += 1
                logging.error('[FAILED] catid not match supcatid! catid=%d keyword=%s', catid, keyword)
        else:
            nomatch_keywords.append(keyword)

    # 2. update match keyword supcatid
    update_sql = "update ALI_KEYWORD_NOT_MATCH set new_supcatid=:1, match_date=sysdate, state='1' where keyword=:2"
    oracle_cur.executemany(update_sql, update_items)
    oracle_db.commit()

    # 3. insert not match keyword to smanager
    insert_ok_count = insert_smanager_cut_table(mysql_db, nomatch_keywords, source)
    logging.info('[cut keyword] get not match keyword %d, matched %d(catid not find supcatid %d), insert new keyword to smanager table %d',
                 len(keywords), len(update_items), catid_not_match_count, insert_ok_count)

    oracle_cur.close()
    mysql_cur.close()

def process_title(oracle_db, mysql_db, source):
    oracle_cur = oracle_db.cursor()
    mysql_cur = mysql_db.cursor()

    # 0. get all title
    titles = oracle_cur.execute("SELECT TITLE FROM ALI_BC_NOT_MATCH where state = 0").fetchall()
    titles = set(i[0].decode('gb18030', 'replace')[:60] for i in titles)

    # 1. title cut keyword and update ALI_BC_NOT_MATCH 
    cut_keywords = []
    insert_titles = []
    for title in titles:
        cut_keyword = core_keyword.get_core_keyword(title.encode('gb18030'))
        if cut_keyword:
            cut_keyword = cut_keyword.decode('gb18030').strip()
            cut_keywords.append(cut_keyword)
            sql = "update ALI_BC_NOT_MATCH set CUT_KEYWORD = :1 where TITLE = :2"
            oracle_cur.execute(sql, (cut_keyword.encode('gb18030'), title.encode('gb18030')))
        else:
            insert_titles.append(title.encode('utf-8'))
    oracle_db.commit()

    # 2. insert cut keyword to ALI_KEYWORD_NOT_MATCH
    insert_oracle_ok_count = 0
    for keyword in cut_keywords:
        sql = "insert into ALI_KEYWORD_NOT_MATCH(id, keyword, keyword_type) values(ALI_KEYWORD_NOT_MATCH_SEQ.nextval, :1, '2')"
        try:
            oracle_cur.execute(sql, (keyword,))
            insert_oracle_ok_count += 1
        except Exception, e:
            if str(e).find('ORA-00001') < 0:
                logging.error('[FAILED] insert ALI_KEYWORD_NOT_MATCH failed! keyword=%s (%s)', keyword, str(e))
    oracle_db.commit()

    # 3. insert not cut_keyword title to smanager
    insert_mysql_ok_count = insert_smanager_cut_table(mysql_db, insert_titles, source)


    logging.info('[title] get not cut title %d. cut ok %d, insert ALI_KEYWORD_NOT_MATCH %d. cut failed %d, insert new title to smansger %d',
                 len(titles), len(cut_keywords), insert_oracle_ok_count, len(insert_titles), insert_mysql_ok_count)
    oracle_cur.close()
    mysql_cur.close()


if __name__ == '__main__':
    cur_path = os.path.split(os.path.realpath(__file__))[0]
    os.chdir(cur_path)
    sys.path.append("..")
    from core_keyword import core_keyword

    logInit(logging.DEBUG, cur_path + '/logs/sync.log', 0, True)

    DB_STR='match/jkn65#ud@192.168.100.111/move'
    # DB_STR='match/bfdds06fd@192.168.44.133:1521/bjdt4'
    oracle_db_move = cx_Oracle.connect(DB_STR)

    mysql_db = MySQLdb.connect(host="192.168.100.62",
                         port=3308,
                         user="searchuser",
                         passwd="Ujhb3trDk",
                         db="searchtj",
                         charset="utf8")
    # mysql_db = MySQLdb.connect(host="192.168.44.233",
                         # port=3306,
                         # user="root",
                         # passwd="root",
                         # db="searchtj",
                         # charset="utf8")
    process_title(oracle_db_move, mysql_db, 13)
    process_keyword(oracle_db_move, mysql_db, 12)

    DB_STR='snatch/e3hAbdiK@192.168.100.148/snatch'
    # DB_STR='snatchdb/bfdds06fd@192.168.44.250/prod'
    oracle_db_3y = cx_Oracle.connect(DB_STR)
    process_title(oracle_db_3y, mysql_db, 15)
    process_keyword(oracle_db_3y, mysql_db, 14)

    oracle_db_move.close()
    oracle_db_3y.close()
    mysql_db.close()
