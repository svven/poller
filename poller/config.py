"""
Config settings for poller app.
"""
import os, socket

## SQLAlchemy
## http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html
# SQLALCHEMY_ECHO = sqlalchemy_echo = True
DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
SQLALCHEMY_DATABASE_URI = sqlalchemy_url = 'postgresql://svven@%s/svven' % DATABASE_HOST

## RQ (Redis Queue)
RQ_REDIS_HOST = os.environ.get('RQ_REDIS_HOST', 'localhost')
RQ_REDIS_PORT = 6379
RQ_REDIS_DB = 0
QUEUES = (POLLER_QUEUE, ) = ("poller", )

## Twitter # @SvvenDotCom
TWITTER_CONSUMER_KEY = 'Jrp1bcXiSahhWAqn3VJb4fzsg'
TWITTER_CONSUMER_SECRET = '36xO8Y8YT7Y0hRHDwoULuTU2xyru6cPkCSrRxLoJAzZ3hmxhfS'

TWITTER_DEFAULT_TOKEN = 2493963913
TWITTER_ACCESS_TOKENS = {
    2493963913: # svvendotcom
    (u'2493963913-XBqema44oP95guiznQf1m5TGtPz7eAyEQ75wFpJ', u'TizqhmhFeFHRnRWdHfoz3OZdO5jT4DX3JiCNBqmov8muM'),
}

## Sentry
SENTRY_DSN = 'https://a5087c7f1fc344cbbc37e71f846a184e:98b7703681d14154b4f14b827f6acb9f@app.getsentry.com/46868'

## Papertrail
HOSTNAME = socket.gethostname()
PAPERTRAIL_HOST = 'logs3.papertrailapp.com'
PAPERTRAIL_PORT = '20728'

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
        handlers: [console, papertrail]
        level: DEBUG
handlers:
    console:
        level: DEBUG
        class: logging.StreamHandler
        formatter: console
    sentry:
        level: INFO
        class: raven.handlers.logging.SentryHandler
        dsn: {sentry_dsn}
    papertrail:
        level: INFO
        class: logging.handlers.SysLogHandler
        address: [{papertrail_host}, {papertrail_port}]
        formatter: papertrail
formatters:
    console:
        format: '%(asctime)s %(message)s'
        # format: '[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s'
        datefmt: '%H:%M:%S'
    papertrail:
        format: '%(asctime)s {hostname} %(process)d %(message)s'
        datefmt: '%H:%M:%S'
'''
LOGGING = LOGGING.format(sentry_dsn=SENTRY_DSN, hostname=HOSTNAME,
    papertrail_host=PAPERTRAIL_HOST, papertrail_port=PAPERTRAIL_PORT)
