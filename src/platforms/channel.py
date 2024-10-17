import grequests
import re

from requests import models
from requests import exceptions

import platforms
from config import config
from utils import check

retry_deepth_max = 2
retry_deepth = 0

class channel:
    def __init__(self, info):
        self.i = info
    def proc_res(self, response):
        global retry_deepth
        # return self.proc_res_impl(response)
        try:
            self.proc_res_impl(response)
        except:
            if type(response) != models.Response:
                print(type(response))
                print(response)
            if type(response) == models.Response and retry_deepth < retry_deepth_max:
                retry_deepth += 1
                response = grequests.map([grequests.get(response.url, headers=config.headers, proxies=config.proxies, timeout=config.retry_time_limit)])[0]
                platforms.gen_channel(self.__dict__['i']).proc_res(response)
            else:
                exception(self.__dict__['i']).proc_res_impl(response)
        retry_deepth = 0
    def gen_m3u_item(self):
        if 'hide' in self.i and self.i['hide'] and self.i['status'] not in (config.LIVE, config.LOOP, config.EXCEPTION, config.TIMEOUT):
            return ''
        for key in config.toml['re']:
            for re_item in config.toml['re'][key]:
                try:
                    self.i[key] = eval('re.sub(%s, self.i[key])' % re_item)
                except:
                    pass
        self.i['name'] = config.toml['format']['name'].format(**self.i)
        self.i['group'] = config.toml['format']['group'].format(**self.i)
        for key in ['name', 'group']:
            for re_item in config.toml['re'][key]:
                try:
                    self.i[key] = eval('re.sub(%s, self.i[key])' % re_item)
                except:
                    pass
        res = '#EXTINF:-1 tvg-logo="%s" group-title="%s",%s\n' % (self.i['logo'], self.i['group'], self.i['name'])
        res += config.toml['format']['url'].get(self.i['platform'], config.toml['format']['url']['default']).format(**self.i) + '\n'
        return res

class exception(channel):
    def gen_req(self):
        return grequests.get('')
    def proc_res_impl(self, response):
        check(self.i, 'nick', self.i['roomid'])
        check(self.i, 'title', self.i['platform'] + ':' + self.i['nick'])
        check(self.i, 'area', self.i['platform'])
        check(self.i, 'logo', '')
        check(self.i, 'status', config.TIMEOUT if isinstance(response, exceptions.Timeout) else config.EXCEPTION)