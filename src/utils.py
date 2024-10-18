import quickjs

def check(dict, key, value):
    if key not in dict:
        dict[key] = value

def jsobject2json(str):
    stringify = quickjs.Function(
        "stringify",
        """
        function stringify() {{
            object = {str};
            return JSON.stringify(object);
        }}
        """.format(str = str))
    return stringify(str)

def streamlink_add_options(session, config, platform):
    if 'http' in config.proxies and config.proxies['http'] != '':
        session.set_option('http-proxy', config.proxies['http'])
    if platform not in config.toml['url']['option']:
        return
    for k, v in config.toml['url']['option'][platform].items():
        session.set_option(k, v)