"""
Poller worker.
"""
# import requests
# # https://urllib3.readthedocs.org/en/latest/security.html
# requests.packages.urllib3.disable_warnings()

# Preload libraries
import config
import logging, logging.config, yaml
logging.config.dictConfig(yaml.load(config.LOGGING))

from . import r

from raven import Client
from rq.contrib.sentry import register_sentry
client = Client(config.SENTRY_DSN)

import sys
from rq import Queue, Connection, Worker

QUEUE = config.POLLER_QUEUE

# Provide queue names to listen to as arguments to this script,
# similar to rqworker
with Connection(r):
    qs = map(Queue, sys.argv[1:]) or [Queue(QUEUE)]
    worker = Worker(qs)
    register_sentry(client, worker)
    worker.work()