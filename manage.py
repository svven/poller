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
from tweepy import Twitter


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

@manager.command
def load():
    "Load Twitter data from config to db."
    from poller import db
    from database.models import TwitterUser
    consumer_key, consumer_secret, access_tokens = (
        config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET, config.TWITTER_ACCESS_TOKENS)
    t = Twitter(consumer_key, consumer_secret, access_tokens)
    user_ids = access_tokens.keys()
    session = db.Session()
    for user in t.lookup_users(user_ids=user_ids):
        key, secret = access_tokens[user.id]
        tweeter = session.query(TwitterUser).filter_by(user_id=user.id).first()
        if not tweeter:
            tweeter = TwitterUser(user, key=key, secret=secret)
            session.add(tweeter)
    session.commit()
    session.close()

@manager.command
def process(screen_name):
    "Process timeline of specified user."
    from poller.twitter import queue
    from poller import db
    from database.models import TwitterUser
    session = db.Session()
    tweeter = session.query(TwitterUser).filter_by(screen_name=screen_name).first()
    if tweeter:
        queue.process(tweeter.user_id)


if __name__ == '__main__':
    manager.main()
