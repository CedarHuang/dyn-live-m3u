import grequests
import json
import re
import sys
import tomllib

sys.setrecursionlimit(4096)

toml = {}
with open('../config/%s.toml' % config_name, 'rb') as f:
    toml = tomllib.load(f)

def check(dict, key, value):
    if key not in dict:
        dict[key] = value
check(toml, 'status', {})
check(toml['status'], 'closed', '')
check(toml['status'], 'live', '')
check(toml['status'], 'blocked', '')
check(toml['status'], 'exception', '')
check(toml, 're', {})
check(toml['re'], 'name', [])
check(toml['re'], 'group', [])
check(toml, 'include', {})
check(toml['include'], 'm3u', {})
check(toml['include']['m3u'], 'remote', [])
check(toml['include']['m3u'], 'local', [])

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

CLOSED = toml['status']['closed']
LIVE = toml['status']['live']
BLOCKED = toml['status']['blocked']
EXCEPTION = toml['status']['exception']

headers = {
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1'
}

retry_deepth_max = 2
retry_deepth = 0

class channel:
    def gen(info):
        try:
            simple = info['simple'].split(':')
            info['platform'] = simple[0]
            info['roomid'] = simple[1]
        except:
            pass
        try:
            return eval(info['platform'] + '(info)')
        except:
            return exception(info)
    def __init__(self, info):
        self.i = info
    def proc_res(self, response):
        global retry_deepth
        # self.proc_res_impl(response)
        try:
            self.proc_res_impl(response)
        except:
            if retry_deepth < retry_deepth_max:
                retry_deepth += 1
                response = grequests.map([grequests.get(response.url, headers=headers)])[0]
                channel.gen(self.__dict__['i']).proc_res(response)
            else:
                exception(self.__dict__['i']).proc_res_impl(response)
        retry_deepth = 0
    def gen_m3u_item(self, toml):
        for key in toml['re']:
            for re_item in toml['re'][key]:
                try:
                    self.i[key] = eval('re.sub(%s, self.i[key])' % re_item)
                except:
                    pass
        self.i['name'] = toml['format']['name'].format(**self.i)
        self.i['group'] = toml['format']['group'].format(**self.i)
        for key in ['name', 'group']:
            for re_item in toml['re'][key]:
                try:
                    self.i[key] = eval('re.sub(%s, self.i[key])' % re_item)
                except:
                    pass
        res = '#EXTINF:-1 tvg-logo="%s" group-title="%s",%s\n' % (self.i['logo'], self.i['group'], self.i['name'])
        res += toml['format']['url'].get(self.i['platform'], toml['format']['url']['default']).format(**self.i) + '\n'
        return res

class exception(channel):
    def gen_req(self):
        return grequests.get('')
    def proc_res_impl(self, response):
        check(self.i, 'nick', self.i['roomid'])
        check(self.i, 'title', self.i['platform'] + ':' + self.i['nick'])
        check(self.i, 'area', self.i['platform'])
        check(self.i, 'logo', '')
        check(self.i, 'status', EXCEPTION)

class douyu(channel):
    def gen_req(self):
        return grequests.get('https://m.douyu.com/' + self.i['roomid'], headers=headers)
    def proc_res_impl(self, response):
        info = json.loads(re.search(r'<script id="vite-plugin-ssr_pageContext" type="application/json">(.*)</script>', response.text).group(1))
        info = info['pageContext']['pageProps']['room']['roomInfo']['roomInfo']
        self.i['nick'] = info['nickname']
        self.i['title'] = info['roomName']
        self.i['area'] = info['cate2Name']
        self.i['logo'] = info['avatar']
        self.i['status'] = LIVE if info['isLive'] == 1 else CLOSED

class huya(channel):
    def gen_req(self):
        return grequests.get('https://m.huya.com/' + self.i['roomid'], headers=headers)
    def proc_res_impl(self, response):
        info = json.loads(re.search(r'<script> window.HNF_GLOBAL_INIT = (.*) </script>', response.text).group(1))
        info = info['roomInfo']['tLiveInfo'] if info['roomInfo']['eLiveStatus'] != 1 else info['roomInfo']['tRecentLive']
        self.i['nick'] = info['sNick']
        self.i['title'] = info['sIntroduction']
        self.i['area'] = info['sGameFullName']
        self.i['logo'] = info['sAvatar180']
        self.i['status'] = LIVE if info['_classname'] == 'LiveRoom.LiveInfo' else CLOSED

class bilibili(channel):
    def gen_req(self):
        return grequests.get('https://api.live.bilibili.com/xlive/web-room/v1/index/getH5InfoByRoom?room_id=' + self.i['roomid'], headers=headers)
    def proc_res_impl(self, response):
        info = json.loads(response.text)
        info = info['data']
        self.i['nick'] = info['anchor_info']['base_info']['uname']
        self.i['title'] = info['room_info']['title']
        self.i['area'] = info['room_info']['area_name']
        self.i['logo'] = info['anchor_info']['base_info']['face']
        self.i['status'] = LIVE if info['room_info']['live_status'] == 1 else CLOSED
        self.i['status'] = BLOCKED if info['block_info']['block'] == True else self.i['status']

web.header('content-type', 'text/plain; charset=utf-8')
res_body = '#EXTM3U\n'
channels = [channel.gen(i) for i in toml['channel']]
responses = grequests.map([i.gen_req() for i in channels])
[channel.proc_res(response) for (channel, response) in list(zip(channels, responses))]
res_body += ''.join([channel.gen_m3u_item(toml) for channel in channels])