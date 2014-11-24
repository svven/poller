"""
Poller Twitter job.
"""
from . import db
from ..config import \
    TWITTER_CONSUMER_KEY as consumer_key, TWITTER_CONSUMER_SECRET as consumer_secret
from api import Twitter, TweepError
from models import Tweeter, Token, Timeline, Tweet

import datetime
from operator import attrgetter

NEW_TWEET, EXISTING_TWEET, PLAIN_TWEET = ('new', 'existing', 'plain')


class TimelineJob(object):
    "Polling job for a Twitter timeline."

    def __init__(self, timeline, tokens):
        "Initialize the timeline model."
        assert timeline and tokens and \
            timeline.tweeter_id in [t.tweeter_id for t in tokens], \
            'Bad or missing TimelineJob args.'

        self.timeline = timeline
        self.tokens = tokens

        self.failed = False # yet
        self.started_at = None
        self.ended_at = None

        self.tweets = [] # return
        self.result = {
            NEW_TWEET: 0, EXISTING_TWEET: 0, PLAIN_TWEET: 0
        }

        access_tokens = \
            {t.tweeter_id: (t.key, t.secret) for t in tokens}
        self.twitter = Twitter(consumer_key, consumer_secret, access_tokens)

    def get_url(self, status):
        "Get first url from status if any."
        urls = hasattr(status, 'entities') and status.entities.get('urls')
        return urls and len(urls) and urls[0].get('expanded_url') or None

    def update_timeline(self, session):
        "Update timeline stats after doing the job."
        now = datetime.datetime.utcnow()
        timefreq = lambda timedelta, count: \
            int(timedelta.total_seconds() / (count - 1))

        timeline = session.merge(self.timeline)
        tweets_count = len(self.tweets)
        timeline.prev_check = now # prev_check
        if self.failed:
            timeline.failures += 1 # failures
            if timeline.failures >= Timeline.MAX_FAILURES:
                timeline.enabled = False # disabled
                timeline.next_check = None # next_check
            else:
                timeline.next_check = now + \
                    datetime.timedelta(seconds=timeline.frequency) # next_check
        else: # success
            if tweets_count > 0:
                timeline.failures = 0 # reset failures
                last_tweet = max(self.tweets, key=attrgetter('status_id'))
                timeline.since_id = last_tweet.status_id # since_id
            if tweets_count > 2:
                first_tweet = min(self.tweets, key=attrgetter('status_id'))
                timedelta = last_tweet.created_at - first_tweet.created_at
                tweetfreq = timefreq(timedelta, tweets_count)
                timeline.frequency = max(min(tweetfreq, 
                    Timeline.MAX_FREQUENCY), Timeline.MIN_FREQUENCY) # frequency
            timeline.next_check = now + \
                datetime.timedelta(seconds=timeline.frequency) # next_check

    def load_tweet(self, session, status):
        "Load tweet from status if possible."
        url = self.get_url(status)
        if not url: # plain tweet
            self.result[PLAIN_TWEET] += 1
            return
        tweeter = session.query(Tweeter).filter_by(tweeter_id=status.user.id).first()
        if not tweeter:
            tweeter = Tweeter(status.user)
            session.add(tweeter)
        tweet = session.query(Tweet).filter_by(status_id=status.id).first()
        if not tweet: # new tweet
            tweet = Tweet(status)
            tweet.source_url = url
            session.add(tweet)
            self.result[NEW_TWEET] += 1
        else: # existing tweet
            self.result[EXISTING_TWEET] += 1
        print unicode(tweet).encode('utf8')
        self.tweets.append(tweet)

    def do(self):
        """
        Iterate the timeline and load relevant tweets.
        Calculate and update timeline stats when done.
        """
        assert self.timeline.enabled, 'Timeline disabled, can\'t do the job.'
        self.started_at = datetime.datetime.utcnow()
        session = db.Session()
        try:
            user_id, since_id = (
                self.timeline.tweeter_id, self.timeline.since_id)
            count = since_id or 300
            try:
                for status in self.twitter.home_timeline(
                    user_id=user_id, since_id=since_id, count=count): # home_timeline
                    self.load_tweet(session, status)
            except TweepError, e:
                if  e.response and (
                    e.response.status_code < 400 or e.response.status_code >= 500):
                    print e # warning
                    pass # no problem
                else:
                    self.failed = True
            self.update_timeline(session)
            session.commit()
        except Exception, e:
            session.rollback()
            raise e # probably db problem
        finally:
            session.close()
        self.ended_at = datetime.datetime.utcnow()

