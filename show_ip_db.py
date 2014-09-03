# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import tornado.web
import tornado.options
import tornado.httpserver
import tornado.ioloop

import pymongo

from tornado.options import define, options
define("port", default=8022, help="run in showdb.", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        print "i am application"
        handlers = [(r"/", ShowHandler)]
        settings = dict(
            templates_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={"IpList": IpListModule},
            debug=True,
        )
        conn = pymongo.MongoClient("localhost", 27017)
        self.db = conn["mydbs"]
        tornado.web.Application.__init__(self, handlers, **settings)


class ShowHandler(tornado.web.RequestHandler):
    """"""   
    def get(self):
        self.write("i am showhandler")
        print "i am showhandler222"
        coll = self.application.db.iplist
        iplist = coll.find().limit(10)        
        self.write("hello sb")
        self.render(
            "templates/ip_list.html",
            page_number="11111",
            iplist=iplist
        )


class IpListModule(tornado.web.UIModule):
    def render(self, ip):
        print "i am IpListModule"
        return self.render_string(
            "templates/modules/single_ip.html",
            ip=ip,
        )

if __name__ == "__main__":
    print "I'am first."
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()