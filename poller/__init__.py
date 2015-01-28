"""
Poller initialization.
"""
import config, database, redis

## Database
database.load_config(config)
db = database.db

## Redis
r = redis.StrictRedis(config.RQ_REDIS_HOST, config.RQ_REDIS_PORT, config.RQ_REDIS_DB)
