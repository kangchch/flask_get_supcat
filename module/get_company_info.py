#-*- coding:utf-8 -*-
import sys
sys.path.append('/tools/python_common')
import re
import redis
import pymongo
from pymongo import MongoClient
import datetime
import json
from common_func import MyEncoder

redis_hosts = ['172.16.252.22', '172.16.248.22', '10.10.10.27']

def is_url(url):
    if re.match(r'^(https?:/{2})?(\w+\.)+\w+/?$', url):
        return True
    else:
        return False

def clear_url(url):
    if re.match(r'^https?:/{2}(\w+\.)+\w+/?$', url):
        url = url[url.find('//')+2:]
    if url[-1:] == '/':
        url = url[:-1]
    return url


class CompanyInfo():
    '''company info module, operator company info from mongo and redis'''

    def __init__(self):
        self.connect_redis()
        self.mongo_db = MongoClient('192.168.60.64', 10010).company_info

    def connect_redis(self):
        for host in redis_hosts:
            redis_pool = redis.ConnectionPool(host=host, port=6379, socket_timeout=2)
            r = redis.Redis(connection_pool = redis_pool)
            try:
                last_len = r.llen('ALI_COMPANY_KEYWORD_LIST')
                break
            except redis.exceptions.ConnectionError:
                continue
        self.redis_handle = redis.Redis(connection_pool = redis_pool)

    def inset_new(self, name, url):
        try:
            self.mongo_db.fill_info.insert({
                'company_name': name,
                'web_url': url,
                'web_status': 0 if url else 2,
                'web_company_name': '',
                'web_mp': '',
                'web_telephone': '',
                'baidu_v_status': 0,
                'qichacha_status':0 if name else 2,
                'qichacha_name': '',
                'qichacha_contacter': '',
                'qichacha_mp': '',
                'qichacha_telephone': '',
                'tianyancha_status':0 if name else 2,
                'tianyancha_company_name': '',
                'tianyancha_contacter': '',
                'tianyancha_mp': '',
                'tianyancha_telephone': '',
                'insert_date': datetime.datetime.now(),
                'update_date': datetime.datetime.now(),
                ## add tianyacha_m 20180109
                'tianyancha_company_status':0 
                })
            if name:
                self.redis_handle.lpush('COMPANY_NAME_QUEUE', name)
                self.redis_handle.lpush('COMPANY_STATUS_QUEUE', name)
            if url:
                self.redis_handle.lpush('COMPANY_URL_QUEUE', url)
        except pymongo.errors.DuplicateKeyError:
            pass

    def get_company_info(self, name='', url='', nocache=False):
        if not name and not url:
            return {'errmsg': 'empty company name and empty url!'}

        item = {}
        json_item = ''
        ## find from redis cache
        if not nocache:
            if name:
                json_item = self.redis_handle.hget('COMPANY_NAME_INFO', name)
            elif url:
                json_item = self.redis_handle.hget('COMPANY_URL_INFO', url)
        if json_item:
            item = json.loads(json_item)
            if item['errmsg'] != 'standby':
                return json_item

        ## redis cache not find, find from mongo
        m_item = ''
        if name:
            m_item = self.mongo_db.fill_info.find_one({'company_name': name})
            if m_item and url and (not m_item.get('web_url', '')):
                self.mongo_db.fill_info.update({'company_name': name}, {'$set': {'web_url': url, 'web_status': 0}})
                self.redis_handle.lpush('COMPANY_URL_QUEUE', url)
            if m_item and url and (not m_item.get('tianyancha_company_status', '')):
                self.mongo_db.fill_info.update({'company_name': name}, {'$set': {'tianyancha_company_status': 0}})
                self.redis_handle.lpush('COMPANY_STATUS_QUEUE', name)
        if not m_item and url:
            m_item = self.mongo_db.fill_info.find_one({'web_url': url})
            if m_item and name and (not m_item.get('company_name', '')):
                self.mongo_db.fill_info.update({'web_url': url}, {'$set': {'company_name': name, 'tianyancha_status': 0}})
                self.redis_handle.lpush('COMPANY_NAME_QUEUE', name)

        ## not find
        item = {'company_name': name, 'url': url, 'errmsg': 'standby'}
        if not m_item or (m_item.get('web_status', 0) == 0 and m_item.get('tianyancha_status', 0) == 0):
            if not m_item:
                self.inset_new(name, url)
            return item

        ## find
        item['company_name'] = name if name else m_item.get('company_name', '')
        item['web_company_name'] = m_item.get('web_company_name', '')
        item['contacter'] = m_item.get('web_contacter', '') if m_item.get('web_contacter', '') else m_item.get('tianyancha_contacter', '')
        item['telephone'] = m_item.get('web_telephone', '') if m_item.get('web_telephone', '') else m_item.get('tianyancha_telephone', '')
        item['mp'] = m_item.get('web_mp', '') if m_item.get('web_mp', '') else m_item.get('tianyancha_mp', '')
        item['web_status'] = m_item.get('web_status', '')
        item['tianyancha_status'] = m_item.get('tianyancha_status', 0)
        item['update_date'] = m_item.get('update_date', '')
        item['url'] = url if url else m_item.get('web_url', '')
        #add tianyancha_m 20180109
        item['tianyancha_company_status'] = m_item.get('tianyancha_company_status', 0)
        if not item['telephone'] and not item['mp']:
            if m_item.get('web_status', 0) == 0 or m_item.get('tianyancha_status', 0) == 0:
                item = {'company_name': name, 'url': url, 'errmsg': 'standby'}
                return item

        ## insert to redis cache
        item['errmsg'] = 'ok' if item['telephone'] or item['mp'] else 'not find'
        if name:
            self.redis_handle.hset('COMPANY_NAME_INFO', name, json.dumps(item, cls=MyEncoder))
        if url:
            self.redis_handle.hset('COMPANY_URL_INFO', url, json.dumps(item, cls=MyEncoder))
        return item


if __name__ == '__main__':
    c = CompanyInfo()
    print c.get_company_info('深圳市衔尾蛇网络科技有限公司', nocache=True)
