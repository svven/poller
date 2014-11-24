"""
Poller dispatcher.
"""
from . import db, r
from config import POLLER_QUEUE as QUEUE
from twitter.models import Tweeter, Token, Timeline
from twitter.job import TimelineJob

import time, datetime, random
from rq import Connection, Queue


def poll_timeline(tweeter_id):
    "Poll provided timeline job."
    s = db.Session()
    tweeter = s.query(Tweeter).filter_by(tweeter_id=tweeter_id).one()
    job = TimelineJob(tweeter.timeline, [tweeter.token]) # user_timeline
    job.do()
    s.close()
    return job.result

def poll_timelines():
    "Poll available timeline jobs."
    s = db.Session()
    now = datetime.datetime.utcnow()
    timelines = s.query(Timeline).\
        filter(Timeline.enabled == True, Timeline.next_check < now).\
        order_by(Timeline.next_check)
    with Connection(r):
        q = Queue(QUEUE)
        for timeline in timelines:
            tweeter_id = timeline.tweeter_id
            job = q.enqueue_call(func=poll_timeline, args=(tweeter_id,), 
                description=timeline) # job_id=unicode(tweeter_id), result_ttl=0
            print '%s %s: %s' % (time.strftime('%X'), 
                job.get_status().capitalize(), job.description)
    s.close()

def dispatch():
    "Polling timelines periodically."
    while True:
        poll_timelines()
        print '%s Sleeping' % time.strftime('%X')
        time.sleep(Timeline.MIN_FREQUENCY)

