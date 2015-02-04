"Temp admin script"

import redis
from tweepy import Twitter

from poller import db
from poller.twitter.job import TimelineJob

from database.twitter.models import User, Token, Timeline

from config import \
    TWITTER_CONSUMER_KEY as consumer_key, TWITTER_CONSUMER_SECRET as consumer_secret, \
    TWITTER_ACCESS_TOKENS as access_tokens

def load_database():
    "From config tokens."

    s = db.Session()
    t = Twitter(consumer_key, consumer_secret, access_tokens)

    # users
    user_ids = access_tokens.keys()
    for user in t.lookup_users(user_ids=user_ids):
        tweeter = User(user)
        s.add(tweeter)

    # tokens
    for user_id in user_ids:
        key, secret = access_tokens[user_id]
        token = Token(user_id=user_id, key=key, secret=secret)
        s.add(token)

    s.commit()
    s.close()


def set_popular():
    "From redis db."

    r = redis.Redis()
    s = db.Session()
    t = Twitter(consumer_key, consumer_secret, access_tokens)

    user_ids = list(r.zrevrange('hn_users:following', 0, 100, withscores=False))
    existing = set([id for id, in s.query(User.user_id).all()])

    for user in t.lookup_users(user_ids=[id for id in user_ids if id not in existing]):
        tweeter = User(user)
        s.add(tweeter)
        print tweeter

    s.commit()
    s.close()


def poll_timeline(screen_name):
    "Using TimelineJob."
    import random

    s = db.Session()
    tweeter = s.query(User).filter_by(screen_name=screen_name).first()
    assert tweeter

    timeline = tweeter.timeline
    if not timeline:
        timeline = Timeline(user_id=tweeter.user_id)
        s.add(timeline)
        s.commit()
    job = TimelineJob(timeline, [tweeter.token])
    job.do(s)
    print job.result

    s.close()

