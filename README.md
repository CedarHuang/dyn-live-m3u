# dyn-live-m3u
可自定义的直播m3u文件生成服务

本项目能动态获取房间信息并生成m3u, 并具有解析房间真实播放链接的能力.

目前仅支持 bilibili, douyu, huya, twitch.

尽管已经采取了并发请求设计, 但因为需要获取每个房间的信息, 所以如果配置频道过多的话, 响应速度会严重减慢, 故并不建议配置太多频道, 只按需配置平时常看的就好.

## 快速开始

### Docker

#### 1. 创建配置目录
在你选定的任意位置创建一个目录, 并记录路径

#### 2. 下载镜像
```shell
docker pull cedarhuang/dyn-live-m3u:latest
```

#### 3. 运行镜像
```shell
# 请注意修改config路径
docker run -d -p 3658:3658 -v 本地挂载config路径:/config cedarhuang/dyn-live-m3u
```

#### 4. 访问 `http://Docker宿主机IP:3658`
如看到m3u配置文本, 则表明成功.

### Python (不建议)
如果你本地具有Python3.11环境, 可直接运行.
```shell
git clone https://github.com/CedarHuang/dyn-live-m3u.git
cd dyn-live-m3u/src
pip3.11 install -r ../requirements.txt
python3.11 app.py
```

## 配置
Docker启动后会自动在挂载的config路径中生成 `default.toml`,  

### 代理播放链接配置
找到 `default.toml` 中的:
```toml
default = 'http://你的IP:端口/{platform}/{roomid}'
```
将 `"你的IP:端口"` 修改为解析链接服务的IP与端口.

如Docker部署的本服务, 可配置为 ```Docker宿主机IP:3658```.

### 频道配置
找到 `default.toml` 中的:
```toml
[[channel]]
simple = 'douyu:3484'
[[channel]]
simple = 'bilibili:732'
```
将其修改为自己需要的频道信息.  
每一个频道都形如:
```toml
[[channel]]
simple = '平台(字母形式):房间号'
```

### 进阶配置
本服务支持多配置:  
访问 `http://Docker宿主机IP:3658` 默认使用 `default.toml`  
如需使用第二套配置如 `second.toml`, 则需访问 `http://Docker宿主机IP:3658/second`

更多配置字段的含义, 在 [default.toml](https://github.com/CedarHuang/dyn-live-m3u/blob/master/config/default.toml) 中有详细解释, 请自行查阅修改.