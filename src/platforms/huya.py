import grequests
import json
import re
import streamlink

import utils
from config import config
from platforms.channel import channel

class huya(channel):
    def gen_req(self):
        return grequests.get('https://m.huya.com/' + self.i['roomid'], **config.request_params)
    def proc_res_impl(self, response):
        info = re.search(r'<script> window.HNF_GLOBAL_INIT = (.*?) </script>', response.text, re.S).group(1)
        info = json.loads(utils.jsobject2json(info))
        live_status = info['roomInfo']['eLiveStatus']
        info = info['roomInfo']['tLiveInfo'] if live_status != 1 else info['roomInfo']['tRecentLive']
        self.i['nick'] = info['sNick']
        self.i['title'] = info['sIntroduction']
        self.i['area'] = info['sGameFullName']
        self.i['logo'] = info['sAvatar180']
        self.i['status'] = config.LIVE if live_status != 1 else config.CLOSED
    def get_live_url(roomid):
        session = streamlink.Streamlink()
        utils.streamlink_add_options(session, config, __class__.__name__)
        streams = session.streams(f'https://huya.com/{roomid}')
        return streams['best'].url