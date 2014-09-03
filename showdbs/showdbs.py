# !/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web
import tornado.options
import tornado.httpserver
import tornado.ioloop

import pymongo

from tornado.options import define, options
define("tina", default=8016, help="run in showdb.", type=int)


########################################################################
class Application(tornado.web.Application):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        print "i am application"
        handlers = [(r"/", ShowHander)]
        conn = pymongo.MongoClient("localhost", 27017)
        self.db = conn["mydbs"]
        tornado.web.Application.__init__(self, handlers)
        
        
########################################################################
class ShowHander(tornado.web.RequestHandler):
    """"""

    #----------------------------------------------------------------------
    def get(self):
        """"""
        print "i am SHowder"
        coll = self.application.db.iplist
        ips = coll.find().limit(10)
        for i in range(0, 10):
            current_cusor = ips[i]
            del current_cusor["_id"]
            self.write(current_cusor)


if __name__ == "__main__":
    print "i am first."
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.tina)
    tornado.ioloop.IOLoop.instance().start()