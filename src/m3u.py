import grequests

import config
import platforms

def process(config_name):
    config.init(config_name)
    res_body = '#EXTM3U\n'
    channels = [platforms.gen_channel(i) for i in config.toml['channel']]
    responses = grequests.map([i.gen_req() for i in channels], exception_handler=lambda _, e: e)
    [channel.proc_res(response) for (channel, response) in list(zip(channels, responses))]
    res_body += ''.join([channel.gen_m3u_item() for channel in channels])
    return res_body