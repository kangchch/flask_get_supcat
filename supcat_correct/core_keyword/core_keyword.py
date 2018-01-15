#coding=gb18030
import sys
import socket
import struct
import random
from ipdb import set_trace
from copy import deepcopy

# HOST_LIST = [{'ip': '192.168.245.37', 'port': 3378}]
# HOST_LIST = [{'ip': '192.168.245.37', 'port': 3377}]
HOST_LIST = [{'ip': '192.168.60.28', 'port': 3377},
        {'ip': '192.168.60.48', 'port': 3377}]

def get_core_keyword(title, keyword = '', debug=False):
    assert(title)

    if isinstance(title, unicode):
        title = title.encode('gb18030')
    if isinstance(keyword, unicode):
        keyword = keyword.encode('gb18030')

    if keyword:
        send_buf = '2010111000020000%08d%s###%s' % (len(title + keyword) + 3, title, keyword)
    else:
        send_buf = '2010111000020000%08d%s' % (len(title), title)

    host_list = deepcopy(HOST_LIST)
    random.shuffle(host_list)
    for i, host in enumerate(host_list):
        try:
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.connect((host['ip'], host['port']))
            while True:
                s.sendall(send_buf)
                data = s.recv(len(send_buf) * 2)
                if data:
                    break
            s.close()
            break
        except:
            if host == HOST_LIST[-1]:
                raise
            else:
                continue

    if debug:
        print data

    for keyword in data.split(" "):
        if len(keyword) > 2 and keyword[-2:] == '/1':
            return keyword[:-2]
    return ''


if __name__ == '__main__':
    title = '提供各种规格皮革和塑料骰盅加工生产'
    keyword = ''
    if len(sys.argv) > 2:
        title = sys.argv[1]
        keyword = sys.argv[2]
    elif len(sys.argv) > 1:
        title = sys.argv[1]

    print get_core_keyword(title, keyword, True)


