"""
Poller Twitter job.
"""
from . import config, db

from tweepy import Twitter, TweepError
from database.db import IntegrityError
from database.twitter.models import User, Token, Timeline, Status

import datetime
from operator import attrgetter

NEW_STATUS, EXISTING_STATUS, PLAIN_STATUS, SKIPPED_STATUS = (
    'new', 'existing', 'plain', 'skipped')
CONSUMER_KEY, CONSUMER_SECRET = (
    config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)

class TimelineJob(object):
    "Polling job for a Twitter timeline."

    def __init__(self, timeline, tokens):
        "Initialize the timeline model."
        assert timeline and tokens and \
            timeline.user_id in [t.user_id for t in tokens], \
            'Bad or missing TimelineJob args.'

        self.timeline = timeline
        self.tokens = tokens

        self.failed = False # yet
        self.started_at = None
        self.ended_at = None

        self.statuses = [] # return
        self.result = {
            NEW_STATUS: 0, EXISTING_STATUS: 0, PLAIN_STATUS: 0, SKIPPED_STATUS: 0
        }

        access_tokens = \
            {t.user_id: (t.key, t.secret) for t in tokens}
        self.twitter = Twitter(CONSUMER_KEY, CONSUMER_SECRET, access_tokens)

    def get_url(self, status):
        "Get first url from tweet if any."
        urls = hasattr(status, 'entities') and status.entities.get('urls')
        return urls and len(urls) and urls[0].get('expanded_url') or None

    def update_timeline(self, session):
        "Update timeline stats after doing the job."
        now = datetime.datetime.utcnow()
        timefreq = lambda timedelta, count: \
            int(timedelta.total_seconds() / (count - 1))

        statuses_count = len(self.statuses)
        timeline = session.merge(self.timeline) # just in case
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
            if statuses_count > 0:
                timeline.failures = 0 # reset failures
                last_status = max(self.statuses, key=attrgetter('status_id'))
                timeline.since_id = last_status.status_id # since_id
            if statuses_count > 2:
                first_status = min(self.statuses, key=attrgetter('status_id'))
                timedelta = last_status.created_at - first_status.created_at
                freq = timefreq(timedelta, statuses_count)
                timeline.frequency = max(min(freq, 
                    Timeline.MAX_FREQUENCY), Timeline.MIN_FREQUENCY) # frequency
            timeline.next_check = now + \
                datetime.timedelta(seconds=timeline.frequency) # next_check

    def load_status(self, session, tweet):
        "Load status from tweet if possible."
        status = result = None
        url = self.get_url(tweet)
        if not url: # plain status
            result = PLAIN_STATUS
            return status, result
        user = session.query(User).filter_by(user_id=tweet.user.id).first()
        if not user:
            user = User(tweet.user)
            session.add(user)
        elif user.ignored:
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

    def do(self, session):
        """
        Iterate the timeline and load relevant statuses.
        Calculate and update timeline stats when done.
        """
        assert self.timeline.enabled, 'Timeline disabled, can\'t do the job.'
        self.started_at = datetime.datetime.utcnow()
        try:
            user_id, since_id = (
                self.timeline.user_id, self.timeline.since_id)
            count = since_id or 300
            for tweet in self.twitter.home_timeline(
                user_id=user_id, since_id=since_id, count=count): # home_timeline
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
                print "%s: %s" % (result.capitalize(), 
                    status and unicode(status).encode('utf8') or \
                    "<Twitter Tweet (%s): %s...>" % (tweet.id, tweet.text[:30].encode('utf8')))
        except TweepError, e:
            if  e.response and (
                e.response.status_code < 400 or e.response.status_code >= 500):
                print e # warning
                # pass # no problem
            else:
                self.failed = True
        self.update_timeline(session)
        session.commit()
        self.ended_at = datetime.datetime.utcnow()

