"""
Poller dispatcher.
"""
from . import db, r
from config import POLLER_QUEUE as QUEUE
from database.twitter.models import User, Token, State, Timeline
from twitter.job import TimelineJob

import time, datetime, random
from rq import Connection, Queue


def poll_timeline(user_id):
    "Poll provided timeline job."
    session = db.Session()
    try:
        user = session.query(User).filter_by(user_id=user_id).one()
        job = TimelineJob(user.timeline, [user.token]) # user_timeline
        job.do(session)
        timeline = session.merge(user.timeline)
        timeline.state = job.failed and State.FAIL or State.DONE
        session.commit()
        return job.result
    except:
        session.rollback()
        raise
    finally:
        session.close()

def poll_timelines():
    "Poll available timeline jobs."
    now = datetime.datetime.utcnow()
    session = db.Session()
    try:
        timelines = session.query(Timeline).\
            filter(Timeline.enabled == True, Timeline.next_check < now).\
            order_by(Timeline.next_check)
        with Connection(r):
            q = Queue(QUEUE)
            for timeline in timelines:
                if timeline.state == State.BUSY:
                    print '%s Skipped: %s' % (time.strftime('%X'), timeline)
                else:
                    user_id = timeline.user_id
                    job = q.enqueue_call(func=poll_timeline, args=(user_id,), 
                        description=timeline) # job_id=unicode(user_id), result_ttl=0
                    timeline.state = State.BUSY
                    session.commit()
                    print '%s Queued: %s' % (time.strftime('%X'), timeline)
    except:
        session.rollback()
        raise
    finally:
        session.close()

def dispatch():
    "Polling timelines periodically."
    while True:
        poll_timelines()
        print '%s Sleeping' % time.strftime('%X')
        time.sleep(Timeline.MIN_FREQUENCY)

