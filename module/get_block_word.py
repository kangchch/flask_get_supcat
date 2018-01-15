#-*- coding:utf-8 -*-
import sys
sys.path.append('/tools/python_common')
import re
import datetime
import json
from common_func import MyEncoder

block_words = [
        u'女性',
        u'男性',
        u'成人',
        u'充气',
        u'慰',
        u'情趣',
        u'人体',
        u'男用',
        u'乳房',
        u'情趣',
        u'阳具',
        u'贞操',
        u'全硅胶非半实体',
        u'假胸',
        u'娃娃',
        u'快乐器',
        u'飞机杯'
        ]

class BlockWord():
    '''company info module, operator company info from mongo and redis'''

    def __init__(self):
        pass

    def get_block_word(self):
        return json.dumps(block_words)


if __name__ == '__main__':
    c = BlockWord()
    print c.get_block_word()
