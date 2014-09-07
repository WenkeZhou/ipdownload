# !/usr/bin/env python
# -*- coding: utf-8 -*-

from apscheduler.schedulers.blocking import BlockingScheduler

COUNT = 0
from datetime import datetime
def trick():
    global COUNT
    COUNT += 1
    print "hello, hero.---->%s" % datetime.now()

if __name__ == "__main__":
    sched = BlockingScheduler()
    sched.add_job(trick, 'cron', id="my_job_id", second='5,15')

    try:
        sched.start()
    except KeyboardInterrupt, SystemExit:
        pass

