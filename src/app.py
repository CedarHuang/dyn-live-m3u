import sys
sys.setrecursionlimit(4096)

import bottle
from gevent import monkey
monkey.patch_all()

import m3u
import url

app = bottle.Bottle()

@app.route('/favicon.ico')
def skip():
    return None

@app.route('/')
@app.route('/<config_name>')
def m3u_entry(config_name='default'):
    bottle.response.content_type = 'text/plain; charset=utf-8'
    return m3u.process(config_name)

@app.route('/<platform>/<roomid>')
def url_entry(platform, roomid):
    if bottle.request.method == 'HEAD':
        bottle.abort(404)
    res = url.process(platform, roomid)
    if not res:
        bottle.abort(404)
    bottle.redirect(res)

if __name__ == "__main__":
    bottle.run(app, host='0.0.0.0', port=3658, server='gevent')