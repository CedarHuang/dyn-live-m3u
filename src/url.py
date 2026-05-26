import sys

import config
import platforms

def process(platform, roomid):
    config.init('default')
    try:
        module = getattr(platforms, platform)
        cls = getattr(module, platform)
        return cls.get_live_url(roomid)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f"[/{platform}/{roomid}] {exc_type.__name__}: {exc_value}")
        # print(f"Exception traceback: {exc_traceback}")
        return ''
