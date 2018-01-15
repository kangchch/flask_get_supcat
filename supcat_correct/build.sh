#!/bin/sh
cur_path=$(cd `dirname $0`; pwd)
swig -c++ -python -o supcat_wrap.cpp supcat.i
gcc -fPIC -c supcat_wrap.cpp -o supcat_wrap.o -I /usr/local/include/python2.7/
gcc -fPIC -c supcat.cpp -o supcat.o
g++ -shared supcat_wrap.o supcat.o -l HCSegDll -L $cur_path -o _supcat.so

g++ supcat.cpp -l HCSegDll -L . -o test
