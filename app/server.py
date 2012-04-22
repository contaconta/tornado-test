# -*- coding: utf-8 -*-

'''
    User: ogata
    Date: 4/22/12
    Time: 4:32 PM
'''
__author__ = 'ogata'

import tornado.ioloop
import tornado.web
import tornado.escape

import os

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

import logging


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/image', ImageTestHandler),
            (r'/test/([A-Za-z0-9]+)', RequestTestHandler),
            (r'/login', AuthLoginHandler),
            (r'/logout', AuthLogoutHandler),
        ]
        settings = dict(
            cookie_secret='43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=fas',
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            login_url="/login",
            autoescape="xhtml_escape",
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user = self.get_secure_cookie("user")
        logging.debug('BaseHandler - user: %s' % user)
        if not user: return None
        return tornado.escape.utf8(user)

class AuthLoginHandler(BaseHandler):

    def get(self):
        message = self.render_string("login.html")
        self.write(message)

    def post(self):

        user = self.get_argument("user")
        password = self.get_argument("password")

        logging.debug('AuthLoginHandler:post %s %s' % (user, password))

        if user == 'test' and password == 'a':
            self.set_secure_cookie("user", tornado.escape.utf8(user))
            self.redirect("/")
        else:
            self.write_error(403)

class AuthLogoutHandler(BaseHandler):

    def initialize(self):
        logging.debug('AuthLogoutHandler - initialize')

    def get(self):
        self.clear_cookie("user")
        self.redirect('/')

    def prepare(self):
        logging.debug('AuthLogoutHandler - prepare()')

    def on_finish(self):
        logging.debug('AuthLogoutHandler - on_finish()')

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write('hello!<br><a href="/logout">Logout</a>')

class ImageTestHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        logging.debug('ImageTestHander')
        with open('noimage.jpg','rb') as img:
            self.set_header('Content-Type', 'Image')
            data = img.read()
            self.write(data)


class RequestTestHandler(tornado.web.RequestHandler):
    def get(self, story_id):
        logging.debug('story id'+story_id)
        self.write('id:'+story_id)


def main():
    tornado.options.parse_config_file(os.path.join(os.path.dirname(__file__), 'server.conf'))
    tornado.options.parse_command_line()
    app = Application()
    logging.debug('run on port %d in %s mode' % (options.port, options.logging))
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
