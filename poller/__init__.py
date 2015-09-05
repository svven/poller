"""
Poller initialization.
"""
# https://urllib3.readthedocs.org/en/latest/security.html#insecurerequestwarning
import urllib3
urllib3.disable_warnings() # temp

import config, database, redis

## Database
database.init(config)
db = database.db

## Redis
r = redis.StrictRedis(config.RQ_REDIS_HOST, config.RQ_REDIS_PORT, config.RQ_REDIS_DB)
