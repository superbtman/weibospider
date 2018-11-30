# -*- coding: utf-8 -*-

BOT_NAME = 'sina'

SPIDER_MODULES = ['sina.spiders']
NEWSPIDER_MODULE = 'sina.spiders'

ROBOTSTXT_OBEY = False

DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
}

# CONCURRENT_REQUESTS 和 DOWNLOAD_DELAY 根据账号池大小调整 目前的参数是账号池大小为200

CONCURRENT_REQUESTS = 16

DOWNLOAD_DELAY = 0.1

DOWNLOADER_MIDDLEWARES = {
    'weibo.middlewares.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    'sina.middlewares.CookieMiddleware': 300,
    'sina.middlewares.RedirectMiddleware': 200,
}

ITEM_PIPELINES = {
    'sina.pipelines.MongoDBPipeline': 300,
}

# MongoDb 配置

LOCAL_MONGO_HOST = '127.0.0.1'
LOCAL_MONGO_PORT = 27017
DB_NAME = 'Sina'

# Redis 配置
LOCAL_REDIS_HOST = '127.0.0.1'
LOCAL_REDIS_PORT = 6379

# 任务的分发和调度 把所有的爬虫开始的请求都放在redis里边 所有爬虫从redis里面去读取请求
SCHEDULER = "scrapy_redis_bloomfilter.scheduler.Scheduler"

# DUPEFILTER_CLASS是去重队列 负责所有请求的去重
DUPEFILTER_CLASS = "scrapy_redis_bloomfilter.dupefilter.RFPDupeFilter"

# Redis URL
REDIS_URL = 'redis://{}:{}'.format(LOCAL_REDIS_HOST, LOCAL_REDIS_PORT)

# Number of Hash Functions to use, defaults to 6
BLOOMFILTER_HASH_NUMBER = 6

# Redis Memory Bit of Bloomfilter Usage, 30 means 2^30 = 128MB, defaults to 30
BLOOMFILTER_BIT = 31

# Persist
SCHEDULER_PERSIST = True
# '''
# 如果这一项为True，那么在Redis中的URL不会被Scrapy_redis清理掉，
# 这样的好处是：爬虫停止了再重新启动，它会从上次暂停的地方开始继续爬取。
# 但是它的弊端也很明显，如果有多个爬虫都要从这里读取URL，需要另外写一段代码来防止重复爬取。

# 如果设置成了False，那么Scrapy_redis每一次读取了URL以后，就会把这个URL给删除。
# 这样的好处是：多个服务器的爬虫不会拿到同一个URL，也就不会重复爬取。
# 但弊端是：爬虫暂停以后再重新启动，它会重新开始爬。
# '''




#1. 增加了一个去重容器类的配置, 作用使用Redis的set集合来存储请求的指纹数据, 从而实现请求去重的持久化
#DUPEFILTER_CLASS = “scrapy_redis.dupefilter.RFPDupeFilter”

#2. 增加了调度的配置, 作用: 把请求对象存储到Redis数据, 从而实现请求的持久化.
#SCHEDULER = “scrapy_redis.scheduler.Scheduler”

#3. 配置调度器是否要持久化, 也就是当爬虫结束了, 要不要清空Redis中请求队列和去重指纹的set。如果是True, 就表示要持久化存储, 就不清空数据, 否则清空数据
#SCHEDULER_PERSIST = True

#4. redis_url配置
#REDIS_URL = ‘reds://127.0.0.1:6379/2’
