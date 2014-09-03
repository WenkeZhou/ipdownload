#!/usr/bin/evn python
#-*- coding: utf-8 -*-

import time
from apscheduler.schedulers.blocking import BlockingScheduler
import urllib2
import sys
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

url = "http://www.xici.net.co/nn"
COUNT = 0


def connect_to_db():
    dbh = 0
    try:
        conn = MongoClient(host="localhost", port=27017)
    except ConnectionFailure, e:
        sys.stderr.write("Could not connect to MongoDB: %s" % e)
        sys.exit(1)
    dbh = conn["mydbs"]
    return dbh


def download_item():
    my_dbh = connect_to_db()
    global COUNT

    if my_dbh != 0:
        print "Return is corret!"
    else:
        print "There is something wrong with dbh!!"

    for i in range(1, 11):
        url_item = url + "/%d" % i
        print "get the %d page" % i
        content = urllib2.urlopen(url_item)
        html = content.read()
        soup = BeautifulSoup(html)

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
            my_dbh.iplist.insert({
                "http_type": http_type,
                "ip": ip,
                "port": port,
                "link_speed": link_speed,
                "link_time": link_time,
                "created_time": created_time,
                "created_count": COUNT
            }, safe=True)
        print "There are %d items now!" % (my_dbh.iplist.count())
        print "Finish getting the %d page" % i


if __name__ == "__main__":
    download_item()
    try:
        conn = connect_to_db()
    except ConnectionFailure, e:
        sys.stderr.write("Could not connect to MongoDB: %s" % e)
        sys.exit(1)
    result = conn
    cursor = result.iplist.find()
    cursor.count()
    for item in cursor:
        print item
    # while cursor.hasNext():
    #     obj = cursor
    #     print "http_type:%s, ip:%s,  port:%s, current_count:%d" % (obj["http_type"], obj["ip"], obj["port"],
    #                                                                obj["current_count"])
    #     obj = cursor.next()
    # scheduler = BlockingScheduler()
    # scheduler.add_job(download_item, "interval", seconds=20)
    # try:
    #     scheduler.start()
    # except (KeyboardInterrupt, SystemExit):
    #     pass