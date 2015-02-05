"""
Config settings for poller app.
"""

## SQLAlchemy
## http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html
# SQLALCHEMY_ECHO = sqlalchemy_echo = True
SQLALCHEMY_DATABASE_URI = sqlalchemy_url = 'postgresql://svven@localhost/test'

## RQ (Redis Queue)
RQ_REDIS_HOST = 'localhost'
RQ_REDIS_PORT = 6379
RQ_REDIS_DB = 0
QUEUES = (POLLER_QUEUE, ) = ("poller", )

## Twitter # @SvvenDotCom
TWITTER_CONSUMER_KEY = 'Jrp1bcXiSahhWAqn3VJb4fzsg'
TWITTER_CONSUMER_SECRET = '36xO8Y8YT7Y0hRHDwoULuTU2xyru6cPkCSrRxLoJAzZ3hmxhfS'

TWITTER_ACCESS_TOKENS = {
    2493963913: # svvendotcom
    (u'2493963913-XBqema44oP95guiznQf1m5TGtPz7eAyEQ75wFpJ', u'TizqhmhFeFHRnRWdHfoz3OZdO5jT4DX3JiCNBqmov8muM'),
}

## Sentry
SENTRY_DSN = ''

## Logging
LOGGING = '''
version: 1
disable_existing_loggers: true
root:
    level: INFO
    propagate: true
loggers:
    rq:
        handlers: [console]
        level: INFO
    tweepy:
        handlers: [console]
        level: WARNING
    poller:
        handlers: [console, sentry]
        level: DEBUG
handlers:
    console:
        level: DEBUG
        class: logging.StreamHandler
        formatter: console
    sentry:
        level: INFO
        class: raven.handlers.logging.SentryHandler
        dsn: {dsn}
formatters:
    console:
        format: '%(asctime)s %(message)s'
        # format: '[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s'
        datefmt: '%H:%M:%S'
'''
LOGGING = LOGGING.format(dsn=SENTRY_DSN)
