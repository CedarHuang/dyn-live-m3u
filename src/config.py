import grequests
import threading
import tomllib
import re

from utils import check

config = threading.local()

def init(config_name):
    with open('../config/%s.toml' % config_name, 'rb') as f:
        toml = tomllib.load(f)

    check(toml, 'proxies', {})
    check(toml['proxies'], 'http', '')
    check(toml['proxies'], 'https', '')
    check(toml, 'url', {})
    check(toml['url'], 'option', {})
    check(toml, 'status', {})
    check(toml['status'], 'closed', '')
    check(toml['status'], 'live', '')
    check(toml['status'], 'loop', '')
    check(toml['status'], 'blocked', '')
    check(toml['status'], 'exception', '')
    check(toml['status'], 'timeout', '')
    check(toml, 're', {})
    check(toml['re'], 'name', [])
    check(toml['re'], 'group', [])
    check(toml, 'include', {})
    check(toml['include'], 'm3u', {})
    check(toml['include']['m3u'], 'remote', [])
    check(toml['include']['m3u'], 'local', [])
    check(toml['include'], 'toml', {})
    check(toml['include']['toml'], 'remote', [])
    check(toml['include']['toml'], 'local', [])
    check(toml, 'channel', [])

    r = grequests.map([grequests.get(url) for url in toml['include']['m3u']['remote']])
    includes = [i.text for i in r]
    for i in toml['include']['m3u']['local']:
        with open('../config/%s' % i) as f:
            includes.append(f.read())
    for i in includes:
        for j in i.splitlines():
            info = re.search(r'^https?://[^/]+/([^/]+)/([^/]+)$', j)
            if info is not None:
                toml['channel'].append({
                    'platform': info.group(1),
                    'roomid': info.group(2),
                })

    r = grequests.map([grequests.get(url) for url in toml['include']['toml']['remote']])
    includes = [i.text for i in r]
    for i in toml['include']['toml']['local']:
        with open('../config/%s' % i) as f:
            includes.append(f.read())
    for i in includes:
        include = tomllib.loads(i)
        check(include, 'channel', [])
        toml['channel'].extend(include['channel'])

    config.headers = {
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1'
    }

    config.time_limit = 5
    config.retry_time_limit = 3

    config.toml = toml
    config.proxies = toml['proxies']
    config.request_params = {
        'headers': config.headers,
        'proxies': config.proxies,
        'timeout': config.time_limit,
    }

    config.CLOSED = toml['status']['closed']
    config.LIVE = toml['status']['live']
    config.LOOP = toml['status']['loop']
    config.BLOCKED = toml['status']['blocked']
    config.EXCEPTION = toml['status']['exception']
    config.TIMEOUT = toml['status']['timeout']