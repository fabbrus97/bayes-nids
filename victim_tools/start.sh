#!/bin/ash


telnetd #-l /bin/ash

mkdir -p /var/log/lighttpd/
lighttpd -D -f /opt/lighttpd/lighttpd.conf
