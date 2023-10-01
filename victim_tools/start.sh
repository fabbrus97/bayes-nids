#!/bin/ash


telnetd #-l /bin/ash

mkdir -p /var/log/lighttpd/
mkdir -p /opt/lighttpd
mkdir -p /var/www
mkdir -p /var/ssl

cp -r /lighttpd/config/lighttpd.conf /opt/lighttpd
cp -r /lighttpd/www/* /var/www/
cp -r /lighttpd/ssl/* /var/ssl/

lighttpd -D -f /opt/lighttpd/lighttpd.conf
