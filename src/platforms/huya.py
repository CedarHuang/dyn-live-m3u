import grequests
import json
import re

import config
from platforms.channel import channel
from utils import jsobject2json

class huya(channel):
    def gen_req(self):
        return grequests.get('https://m.huya.com/' + self.i['roomid'], **config.request_params)
    def proc_res_impl(self, response):
        info = re.search(r'<script> window.HNF_GLOBAL_INIT = (.*?) </script>', response.text, re.S).group(1)
        info = json.loads(jsobject2json(info))
        live_status = info['roomInfo']['eLiveStatus']
        info = info['roomInfo']['tLiveInfo'] if live_status != 1 else info['roomInfo']['tRecentLive']
        self.i['nick'] = info['sNick']
        self.i['title'] = info['sIntroduction']
        self.i['area'] = info['sGameFullName']
        self.i['logo'] = info['sAvatar180']
        self.i['status'] = config.LIVE if live_status != 1 else config.CLOSED
