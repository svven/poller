"""
Poller manager.
"""
from poller import config
import logging, logging.config, yaml
logging.config.dictConfig(yaml.load(config.LOGGING))

from manager import Manager
manager = Manager()

import sys, time
from rq import Queue, Connection, Worker


@manager.command
def enqueue(loop=False):
    "Enqueue timelines to be processed."
    from poller.twitter import queue
    while True:
        queue.enqueue()
        if not loop:
            break
        time.sleep(queue.FREQUENCY)

@manager.command
def work():
    "Queue worker processing timelines."
    from poller import r
    with Connection(r):
        worker = Worker([Queue(config.POLLER_QUEUE)])
        if config.SENTRY_DSN:
            from raven import Client
            from rq.contrib.sentry import register_sentry
            client = Client(config.SENTRY_DSN)
            register_sentry(client, worker)
        worker.work()


if __name__ == '__main__':
    manager.main()