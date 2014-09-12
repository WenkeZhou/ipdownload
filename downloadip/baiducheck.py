# !/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
# import iplisttxt
import socket
socket.setdefaulttimeout(10)
import aaa
import bbb
COUNT = 0


def url_user_agent():
    #设置使用代理
    # proxy = {'http': '140.206.86.68:8080'}
    global COUNT
    good_ip_list = {}
    print "there are total %d in list." % len(bbb.testb)
    for i in range(len(bbb.testb)):
        proxy = {'http': bbb.testb[i]}
        proxy_support = urllib2.ProxyHandler(proxy)
        opener = urllib2.build_opener(proxy_support)
        opener.addheaders.append(
            ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.48')
        )

        try:
            content = opener.open(url1)
            print content.getcode()
            print_good(i, bbb.testb[i])
            good_ip_list[i] = bbb.testb[i]
        except urllib2.URLError, e:
            print "####"
            print_error(i, bbb.testb[i])
        except socket.error, e:
            print "!!!!"
            print_error(i, bbb.testb[i])

    print good_ip_list


def write(i, ip):
    aaa.testa.append({ip: i})
    aaa.count += 1


def print_error(i, ip):
    global COUNT
    COUNT += 1
    write(i, ip)
    print "aaa len is %d " % len(aaa.testa)
    print "the No.%d ip is bad --->" % i + ip
    print "there are %d ips is bad" % COUNT


def print_good(i, ip):
    global COUNT
    COUNT += 1
    print "the No.%d ip is good --->" % i + ip
    print "there are %d ips is good" % COUNT


def connect_db():
    try:
        conn = MongoClient(host="localhost", port=27017)
    except ConnectionFailure, e:
        sys.stderr.write("Could not connect to MongoDB: %s" % e)
        sys.exit(1)
    dbh = conn["mydbs"]



url = 'http://www.dianping.com/search/category/2/10/g311'
url1 = 'http://www.douguo.com/'
# doc = url_user_agent(url1)
# print doc

if __name__ == "__main__":
    url_user_agent()