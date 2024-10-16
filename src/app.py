import sys
sys.setrecursionlimit(4096)

import web
from gevent.pywsgi import WSGIServer

import m3u
import url

class skip:
    def GET(self):
        return

class m3u_entry:
    def GET(self, config_name):
        if not config_name:
            config_name = 'default'
        web.header('content-type', 'text/plain; charset=utf-8')
        return m3u.process(config_name)

class url_entry:
    def HEAD(*_):
        return web.notfound()
    def GET(self, platform, roomid):
        u = url.process(platform, roomid) 
        if not u:
            return web.notfound()
        return web.seeother(u)

urls = (
    '/favicon.ico', 'skip',
    '/([^/]*)', 'm3u_entry',
    '/([^/]+)/([^/]+)', 'url_entry',
)

app = web.application(urls, globals())
if __name__ == "__main__":
    print('http://0.0.0.0:3658/')
    WSGIServer(('0.0.0.0', 3658), app.wsgifunc()).serve_forever()