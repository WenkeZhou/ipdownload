# !/use/bin/env python
# -*- coding: utf-8 -*-

import threading
import Queue
import socket
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import urllib2
import time

target_url = "http://tieba.baidu.com/f?kw=%D5%C5%B9%FA%C8%D9"
socket.setdefaulttimeout(20)
NUM = 0


def connection_db():
    try:
        conn = MongoClient(host="localhost", port=27017)
    except ConnectionFailure, e:
        sys.stderr.write("Could not connect to MongoDB: %s" % e)
        sys.exit(1)
    dbh = conn["mydbs"]
    return dbh


def checkip(target_job, dbh):
    # dbh = connection_db()
    # test = dbh.iplist.find_one()
    http_type = target_job["http_type"]
    ip = target_job["ip"]
    ip_id = target_job["_id"]

    proxy = {http_type: ip}
    proxy_support = urllib2.ProxyHandler(proxy)
    opener = urllib2.build_opener(proxy_support)
    opener.addheaders.append(
         ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.48')
    )

    totaltime = 0
    flag = 1

    for i in range(10):
        try:
            start_open_time = time.time()
            content = opener.open(target_url)
            status = content.getcode()
            end_open_time = time.time()
            used_open_time = end_open_time - start_open_time
            totaltime += used_open_time
            # print "It's the %d time. status = %d, current_time = %f, total_time = %f" % (
            #     i, status, used_open_time, totaltime
            # )
        except urllib2.URLError, e:
            print "urllib2.URLError"
            flag = 0
        except socket.error, e:
            print "socket.error"
            flag = 0

    if flag == 0:
        totaltime = -1
    else:
        totaltime /= 10

    dbh.iplist.update({"_id": ip_id}, {"$set": {"connect_time": totaltime}})
    print totaltime


def create_threads(concurrency, jobs, results, dbh):
    for i in range(concurrency):
        print "I am %d, i was created." % i
        thread = threading.Thread(target=work, args=[concurrency, jobs, results, dbh])
        thread.daemon = True
        thread.start()


def work(concurrency, jobs, results, dbh):
    global NUM
    while True:
        try:
            target_job = jobs.get()
            NUM += 1
            print target_job
            print "It's (%d) job--->" % NUM + str(threading.current_thread())

            checkip(target_job, dbh)

        finally:
            jobs.task_done()


def add_jobs(job_count, jobs, results):
    for i in range(job_count):
        jobs.put(results[i])
    print "I have added %d jobs" % job_count
    return job_count


def process(todo, jobs, results, concurrency):
    canceled = False
    try:
        jobs.join()
    except KeyboardInterrupt:
        canceled = True
    if canceled:
        done = results.qsize()
    else:
        print "keep going"


def test():
    concurrency = 16
    dbh = connection_db()
    db_result = dbh.iplist.find({"connect_time": {"$exists": False}})
    job_count = db_result.count()
    print "there are %d items in the db." % db_result.count()
    jobs = Queue.Queue()
    results = Queue.Queue()
    create_threads(concurrency, jobs, results, dbh)
    todo = add_jobs(job_count, jobs, db_result)
    process(todo, jobs, results, concurrency)

if __name__ == "__main__":
    main_begin_time = time.time()
    test()
    main_end_time = time.time()
    main_used_time = main_end_time - main_begin_time
    print "________________________________________________"
    print "Over time %f" % main_used_time


# def main():
#     main_begin_time = time.time()
#     test()
#     main_end_time = time.time()
#     main_used_time = main_end_time - main_begin_time
#     print "________________________________________________"
#     print "Over time %f" % main_used_time