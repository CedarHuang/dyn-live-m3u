import grequests
import json
import streamlink

import utils
from config import config
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
    def get_live_url(roomid):
        session = streamlink.Streamlink()
        utils.streamlink_add_options(session, config, __class__.__name__)
        session.plugins.load_path("streamlink_plugins/streamlink-plugin-for-douyu")
        streams = session.streams(f'https://douyu.com/{roomid}')
        return streams['best'].url