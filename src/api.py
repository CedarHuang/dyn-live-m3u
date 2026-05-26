import json
import os
import re

CONFIG_DIR = '../config'

def _config_path(config_name):
    return f'{CONFIG_DIR}/{config_name}.toml'

def _parse_channels(text):
    pattern = re.compile(
        r'(^[ \t]*#)?[ \t]*\[\[channel\]\](?:[ \t]*#[ \t]*(.*?))?[ \t]*\n'
        r'(?:[ \t]*#)?[ \t]*simple[ \t]*=[ \t]*[\'"]([^\'"]+)[\'"]',
        re.MULTILINE,
    )
    channels = []
    for m in re.finditer(pattern, text):
        enabled = m.group(1) is None
        name = (m.group(2) or '').strip()
        simple = m.group(3)
        parts = simple.split(':')
        platform = parts[0]
        roomid = parts[1]
        hide = len(parts) > 2 and parts[2] == 'hide'
        channels.append({
            'platform': platform,
            'roomid': roomid,
            'hide': hide,
            'name': name,
            'enabled': enabled,
        })
    return channels

def _build_channel_lines(channel):
    name_suffix = f' # {channel["name"]}' if channel.get('name') else ''
    hide_suffix = ':hide' if channel.get('hide') else ''
    simple = f'{channel["platform"]}:{channel["roomid"]}{hide_suffix}'
    if channel.get('enabled', True):
        return [f'[[channel]]{name_suffix}', f"simple = '{simple}'"]
    else:
        return [f'# [[channel]]{name_suffix}', f"# simple = '{simple}'"]

def _rebuild(text, channels):
    first = re.search(r'^\[\[channel\]\]|^# \[\[channel\]\]', text, re.MULTILINE)
    if first:
        header = text[:first.start()]
    else:
        header = text.rstrip() + '\n\n'
    lines = []
    for ch in channels:
        lines.extend(_build_channel_lines(ch))
        lines.append('')
    return header + '\n'.join(lines)

def _read(config_name):
    with open(_config_path(config_name), 'r', encoding='utf-8') as f:
        return f.read()

def _write(config_name, text):
    with open(_config_path(config_name), 'w', encoding='utf-8') as f:
        f.write(text)

def list_configs():
    configs = []
    try:
        for f in os.listdir(CONFIG_DIR):
            if f.endswith('.toml'):
                configs.append(f[:-5])
        configs.sort()
    except FileNotFoundError:
        pass
    return configs

def list_channels(config_name):
    text = _read(config_name)
    channels = _parse_channels(text)
    for i, ch in enumerate(channels):
        ch['index'] = i
    return channels

def add_channel(config_name, channel):
    text = _read(config_name)
    channels = _parse_channels(text)
    index = channel.pop('index', len(channels))
    channel.setdefault('hide', False)
    channel.setdefault('enabled', True)
    channel.setdefault('name', '')
    channels.insert(index, channel)
    _write(config_name, _rebuild(text, channels))
    return {'ok': True, 'index': index}

def delete_channel(config_name, index):
    text = _read(config_name)
    channels = _parse_channels(text)
    if 0 <= index < len(channels):
        channels.pop(index)
        _write(config_name, _rebuild(text, channels))
        return {'ok': True}
    return {'ok': False, 'error': 'index out of range'}

def update_channel(config_name, index, fields):
    text = _read(config_name)
    channels = _parse_channels(text)
    if 0 <= index < len(channels):
        channels[index].update(fields)
        _write(config_name, _rebuild(text, channels))
        return {'ok': True}
    return {'ok': False, 'error': 'index out of range'}

def move_channel(config_name, from_idx, to_idx):
    text = _read(config_name)
    channels = _parse_channels(text)
    n = len(channels)
    if 0 <= from_idx < n and 0 <= to_idx < n:
        ch = channels.pop(from_idx)
        channels.insert(to_idx, ch)
        _write(config_name, _rebuild(text, channels))
        return {'ok': True}
    return {'ok': False, 'error': 'index out of range'}

def set_platform_option(config_name, platform, key, value):
    path = _config_path(config_name)
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    section = f'[url.option.{platform}]'
    line = f"{key} = '{value}'"
    _sec = re.escape(f'url.option.{platform}')
    pattern = re.compile(
        r'^[ \t]*#?[ \t]*\[' + _sec + r'\]\s*\n'
        r'(?:(?!\[[a-z]|^\s*$|^[ \t]*#?[ \t]*\[)[^\n]*\n)*',
        re.MULTILINE,
    )
    m = pattern.search(text)

    # extract current value for comparison
    current = None
    if m:
        val_match = re.search(f"^{key}\\s*=\\s*'([^']*)'", m.group(0), re.MULTILINE)
        if val_match:
            current = val_match.group(1)

    if current == value:
        return {'ok': True, 'synced': False}

    if m:
        new_block = [section, line]
        new_text = text[:m.start()] + '\n'.join(new_block) + '\n' + text[m.end():]
    else:
        new_text = text.rstrip() + f'\n\n{section}\n{line}\n'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    return {'ok': True, 'synced': True}
