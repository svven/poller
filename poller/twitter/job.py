"""
Poller Twitter job.
"""
import logging
logger = logging.getLogger(__name__)

from . import config

from tweepy import Twitter, TweepError
# from meepy import Twitter, TweepError

from database.db import IntegrityError
from database.models import *

import datetime
from operator import attrgetter

NEW_STATUS, EXISTING_STATUS, PLAIN_STATUS, SKIPPED_STATUS = (
    'new', 'existing', 'plain', 'skipped')
CONSUMER_KEY, CONSUMER_SECRET = (
    config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)


class TimelineJob(object):
    "Polling job for a Twitter timeline."

    def __init__(self, timeline, users, tokens):
        "Initialize the timeline model."
        self.timeline = timeline
        self.users = users or [] # new
        self.tokens = tokens

        self.failed = False # yet
        self.started_at = None
        self.ended_at = None

        self.statuses = [] # new or existing
        self.result = {
            NEW_STATUS: 0, EXISTING_STATUS: 0, PLAIN_STATUS: 0, SKIPPED_STATUS: 0
        }

        access_tokens = {t.user_id: (t.key, t.secret) for t in tokens}
        self.twitter = Twitter(CONSUMER_KEY, CONSUMER_SECRET, access_tokens)

    def get_url(self, status):
        "Get first url from tweet if any."
        urls = hasattr(status, 'entities') and status.entities.get('urls')
        return urls and len(urls) and urls[0].get('expanded_url') or None

    def get_tweets(self):
        "Get Twitter API timeline method call."
        user_id = self.timeline.user_id
        list_id = self.timeline.list_id
        since_id = self.timeline.since_id
        count = self.timeline.since_id is None and 300 or None

        if self.timeline.type == Timeline.Type.HOME:
            return self.twitter.home_timeline(
                user_id=user_id, since_id=since_id, count=count) # home_timeline
        elif self.timeline.type == Timeline.Type.USER:
            return self.twitter.user_timeline(
                user_id=user_id, since_id=since_id, count=count) # user_timeline
        elif self.timeline.type == Timeline.Type.LIST:
            return self.twitter.list_timeline(
                list_id=list_id, since_id=since_id, count=count)


    def update_timeline(self, session):
        "Update timeline stats after doing the job."
        now = datetime.datetime.utcnow()
        timefreq = lambda timedelta, count: \
            int(timedelta.total_seconds() / (count - 1))
        timeline = session.merge(self.timeline) # just in case
        
        timeline.prev_check = now # prev_check
        statuses_count = len(self.statuses)
        if statuses_count > 0:
            last_status = max(self.statuses, key=attrgetter('status_id'))
            timeline.since_id = last_status.status_id # since_id
        if statuses_count > 2:
            first_status = min(self.statuses, key=attrgetter('status_id'))
            timedelta = last_status.created_at - first_status.created_at
            freq = timefreq(timedelta, statuses_count)
            timeline.frequency = max(min(freq, 
                Timeline.MAX_FREQUENCY), Timeline.MIN_FREQUENCY) # frequency
        if self.failed:
            timeline.failures += 1 # failures
            if timeline.failures >= Timeline.MAX_FAILURES:
                timeline.enabled = False # disabled
        else: # success
            timeline.failures = 0 # reset failures
            timeline.enabled = True # enabled
        timeline.next_check = now + \
            datetime.timedelta(seconds=timeline.frequency) # next_check
        session.commit() # stats matter

    def load_status(self, session, tweet):
        "Load status from tweet if possible."
        status = result = None
        url = self.get_url(tweet)
        if not url: # plain status
            result = PLAIN_STATUS
            return status, result
        user = session.query(TwitterUser).filter_by(user_id=tweet.user.id).first()
        if not user: # new
            user = TwitterUser(tweet.user)
            session.add(user)
            self.users.append(user)
        else:
            user.load(tweet.user)
            user = session.merge(user) # just in case
            if user.reader and user.reader.auth_user:
                user.reader.auth_user.load(user) # temp
        if user.ignored:
            result = SKIPPED_STATUS
            return status, result
        status = session.query(Status).filter_by(status_id=tweet.id).first()
        if not status: # new status
            status = Status(tweet)
            status.url = url
            session.add(status)
            result = NEW_STATUS
        else: # existing status
            result = EXISTING_STATUS
        return status, result

    def save_status(self, session, tweet):
        "Save status from tweet if needed."
        status = result = None
        try:
            status, result = self.load_status(session, tweet)
            if session.new: # new
                session.commit() # atomic
        except IntegrityError: # existing
            session.rollback()
            result = SKIPPED_STATUS
        if status: # new or existing
            self.statuses.append(status)
        self.result[result] += 1
        logger.debug(result.capitalize() + ": %s",
            status and unicode(status).encode('utf8') or \
            "<Twitter Tweet (%s): %s...>" % (tweet.id, tweet.text[:30].encode('utf8')))

    def do(self, session):
        """
        Iterate the timeline and load relevant statuses.
        Calculate and update timeline stats when done.
        """
        logger.debug("Start job")
        # assert self.timeline.enabled, 'Timeline disabled, can\'t do the job.'
        self.started_at = datetime.datetime.utcnow()
        try:
            if self.timeline:
                for tweet in self.get_tweets():
                    self.save_status(session, tweet)
                self.update_timeline(session)
            for user in set(self.users):
                for tweet in self.twitter.user_timeline(
                    user_id=user.user_id, count=100): # user_timeline
                    self.save_status(session, tweet)
        except TweepError, e:
            if  e.response and (
                e.response.status_code < 400 or e.response.status_code >= 500):
                pass # no problem
            else:
                self.failed = True
                if sum(self.result.values()) == 0:
                    self.result = repr(e) # exception
                logger.exception(e)

        finally:
            session.commit() # outside
            self.ended_at = datetime.datetime.utcnow()
            logger.debug("End job")

