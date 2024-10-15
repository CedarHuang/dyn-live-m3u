from . import channel
from . import bilibili
from . import douyu
from . import huya
from . import twitch

def gen_channel(info):
    try:
        simple = info['simple'].split(':')
        info['platform'] = simple[0]
        info['roomid'] = simple[1]
        for i in range(2, len(simple)):
            if simple[i] == 'hide':
                info['hide'] = True
    except:
        pass
    try:
        return eval('{0}.{0}(info)'.format(info['platform']))
    except:
        print('Platform not yet supported.')
        return channel.exception(info)
