#coding:gb18030
import sys
import datetime
import traceback
import pymongo
import json
from core_keyword.core_keyword import get_core_keyword

VERSION = "1002"

class SupcatCorrentError(Exception):
    pass

class SupcatCorrent():
    def __init__(self):
        self.mongo_db = None
        self.connect_mongo()

    def __del__(self):
        pass

    def get_version(self):
        return VERSION

    def connect_mongo(self, ip='192.168.60.64', port=10010):
        self.mongo_db = pymongo.MongoClient(ip, port).supcat

    def get_supcat_path(self, supcatid):
        if supcatid:
            record = self.mongo_db.supcat_id_path.find_one({'supcatid': supcatid}, {'supcatpath': 1})
            return record.get('supcatpath', '')
        return ''

    def get_body(self, keyword):
        step = 0
        supcatid = ''
        supcatpath = ''
        cut_keyword = ''
        ret = 1
        errmsg = ''
        if not keyword:
            ret = -1
            errmsg = 'keyword is empty!'
            body = {'supcatid': supcatid,
                    'supcatpath': supcatpath,
                    'step': step,
                    'cut_keyword': cut_keyword,
                    'ret': ret,
                    'errmsg': errmsg,
                    'version': VERSION}
            return body

        step += 1
        for _ in range(2):
            record = self.mongo_db.supcat_last_level.find_one({'supcatname': keyword.decode('gb18030')},
                                                         {'supcatid': 1})
            if record:
                supcatid =  record['supcatid']
                supcatpath = self.get_supcat_path(record['supcatid'])
                break

            step += 1
            record = self.mongo_db.supcat_keyword.find_one({'keyword': keyword.decode('gb18030')},
                                                      {'supcatid': 1})
            if record:
                supcatid =  record['supcatid']
                supcatpath = self.get_supcat_path(record['supcatid'])
                break

            step += 1
            if step == 5:
                # 其他
                record = self.mongo_db.supcat_last_level.find_one({'supcatname': u'\u5176\u4ed6'},
                                                             {'supcatid': 1})
                supcatid =  record['supcatid']
                supcatpath = self.get_supcat_path(record['supcatid'])
                break

            try:
                keyword = get_core_keyword(keyword)
                cut_keyword = keyword
                continue
            except Exception, e:
                step = 0
                ret = -1
                errmsg = 'get_core_keyword error! (%s)' % (str(e))
                break

        body = {'supcatid': supcatid,
                'supcatpath': supcatpath,
                'step': step,
                'cut_keyword': cut_keyword.decode('gb18030'),
                'ret': ret,
                'errmsg': errmsg,
                'version': VERSION}

        return body

if __name__=='__main__':
    reload(sys)
    sys.setdefaultencoding('gb18030')

    sc = SupcatCorrent()

    if len(sys.argv) > 1:
        word = sys.argv[1]
        print sc.get_body(word)
        print json.dumps(sc.get_body(word), ensure_ascii=False)
    else:
        word_list = [
            '',
            '苹果',
            '富士苹果',
            '北京苹果',
            '三星手机蘑菇充气城堡',
            '哈哈哈哈哈']
        for word in word_list:
            print sc.get_body(word)
            print json.dumps(sc.get_body(word), ensure_ascii=False)
