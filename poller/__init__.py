"""
Poller initialization.
"""
import requests
requests.packages.urllib3.disable_warnings()

import config, database, redis

def init(config_updates=None):
    """
    Delayed init to allow config updates.
    Updates can be passed as param here or set onto `config` upfront.
    i.e. `config.SETTING = updates.PREFIX_SETTING or updates.SETTING`
    """
    if config_updates:
        config.from_object(config_updates)

    global db, r

    ## Database
    database.init(config)
    db = database.db

    ## Redis
    r = redis.StrictRedis(config.RQ_REDIS_HOST, config.RQ_REDIS_PORT, config.RQ_REDIS_DB)
