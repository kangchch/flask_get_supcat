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

def update_supcat_keyword(mongo_db, filename):
    fp = codecs.open(filename, 'r', 'gb18030')
    records = [record.strip().decode('gb18030') for record in fp]
    file_supcat_items = {}
    for record in records:
        items = record.split('=')
        if len(items) < 2:
            continue
        keyword = items[0]
        supcat_list = []
        for supcat_str in items[1].split(';'):
            supcat = supcat_str.replace(':', '')
            supcat_list.append(supcat)
        file_supcat_items[keyword] = supcat_list

    mongo_records = [record for record in mongo_db.supcat_keyword.find({}, {'keyword': 1,
                                                                 'supcatid': 1})]
    mongo_supcat_items = {item['keyword']: item['supcatid'] for item in mongo_records} if mongo_records and mongo_records[0] else {}
    mongo_keywords = mongo_supcat_items.keys()
    file_keywords = file_supcat_items.keys()

    # set invalid
    keywords = list(set(mongo_keywords) - set(file_keywords))
    logging.info('[invalid] update start (%d)', len(keywords))
    for keyword in keywords:
        mongo_db.supcat_keyword.update({'keyword': keyword},
                                       {'$set':
                                        {'is_valid': False,
                                         'check_date': datetime.datetime.now(),
                                         'update_date': datetime.datetime.now()}})
    logging.info('[invalid] update end (%d)', len(keywords))

    # insert new 
    keywords = list(set(file_keywords) - set(mongo_keywords))
    logging.info('[new] insert start (%d)', len(keywords))
    insert_items = []
    for keyword in keywords:
        supcat_all = file_supcat_items[keyword]
        insert_items.append({'keyword': keyword,
                             'supcatid': supcat_all[0],
                             'supcatid_all': supcat_all,
                             'is_valid': True,
                             'insert_date': datetime.datetime.now(),
                             'check_date': datetime.datetime.now(),
                             'update_date': datetime.datetime.now()})
    if insert_items:
        mongo_db.supcat_keyword.insert_many(insert_items)
    logging.info('[new] insert end (%d)', len(keywords))

    # update
    keywords = list(set(file_keywords) & set(mongo_keywords))
    logging.info('[update] update start (%d)', len(keywords))
    insert_items = []
    update_count = 0
    for keyword in keywords:
        supcat_all = file_supcat_items[keyword]
        if mongo_supcat_items[keyword] == supcat_all[0]:
            continue
        mongo_db.supcat_keyword.update_one({'keyword': keyword},
                                       {'$set':
                                        {'supcatid': supcat_all[0],
                                         'supcatid_all': supcat_all,
                                         'is_valid': True,
                                         'check_date': datetime.datetime.now(),
                                         'update_date': datetime.datetime.now()}})
        update_count += 1
    logging.info('[update] update end (%d:%d)', len(keywords), update_count)




def update_supcat_last_level(mongo_db, oracle_cur):
    oracle_cur.execute("select s.SUPCATNAME, s.supcatid from supermarket_cat s where s.show='1' and s.state='0' and catid!=0")
    results = oracle_cur.fetchall()
    oracle_supcat_items = {}
    for item in results:
        oracle_supcat_items[item[0].decode('gb18030')] = item[1]
    oracle_supcat_items[u'\u5176\u4ed6'] = '035001' #其他

    mongo_records = [record for record in mongo_db.supcat_last_level.find({}, {'supcatname': 1, 'supcatid': 1})]
    mongo_supcat_items = {item['supcatname']: item['supcatid'] for item in mongo_records} if mongo_records and mongo_records[0] else {}

    mongo_keywords = mongo_supcat_items.keys()
    oracle_keywords = oracle_supcat_items.keys()

    # set invalid
    keywords = list(set(mongo_keywords) - set(oracle_keywords))
    logging.info('[invalid] update start (%d)', len(keywords))
    for keyword in keywords:
        mongo_db.supcat_last_level.update({'supcatname': keyword},
                                       {'$set':
                                        {'is_valid': False,
                                         'check_date': datetime.datetime.now(),
                                         'update_date': datetime.datetime.now()}})
    logging.info('[invalid] update end (%d)', len(keywords))

    # insert new 
    keywords = list(set(oracle_keywords) - set(mongo_keywords))
    logging.info('[new] insert start (%d)', len(keywords))
    insert_items = []
    for keyword in keywords:
        insert_items.append({'supcatname': keyword,
                             'supcatid': oracle_supcat_items[keyword],
                             'is_valid': True,
                             'insert_date': datetime.datetime.now(),
                             'check_date': datetime.datetime.now(),
                             'update_date': datetime.datetime.now()})
    if insert_items:
        mongo_db.supcat_last_level.insert_many(insert_items)
    logging.info('[new] insert end (%d)', len(keywords))

    # update
    keywords = list(set(oracle_keywords) & set(mongo_keywords))
    logging.info('[update] update start (%d)', len(keywords))
    insert_items = []
    update_count = 0
    for keyword in keywords:
        if mongo_supcat_items[keyword] == oracle_supcat_items[keyword]:
            continue
        mongo_db.supcat_last_level.update_one({'supcatname': keyword},
                                       {'$set':
                                        {'supcatid': oracle_supcat_items[keyword],
                                         'is_valid': True,
                                         'check_date': datetime.datetime.now(),
                                         'update_date': datetime.datetime.now()}})
        update_count += 1
    logging.info('[update] update end (%d:%d)', len(keywords), update_count)

def update_supcat_id_path(mongo_db, oracle_cur):
    oracle_cur.execute("select s.supcatid, getsupcatname(s.supcatid) from supermarket_cat s where s.show='1' and s.state='0' and catid!=0")
    results = oracle_cur.fetchall()
    oracle_supcat_items = {}
    for item in results:
        oracle_supcat_items[item[0]] = item[1].decode('gb18030')

    mongo_records = [record for record in mongo_db.supcat_id_path.find({}, {'supcatpath': 1, 'supcatid': 1})]
    mongo_supcat_items = {item['supcatid']: item['supcatpath'] for item in mongo_records} if mongo_records and mongo_records[0] else {}

    mongo_supcatids = mongo_supcat_items.keys()
    oracle_supcatids = oracle_supcat_items.keys()

    # set invalid
    supcatids = list(set(mongo_supcatids) - set(oracle_supcatids))
    logging.info('[invalid] update start (%d)', len(supcatids))
    for supcatid in supcatids:
        mongo_db.supcat_id_path.update({'supcatid': supcatid},
                                       {'$set':
                                        {'is_valid': False,
                                         'check_date': datetime.datetime.now(),
                                         'update_date': datetime.datetime.now()}})
    logging.info('[invalid] update end (%d)', len(supcatids))

    # insert new 
    supcatids = list(set(oracle_supcatids) - set(mongo_supcatids))
    logging.info('[new] insert start (%d)', len(supcatids))
    insert_items = []
    for supcatid in supcatids:
        insert_items.append({'supcatid': supcatid,
                             'supcatpath': oracle_supcat_items[supcatid],
                             'is_valid': True,
                             'insert_date': datetime.datetime.now(),
                             'check_date': datetime.datetime.now(),
                             'update_date': datetime.datetime.now()})
    if insert_items:
        mongo_db.supcat_id_path.insert_many(insert_items)
    logging.info('[new] insert end (%d)', len(supcatids))

    # update
    supcatids = list(set(oracle_supcatids) & set(mongo_supcatids))
    logging.info('[update] update start (%d)', len(supcatids))
    insert_items = []
    update_count = 0
    for supcatid in supcatids:
        if mongo_supcat_items[supcatid] == oracle_supcat_items[supcatid]:
            continue
        mongo_db.supcat_id_path.update_one({'supcatid': supcatid},
                                       {'$set':
                                        {'supcatpath': oracle_supcat_items[supcatid],
                                         'is_valid': True,
                                         'check_date': datetime.datetime.now(),
                                         'update_date': datetime.datetime.now()}})
        update_count += 1
    logging.info('[update] update end (%d:%d)', len(supcatids), update_count)

import MySQLdb
def update_smanager_keyword(mongo_db):
    db = MySQLdb.connect(host="192.168.100.62",
                         port=3308,
                         user="searchuser",
                         passwd="Ujhb3trDk",
                         db="searchtj",
                         charset="utf8")
    # db = MySQLdb.connect(host="192.168.44.233",
                         # port=3306,
                         # user="root",
                         # passwd="root",
                         # db="searchtj",
                         # charset="utf8")
    cursor = db.cursor()
    sql = '''
select b.keyword, a.speech
from s_optimal_keyword_speech  a
left join s_optimal_keyword b
on a.kid = b.id
where a.speech='11000000'
    '''
    cursor.execute(sql)
    results = cursor.fetchall()
    mysql_items = {}
    for item in results:
        mysql_items[item[0]] = item[1]

    mongo_records = [record for record in mongo_db.smanager_keyword.find({},
                                                                         {'keyword': 1,
                                                                          'speech': 1})]
    mongo_smanager_keywords = {item['keyword']: item['speech'] for item in mongo_records} if mongo_records and mongo_records[0] else {}

    mysql_keywords = mysql_items.keys()
    mongo_keywords = mongo_smanager_keywords.keys()

    # set invalid
    keywords = list(set(mongo_keywords) - set(mysql_keywords))
    logging.info('[invalid] update start (%d)', len(keywords))
    for keyword in keywords:
        mongo_db.smanager_keyword.update({'keyword': keyword},
                                       {'$set':
                                        {'is_valid': False,
                                         'check_date': datetime.datetime.now(),
                                         'update_date': datetime.datetime.now()}})
    logging.info('[invalid] update end (%d)', len(keywords))

    # insert new 
    keywords = list(set(mysql_keywords) - set(mongo_keywords))
    logging.info('[new] insert start (%d)', len(keywords))
    insert_items = []
    for keyword in keywords:
        speech = mysql_items[keyword]
        insert_items.append({'keyword': keyword,
                             'speech': speech,
                             'is_valid': True,
                             'insert_date': datetime.datetime.now(),
                             'check_date': datetime.datetime.now(),
                             'update_date': datetime.datetime.now()})
    if insert_items:
        mongo_db.smanager_keyword.insert_many(insert_items)
    logging.info('[new] insert end (%d)', len(keywords))

    # update
    keywords = list(set(mysql_keywords) & set(mongo_keywords))
    logging.info('[update] update start (%d)', len(keywords))
    insert_items = []
    update_count = 0
    for keyword in keywords:
        speech = mysql_items[keyword]
        if mongo_smanager_keywords[keyword] == speech:
            continue
        mongo_db.smanager_keyword.update_one({'keyword': keyword},
                                       {'$set':
                                        {'speech': speech,
                                         'is_valid': True,
                                         'check_date': datetime.datetime.now(),
                                         'update_date': datetime.datetime.now()}})
        update_count += 1
    logging.info('[update] update end (%d:%d)', len(keywords), update_count)

    db.close()


if __name__ == '__main__':
    cur_path = os.path.split(os.path.realpath(__file__))[0]
    logInit(logging.DEBUG, cur_path + '/logs/import.log', 0, True)

    os.chdir(cur_path)
    os.system('scp root@192.168.60.180:/app/cache/keycode.txt .')

    mongo_db = pymongo.MongoClient('192.168.60.64', 10010).supcat
    # mongo_db = pymongo.MongoClient('192.168.245.41', 10001).supcat

    # supcat_keyword 
    logging.info('update supcat_keyword start')
    update_supcat_keyword(mongo_db, cur_path + '/keycode.txt')
    logging.info('update supcat_keyword end')

    DB_STR='match/jkn65#ud@192.168.100.111/move'
    oracle_conn= cx_Oracle.connect(DB_STR)
    oracle_cur = oracle_conn.cursor()

    # supcat_last_level 
    logging.info('update supcat_last_level start')
    update_supcat_last_level(mongo_db, oracle_cur)
    logging.info('update supcat_last_level end')

    # supcat_id_path
    logging.info('update supcat_id_path start')
    update_supcat_id_path(mongo_db, oracle_cur)
    logging.info('update supcat_id_path end')

    # smanager_keyword
    logging.info('update smanager_keyword start')
    update_smanager_keyword(mongo_db)
    logging.info('update smanager_keyword end')

    oracle_cur.close()
    oracle_conn.close()
