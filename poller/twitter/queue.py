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
    failed = False # yet
    user = session.query(User).filter_by(user_id=user_id).one()
    try:
        # assert user.timeline.state == State.BUSY # not necessarily
        job = TimelineJob(user.timeline, [user.token]) # user_timeline
        job.do(session)
        failed = job.failed # may be True
        return job.result
    except:
        session.rollback()
        failed = True # obviously
        raise
    finally:
        timeline = session.merge(user.timeline) # no need
        timeline.state = failed and State.FAIL or State.DONE
        session.commit()
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
