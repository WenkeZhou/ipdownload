# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import tornado.web
import tornado.options
import tornado.httpserver
import tornado.ioloop

import math
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
            ui_modules={"IpList": IpListModule, "PagePart": PagePartModule},
            debug=True,
        )
        conn = pymongo.MongoClient("localhost", 27017)
        self.db = conn["mydbs"]
        tornado.web.Application.__init__(self, handlers, **settings)


class ShowHandler(tornado.web.RequestHandler):
    """"""   
    def get(self):
        coll = self.application.db.iplist
        total_num = coll.find().count()
        current_page = int(self.get_argument("current_page", 1))
        page_items_num = int(self.get_argument("page_item_num", 10))
        page_num = int(math.ceil(total_num/page_items_num)) if total_num > 0 else 0
        print "i am showhandler222"
        iplist = coll.find().skip((current_page-1)*page_items_num).limit(10)
        self.write("hello sb")
        self.render(
            "templates/ip_list.html",
            page_number="11111",
            iplist=iplist,
            page_num=page_num,
            current_page=current_page,
            total_num=total_num,
            page_items_num=page_items_num,
        )


class IpListModule(tornado.web.UIModule):
    def render(self, ip):
        print "i am IpListModule"
        return self.render_string(
            "templates/modules/single_ip.html",
            ip=ip,
        )


class PagePartModule(tornado.web.UIModule):
    def render(self, page_num, current_page, total_num, page_items_num):
        # page_num, current_page, total_num, page_items_num
        # current_page, total_num, page_num, page_items_num
        _htmls = []
        if page_num <= 1:
            return '<a class="disable">1</a>'
        if current_page == 1:
            _htmls.append('<a class="disable">首页</a>')
            _htmls.append('<a class="disable">&larr;上一页</a>')
        else:
            _htmls.append('<a href="?current_page=%d&page_items_num=%d">首页</a>' % (1, page_items_num))
            _htmls.append('<a href="?current_page=%d&page_items_num=%d">&larr;上一页</a>' % (current_page-1, page_items_num))

        if page_num <= 12:
            for i in range(1, page_num):
                if i == current_page:
                    _htmls.append('<a class="current_page_status">%d</a>' % current_page)
                else:
                    _htmls.append('<a href="?current_page=%d&page_items_num=%d">%d</a>' % (i, page_items_num, i))
        elif page_num >= 13:
            if current_page <= 8:
                for i in range(1, 9):
                    if i == current_page:
                        _htmls.append('<a class="current_page_status">%d</a>' % i)
                    else:
                        _htmls.append('<a href="?current_page=%d&page_items_num=%d">%d</a>' % (i, page_items_num, i))
                _htmls.append('<a>...</a>')
                for i in range(page_num-2, page_num+1):
                    _htmls.append('<a href="?current_page=%d&page_items_num=%d">%d</a>' % (i, page_items_num, i))
            elif (current_page >= 9) & (current_page < page_num - 7):
                for i in range(1, 4):
                    _htmls.append('<a href="?current_page=%d&page_items_num=%d">%d</a>' % (i, page_items_num, i))
                _htmls.append('<a>...</a>')
                for i in range(current_page-2, current_page+3):
                    if i == current_page:
                        _htmls.append('<a class="current_page_status">%d</a>' % current_page)
                    else:
                        _htmls.append('<a href="?current_page=%d&page_items_num=%d">%d</a>' % (i, page_items_num, i))
                _htmls.append('<a>...</a>')
                for i in range(page_num-2, page_num+1):
                    _htmls.append('<a href="?current_page=%d&page_items_num=%d">%d</a>' % (i, page_items_num, i))
            elif (current_page >= page_num -7) & (current_page <= page_num):
                for i in range(1, 4):
                    _htmls.append('<a href="?current_page=%d&page_items_num=%d">%d</a>' % (i, page_items_num, i))
                _htmls.append('<a>...</a>')
                for i in range(page_num - 7, page_num + 1):
                    if i == current_page:
                        _htmls.append('<a class="current_page_status">%d</a>' % current_page)
                    else:
                        _htmls.append('<a href="?current_page=%d&page_items_num=%d">%d</a>' % (i, page_items_num, i))

        if current_page == page_num:
            _htmls.append('<a class="disable">末页</a>')
            _htmls.append('<a class="disable">&rarr;下一页</a>')
        else:
            _htmls.append('<a href="?current_page=%d&page_items_num=%d">末页</a>' % (page_num, page_items_num))
            _htmls.append('<a href="?current_page=%d&page_items_num=%d">&rarr;下一页</a>' % (current_page+1, page_items_num))

        return '\r\n'.join(_htmls)

if __name__ == "__main__":
    print "I'am first."
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()