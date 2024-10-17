import grequests
import json
import re
import streamlink

from config import config
from platforms.channel import channel

# 已失效

class twitch(channel):
    def gen_req(self):
        return grequests.get('https://m.twitch.tv/' + self.i['roomid'], **config.request_params)
    def proc_res_impl(self, response):
        info = json.loads(re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*)</script>', response.text).group(1))
        info = info['props']['relayQueryRecords']
        key = info['client:root']['user(login:\"%s\")' % self.i['roomid']]['__ref']
        self.i['nick'] = info[key]['displayName']
        self.i['logo'] = info[key]['profileImageURL(width:150)']
        if info[key]['stream'] is None:
            key = info[key]['broadcastSettings']['__ref']
            self.i['title'] = info[key]['title']
            self.i['area'] = info[info[key]['game']['__ref']]['displayName']
            self.i['status'] = config.CLOSED
        else:
            key = info[key]['stream']['__ref']
            self.i['title'] = info[info[key]['archiveVideo']['__ref']]['title']
            self.i['area'] = info[info[key]['game']['__ref']]['displayName']
            self.i['status'] = config.LIVE
    def get_live_url(roomid):
        session = streamlink.Streamlink()
        if 'http' in config.proxies and config.proxies['http'] != '':
            session.set_option('http-proxy', config.proxies['http'])
        # session.set_option('http-headers', 'Authorization=OAuth鉴权')
        streams = session.streams(f'https://twitch.tv/{roomid}')
        return streams['best'].url