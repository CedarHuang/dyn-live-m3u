import grequests
import json

import config
from platforms.channel import channel

class douyu(channel):
    def gen_req(self):
        return grequests.get('https://www.douyu.com/betard/' + self.i['roomid'], **config.request_params)
    def proc_res_impl(self, response):
        info = json.loads(response.text)
        # info = info['pageProps']['room']['roomInfo']['roomInfo']
        self.i['nick'] = info['room']['nickname']
        self.i['title'] = info['room']['room_name']
        self.i['area'] = info['game']['tag_name']
        self.i['logo'] = info['room']['avatar']['big']
        self.i['status'] = config.LIVE if info['room']['show_status'] == 1 else config.CLOSED
        self.i['status'] = config.LOOP if info['room']['videoLoop'] == 1 else self.i['status']
