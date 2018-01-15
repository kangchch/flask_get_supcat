#!/usr/bin/env python
# -*- coding: gb18030 -*

import sys
import pdb
import logging
import time
import requests
import re
import cx_Oracle
import urllib
import csv
import json
import traceback
from core_keyword import get_core_keyword


reload(sys)
sys.setdefaultencoding('gb18030')


def getTitleAndSupcatid(bcid):
    if not bcid:
        return ''
    url = 'http://s.hc360.com/getmmtlast.cgi?bc_id=%s&sys=ls' %(bcid)
    providerid = ''
    title = ''
    supcatid = ''
    keyword = ''
    r = None
    try:
        r = requests.get(url)
        title = re.findall(r'(?<=searchResultfoTitle":").*?(?=")', r.text)
        title = title[0] if title else ''
        supcatid = re.findall(r'(?<=searchResultfoRforumclass":").*?(?=")', r.text)
        supcatid = "".join(supcatid[0].split(':'))
    except Exception, e:
        print str(traceback.format_exc())
        print url, r.text if r else ''
    return title, keyword, supcatid

if len(sys.argv) < 2:
    print 'Usage: python %s <source filename>' %(__file__)
    sys.exit()

with open(sys.argv[1], 'rb') as fp_in, open('result.csv', 'wb') as fp_out:
    csv_writer = csv.writer(fp_out, dialect='excel')
    csv_reader = csv.DictReader(fp_in, dialect='excel')
    for row in csv_reader:
        # movehouse
        bc_id = row.get('BC_ID', '')
        whoinput = row.get('WHOINPUT', '')
        whoinput = whoinput
        ali_keyword_old = row.get('KEYWORD', '')
        ali_keyword = row.get('KEYWORD', '')
        if ali_keyword:
            ali_keyword = ali_keyword.replace('"', '').strip()
            ali_keyword = re.split(u'，|、|,', ali_keyword)
        title, supcatkeyword, supcatid_move = getTitleAndSupcatid(bc_id)
        if not title:
            continue

        core_keyword_title = get_core_keyword(title)
        core_keyword_alikeyword = ''
        core_keyword_title_and_alikeyword = ''
        core_keyword_alikeyword_one = ''
        core_keyword_title_and_alikeyword_one = ''
        if ali_keyword_old:
            core_keyword_alikeyword = get_core_keyword(ali_keyword_old)
            core_keyword_title_and_alikeyword = get_core_keyword(title, ali_keyword_old)
            if ali_keyword and ali_keyword[0]:
                core_keyword_alikeyword_one = get_core_keyword(ali_keyword[0])
                core_keyword_title_and_alikeyword_one = get_core_keyword(title, ali_keyword[0])

        csv_writer.writerow([bc_id, whoinput, title, ali_keyword_old.strip(),
                             core_keyword_title,
                             core_keyword_alikeyword,
                             core_keyword_title_and_alikeyword,
                             core_keyword_alikeyword_one,
                             core_keyword_title_and_alikeyword_one])


