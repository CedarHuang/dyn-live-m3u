import grequests
import json

import config
from platforms.channel import channel

class bilibili(channel):
    def gen_req(self):
        return grequests.get('https://api.live.bilibili.com/xlive/web-room/v1/index/getH5InfoByRoom?room_id=' + self.i['roomid'], **config.request_params)
    def proc_res_impl(self, response):
        info = json.loads(response.text)
        info = info['data']
        self.i['nick'] = info['anchor_info']['base_info']['uname']
        self.i['title'] = info['room_info']['title']
        self.i['area'] = info['room_info']['area_name']
        self.i['logo'] = info['anchor_info']['base_info']['face']
        self.i['status'] = config.LIVE if info['room_info']['live_status'] == 1 else config.CLOSED
        # self.i['status'] = BLOCKED if info['block_info']['block'] == True else self.i['status']
