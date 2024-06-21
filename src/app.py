import gevent
gevent.get_hub()
from gevent import monkey
monkey.patch_all()

import web

class skip:
    def GET(self):
        return

class process:
    def GET(self, config_name):
        if not config_name:
            config_name = 'default'
        local = {'web': web, 'config_name': config_name}
        with open('process.py') as f:
            exec(f.read(), local)
        return local['res_body']

urls = (
    '/favicon.ico', 'skip',
    '/(.*)', 'process',
)

app = web.application(urls, globals())
if __name__ == "__main__":
    app.run() # port: 3658