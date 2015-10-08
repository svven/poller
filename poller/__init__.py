"""
Poller initialization.
"""
import requests
requests.packages.urllib3.disable_warnings()

import config, database, redis

## Database
database.init(config)
db = database.db

## Redis
r = redis.StrictRedis(config.RQ_REDIS_HOST, config.RQ_REDIS_PORT, config.RQ_REDIS_DB)
