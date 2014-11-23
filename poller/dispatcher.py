"""
Poller dispatcher.
"""
from . import db, r
from config import POLLER_QUEUE as QUEUE
from twitter.models import Tweeter, Token, Timeline
from twitter.job import TimelineJob

import time, datetime, random
from rq import Connection, Queue
from rq.job import Status


def poll_timeline(tweeter_id):
    "Poll provided timeline job."
    s = db.Session()
    try:
        tweeter = s.query(Tweeter).filter_by(tweeter_id=tweeter_id).one()
        job = TimelineJob(tweeter.timeline, [tweeter.token]) # user_timeline
        job.do()
        return job.results
    except Exception, e:
        raise e
    finally:
        s.close()
    # if timeline.method == Timeline.HOME_TIMELINE:
    #     # do the above
    # else: # timeline.method == Timeline.USER_TIMELINE:
    #     return # give up home_timelines

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
            job = q.fetch_job(unicode(tweeter_id))
            if job is None or job.get_status() == Status.FINISHED:
                job = q.enqueue_call(
                    func=poll_timeline, args=(tweeter_id,), 
                    job_id=unicode(tweeter_id), description=timeline)
            print '%s %s: %s' % (
                time.strftime('%X'), job.get_status().capitalize(), job)
    s.close()

def dispatch():
    "Polling timelines periodically."
    while True:
        poll_timelines()
        print '%s Sleeping' % time.strftime('%X')
        time.sleep(Timeline.MIN_FREQUENCY)

