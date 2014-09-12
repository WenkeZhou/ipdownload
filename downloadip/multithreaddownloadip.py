# !/user/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import random
from iplisttxt import proxyiplist
from agentheadertxt import proxyheaderlist
import urllib2
import socket
from bs4 import BeautifulSoup
import badproxyiplist
import badproxyheaderlist
import iplisttxt
import agentheadertxt
import time

url = "http://www.xici.net.co/nn"
socket.setdefaulttimeout(10)
COUNT = 0


def connection_db():
    try:
        conn = MongoClient(host="localhost", port=27017)
    except ConnectionFailure, e:
        sys.stderr.write("Could not connect to MongoDB: %s" % e)
        sys.exit(1)
    dbh = conn["mydbs"]
    return dbh


def download_items(page, proxy_ip, proxy_header):
    pass


def proxy_ip_header_agent(target_url, proxy_ip, proxy_header):
    #设置使用代理ip, 和伪装头部
    status = 1
    # proxy = {'http': '140.206.86.68:8080'}
    proxy = {'http': proxy_ip}
    proxy_support = urllib2.ProxyHandler(proxy)
    opener = urllib2.build_opener(proxy_support)
    opener.addheaders.append(
        ('User-Agent', proxy_header)
    )

    try:
        content = opener.open(target_url)
        print "aa"
    except Exception, e:
        # delete_proxy_item(proxy_ip, iplisttxt.proxyiplist, badproxyiplist.badproxyiplist)
        if proxy_ip not in badproxyiplist.badproxyiplist:
            badproxyiplist.badproxyiplist.append(proxy_ip)

        if proxy_ip in iplisttxt.proxyiplist:
            iplisttxt.proxyiplist.remove(proxy_ip)
        status = 0  # this ip is bad, reload ip and proxy_header
        content = ""

    if status != 0:
        if content.getcode() not in [200, 201, 202, 203, 204, 205, 206]:
            delete_proxy_item(proxy_ip, iplisttxt.proxyiplist, badproxyiplist.badproxyiplist)
            status = -2  # there is something wrong in the web. solve this in future.

    if len(proxyiplist) <= 0:
        print "proxyiplist is empty!!!!!!-----> a fital error."
        status = -1  # proxyiplist is empty!!!!!!-----> a fital error. It's a bad smell.

    return status, content


def do_job(page, proxy_ip, proxy_header, dbh):
    target_url = url + "/%d" % page
    print "this is %d page!!!" % page
    status, content = proxy_ip_header_agent(target_url, proxy_ip, proxy_header)

    while status in [0, -2]:
        print "down the do_job web."
        proxy_ip, proxy_header = pickup_ip_header()
        status, content = proxy_ip_header_agent(target_url, proxy_ip, proxy_header)

    while status == -1:
        print "proxyiplist is empty!!!!!!-----> a fital error."
    if content is not None:
        html = content.read()
        soup = BeautifulSoup(html)
        analyse_soup(soup, dbh, page)


def analyse_soup(soup, dbh, page):
    global COUNT
    table = soup.find("table", {"id": "ip_list"})
    trs = table.findAll("tr")

    for tr in trs[1:]:
        tds = tr.findAll("td")
        ip = tds[1].string
        port = tds[2].string
        http_type = tds[5].string
        times = tr.findAll("div", {"class": "bar"})
        link_speed = float(times[0].attrs['title'][:-1])
        link_time = float(times[1].attrs['title'][:-1])
        created_time = time.time()
        COUNT += 1
        dbh.iplist.insert({
            "http_type": http_type,
            "ip": ip,
            "port": port,
            "link_speed": link_speed,
            "link_time": link_time,
            "created_time": created_time,
            "created_count": COUNT
        }, safe=True)
    print "There are %d items now!" % (dbh.iplist.count())
    print "----------Finish getting the %d page--------------" % page


# def delete_proxy_item(proxyitem, proxylist, badproxylist):
#     if proxyitem not in badproxyiplist:
#         badproxylist.append(proxyitem)
#
#     if proxyitem in proxylist:
        # proxylist.remove(porxyitem)


def pickup_ip_header():
    proxy_ip = create_ip_header(iplisttxt.proxyiplist, badproxyiplist.badproxyiplist)
    proxy_header = create_ip_header(agentheadertxt.proxyheaderlist, badproxyheaderlist.badproxyheaderlist)
    return proxy_ip, proxy_header


def create_ip_header(source_proxy_list, bad_proxy_list):
    """
    选取ip, proxy_header 质量比较高的, 将坏ip, proxy_header存入一个list队列中， 等待删除
    """
    proxy_target_item = random.choice(source_proxy_list)
    if proxy_target_item in bad_proxy_list:
        try:
            source_proxy_list.remove(proxy_target_item)
        except ValueError:
            print "this bad ip have been removed some thread else."
            proxy_target_item = check_ip_header(source_proxy_list, bad_proxy_list)
        finally:
            if len(source_proxy_list) <= 0:
                print "proxyiplist is empty!!!!!!-----> a fital error."

    return proxy_target_item


def main():
    dbh = connection_db()
    for i in range(1, 11):
        proxy_ip, proxy_header = pickup_ip_header()
        do_job(i, proxy_ip, proxy_header, dbh)


if __name__ == '__main__':
    main()



