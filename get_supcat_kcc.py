from flask import Flask
from flask import request
from flask import Response
from flask import abort
import re
import sys
sys.path.append('/tools/python_common')
sys.path.append('module')
from common_func import MyEncoder
from get_company_info import CompanyInfo
from get_block_word import BlockWord

from supcat_correct.supcat_correct import SupcatCorrent
import json


sc = SupcatCorrent()
bw = BlockWord()
def create_app():
    app = Flask(__name__)
    return app

app = create_app()

@app.route('/GetSupcat')
def get_supcat():
    if request.method == 'GET':
        if 'w' in request.args:
            word = request.args['w'].encode('gb18030')
            body = sc.get_body(word)
            #body['supcatid'] = '035001'
            #body['step'] = 5
            body_json = json.dumps(body, ensure_ascii=False).encode('gb18030', 'ignore')
            #body_json = json.dumps('Hello get supcat', ensure_ascii=False).encode('gb18030', 'ignore')
            return Response(body_json, content_type='text/html; charset=gbk')
        elif 'title' in request.args:
            word = request.args['title'].encode('gb18030')
            body = sc.get_body(word)
            #body['supcatid'] = '035001'
            #body['step'] = 5
            body_json = json.dumps(body, ensure_ascii=False).encode('gb18030', 'ignore')
            #body_json = json.dumps('Hello get supcat', ensure_ascii=False).encode('gb18030', 'ignore')
            return Response(body_json, content_type='text/html; charset=gbk')
        else:
            abort(404)

company_info = CompanyInfo()

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

def return_errmsg(errmsg):
    item = {'errmsg': errmsg}
    body_json = json.dumps(item)
    return Response(body_json, content_type='text/html; charset=utf-8')

@app.route('/GetCompanyInfo')
def get_company_info():
    if request.method == 'GET':
        ## 0. check params
        name = request.args.get('name', '').strip()
        company_name = name if not is_url(name) else ''
        url_tmp = request.args.get('url', '').strip()
        url = clear_url(url_tmp) if is_url(url_tmp) else ''
        if not company_name and not url:
            return return_errmsg('error params! name=%s url=%s' % (name, url_tmp))

        ## 1. call get_company_info and response
        item = {}
        app.logger.info('call company_info company_name:%s url:%s', company_name, url)
        if 'nocache' in request.args and request.args['nocache'].strip().lower() == 'true':
            item = company_info.get_company_info(company_name, url, nocache=True)
        else:
            item = company_info.get_company_info(company_name, url, nocache=False)

        body_json = json.dumps(item, cls=MyEncoder) if isinstance(item, dict) else item
        return Response(body_json, content_type='text/html; charset=utf-8')
    else:
        abort(404)

@app.route('/GetBlockWord')
def get_block_word():
    if request.method == 'GET':
        body_json = bw.get_block_word()
        return Response(body_json, content_type='text/html; charset=utf-8')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8989)
