import grequests
import json
import streamlink

from config import config
from platforms.channel import channel

class twitch(channel):
    def gen_req(self):
        data = {
            'operationName': 'MwebChannelLiveQuery',
            'variables': {
                'login': self.i['roomid'],
                'includeIsDJ': True,
            },
            'extensions': {
                'persistedQuery': {
                    'version': 1,
                    'sha256Hash': 'cfe04840f42b3a693d1de935ab8ebcb8d85857ac20dd8ce3001d6fa14eae97ec',
                }
            }
        }
        headers = {
            'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
        }
        return grequests.post('https://gql.twitch.tv/gql', json=data, headers=headers, proxies=config.proxies)
    def proc_res_impl(self, response):
        info = json.loads(response.text)
        info = info['data']['channel']
        self.i['nick'] = info['displayName']
        self.i['title'] = info['broadcastSettings']['title']
        self.i['area'] = info['broadcastSettings']['game']['displayName']
        self.i['logo'] = info['profileImageURL']
        self.i['status'] = config.LIVE if info['stream'] else config.CLOSED
    def get_live_url(roomid):
        session = streamlink.Streamlink()
        if 'http' in config.proxies and config.proxies['http'] != '':
            session.set_option('http-proxy', config.proxies['http'])
        # session.set_option('http-headers', 'Authorization=OAuth鉴权')
        streams = session.streams(f'https://twitch.tv/{roomid}')
        return streams['best'].url