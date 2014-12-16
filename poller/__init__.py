"""
Poller initialization.
"""
import config

import database
db = database.db

# TODO: Make this generic
database.config.sqlalchemy_url = config.sqlalchemy_url
database.config.SQLALCHEMY_DATABASE_URI = config.SQLALCHEMY_DATABASE_URI


from redis import Redis
r = Redis(config.REDIS_HOST, config.REDIS_PORT)

