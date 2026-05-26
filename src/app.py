import json
import os

import bottle
from gevent import monkey
monkey.patch_all()

import api
import m3u
import url

app = bottle.Bottle()


@app.route('/favicon.ico')
def skip():
    return None


# --- API ---

@app.route('/api/_')
def api_configs():
    bottle.response.content_type = 'application/json'
    return json.dumps(api.list_configs(), ensure_ascii=False)


@app.route('/api/<config>')
def api_list(config):
    bottle.response.content_type = 'application/json'
    return json.dumps(api.list_channels(config), ensure_ascii=False)


@app.route('/api/<config>', method='POST')
def api_add(config):
    return json.dumps(api.add_channel(config, bottle.request.json), ensure_ascii=False)


@app.route('/api/<config>/<index:int>', method='PUT')
def api_update(config, index):
    return json.dumps(api.update_channel(config, index, bottle.request.json), ensure_ascii=False)


@app.route('/api/<config>/<index:int>', method='DELETE')
def api_delete(config, index):
    return json.dumps(api.delete_channel(config, index), ensure_ascii=False)


@app.route('/api/<config>/move', method='POST')
def api_move(config):
    body = bottle.request.json
    return json.dumps(api.move_channel(config, body['from'], body['to']), ensure_ascii=False)


@app.route('/api/<config>/cookie', method='POST')
def api_cookie(config):
    if config != 'default':
        bottle.abort(400, 'cookie sync only supported for default config')
    body = bottle.request.json
    return json.dumps(api.set_platform_option(config, body['platform'], 'http-cookies', body['cookies']), ensure_ascii=False)


# --- pages ---

@app.route('/')
def manage_page():
    return bottle.static_file('manage.html', root=os.path.join(os.path.dirname(__file__), 'static'))


@app.route('/<config>')
def m3u_entry(config='default'):
    bottle.response.content_type = 'text/plain; charset=utf-8'
    return m3u.process(config)


@app.route('/<platform>/<roomid>')
def url_entry(platform, roomid):
    if bottle.request.method == 'HEAD':
        bottle.abort(404)
    res = url.process(platform, roomid)
    if not res:
        bottle.abort(404)
    bottle.redirect(res)


if __name__ == '__main__':
    bottle.run(app, host='0.0.0.0', port=3658, server='gevent')
