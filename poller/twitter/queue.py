"""
Poller Twitter queue.
"""
from . import config, db, r
from job import TimelineJob

from database.twitter.models import User, State, Timeline

import time, datetime
from rq import Connection, Queue

QUEUE = config.POLLER_QUEUE
FREQUENCY = Timeline.MIN_FREQUENCY


def process(user_id):
    "Process specified timeline."
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

def enqueue(timelines=[]):
    "Enqueue timelines to process."
    now = datetime.datetime.utcnow()
    session = db.Session()
    try:
    	if not timelines:
        	timelines = session.query(Timeline).\
	            filter(Timeline.enabled == True, Timeline.next_check < now).\
	            order_by(Timeline.next_check)
        else:
        	timelines = [session.merge(t) for t in timelines]
        with Connection(r):
            q = Queue(QUEUE)
            for timeline in timelines:
                if timeline.state == State.BUSY: # warning
                    print '%s Skipped: %s' % (time.strftime('%X'), timeline)
                else:
                    user_id = timeline.user_id
                    job = q.enqueue_call(func=process, args=(user_id,), 
                        description=timeline) # job_id=unicode(user_id), result_ttl=0
                    timeline.state = State.BUSY
                    session.commit()
                    print '%s Queued: %s' % (time.strftime('%X'), timeline)
    except:
        session.rollback()
        raise
    finally:
        session.close()
