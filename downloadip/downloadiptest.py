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


def deco(func):
    def _deco(*args, **kwargs):
        start_time = time.time()
        ret = func(*args, **kwargs)
        end_time = time.time()
        process_time = end_time - start_time
        print '%s\t: %.3f ' % (func.func_name, process_time)
        return ret
    return _deco


@deco
def connect_to_db():
    try:
        conn = MongoClient(host="localhost", port=27017)
    except ConnectionFailure, e:
        sys.stderr.write("Could not connect to MongoDB: %s" % e)
        sys.exit(1)
    dbh = conn["mydbs"]
    return dbh


import time


@deco
def my_urlopen(url_item):
    return urllib2.urlopen(url_item)

@deco
def download_item():
    """ """
    global COUNT
    my_dbh = connect_to_db()
    my_dbh.acceptive.update({"_id": "status"}, {"$set": {"accpeted_status": 0}}, safe=True)
    print conn.iplist.count()
    conn.iplist.remove()

    for i in range(1, 11):
        url_item = url + "/%d" % i
        print "get the %d page" % i
        content = my_urlopen(url_item)
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
        print "----------Finish getting the %d page--------------" % i
        print "the db status:"
        print my_dbh.acceptive.find_one({"_id": "status"})["accpeted_status"]
    print "3333333333333333333333333"
    print my_dbh.acceptive.find_one({"_id": "status"})["accpeted_status"]
    my_dbh.acceptive.update({"_id": "status"}, {"$set": {"accpeted_status": 1}}, safe=True)
    print my_dbh.acceptive.find_one({"_id": "status"})["accpeted_status"]
    print "444444444444444444"


if __name__ == "__main__":
    try:
        conn = connect_to_db()
        print conn.iplist.count()
    except ConnectionFailure, e:
        sys.stderr.write("Could not connect to MongoDB: %s" % e)
        sys.exit(1)

    scheduler = BlockingScheduler()
    scheduler.add_job(download_item, "cron", second=1)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
