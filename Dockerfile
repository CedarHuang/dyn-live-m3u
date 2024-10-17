FROM python:3-slim-bullseye

ENV LANG C.UTF-8
ENV TZ Asia/Shanghai

WORKDIR /app

RUN apt-get update && apt-get -y install git && apt-get install -y build-essential && apt-get clean
RUN git clone https://github.com/CedarHuang/dyn-live-m3u.git
RUN pip install -r dyn-live-m3u/requirements.txt
RUN cp -r dyn-live-m3u/src/* .

RUN mkdir /config
VOLUME /config

EXPOSE 3658

ENTRYPOINT ["./entrypoint.sh"]