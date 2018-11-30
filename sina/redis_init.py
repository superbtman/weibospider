#!/usr/bin/env python
# encoding: utf-8
import redis
import sys
import os

sys.path.append(os.getcwd())
from sina.settings import LOCAL_REDIS_HOST, LOCAL_REDIS_PORT

r = redis.Redis(host=LOCAL_REDIS_HOST, port=LOCAL_REDIS_PORT)
# 因为SCHEDULER_PERSIST = True 所以redis中的url都保存了 在这里已经开始爬取的url 避免重复爬去
for key in r.scan_iter("weibo_spider*"):
    r.delete(key)

start_uids = [
    '2803301701',  # 人民日报
    '1699432410'  # 新华社
]
for uid in start_uids:
    r.lpush('weibo_spider:start_urls', "https://weibo.cn/%s/info" % uid)

print('redis初始化完毕')
