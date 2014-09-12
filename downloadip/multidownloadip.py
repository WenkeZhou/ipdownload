#!/usr/bin/evn python
#-*- coding: utf-8 -*-

import bdcheckip
from bs4 import BeautifulSoup
import urllib2
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import threading
import Queue
import time
from apscheduler.schedulers.blocking import BlockingScheduler

COUNT = 0
url = "http://www.xici.net.co/nn"

def connect_to_db():
    try:
        conn = MongoClient(host="localhost", port=27017)
    except ConnectionFailure, e:
        sys.stderr.write("Could not connect to MongoDB: %s" % e)
        sys.exit(1)
    dbh = conn["mydbs"]
    return dbh


def create_thread(jobs_num, jobs, concurrency, dbh):
    for i in range(concurrency):
        thread = threading.Thread(target=work, args=[jobs_num, jobs, dbh])
        print "I have created %d thread." % i
        thread.daemon = True
        thread.start()


def my_urlopen(url_item):
    return urllib2.urlopen(url_item)


def work(jobs_num, jobs, dbh):
    while True:
        try:
            global COUNT
            page_num = jobs.get()

            url_item = url + "/%d" % page_num
            # print "get the %d page" % page_num
            print url_item
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
            print "----------Finish getting the %d page--------------" % page_num

        finally:
            jobs.task_done()


def add_jobs(jobs_num, jobs, result):
    for i in range(1, jobs_num+1):
        jobs.put(i)
    print "I have added %d jobs" % jobs_num
    return jobs_num


def process(todo, jobs_num, jobs, results, dbh):
    canceled = False
    try:
        dbh.acceptive.update({"_id": "status"}, {"$set": {"accpeted_status": 0}}, safe=True)
        print dbh.iplist.count()
        dbh.iplist.remove()
        jobs.join()
    except KeyboardInterrupt:
        canceled = True
    if canceled:
        done = results.qsize()

    else:
        dbh.acceptive.update({"_id": "status"}, {"$set": {"accpeted_status": 1}}, safe=True)
        print "keep going"


def multidownloadip():

    main_begin_time = time.time()

    dbh = connect_to_db()
    jobs_num = page_num = 11
    concurrency = 5
    jobs = Queue.Queue()
    results = Queue.Queue()
    create_thread(jobs_num, jobs, concurrency, dbh)
    todo = add_jobs(jobs_num, jobs, results)
    process(todo, jobs_num, jobs, results, dbh)

    main_end_time = time.time()
    main_used_time = main_end_time - main_begin_time
    print "________________________________________________"
    print "Over time %f" % main_used_time
    bdcheckip.main()

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(multidownloadip, "cron", second=1)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
