"""
Poller initialization.
"""
import config

import database, redis

## Database
database.config.sqlalchemy_url = config.sqlalchemy_url
database.config.SQLALCHEMY_DATABASE_URI = config.SQLALCHEMY_DATABASE_URI
db = database.db

## Redis
r = redis.StrictRedis(config.RQ_REDIS_HOST, config.RQ_REDIS_PORT, config.RQ_REDIS_DB)
