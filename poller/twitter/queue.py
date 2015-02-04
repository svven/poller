"""
Poller Twitter queue.
"""
import logging
logger = logging.getLogger(__name__)

from . import config, db, r

from job import TimelineJob
from database.news.models import Reader
from database.twitter.models import User, State, Timeline

import time, datetime
from rq import Connection, Queue

QUEUE = config.POLLER_QUEUE
FREQUENCY = Timeline.MIN_FREQUENCY
RESULT_TTL = 1 * 60 # 1 min


def process(user_id):
    "Process specified timeline."
    logger.debug("Start process")
    session = db.Session()
    failed = False # yet
    user = session.query(User).filter_by(user_id=user_id).one()
    timeline, token = (user.timeline, user.token)
    try:
        # assert timeline.state == State.BUSY # not necessarily
        job = TimelineJob(timeline, [token]) # user_timeline
        job.do(session)
        failed = job.failed # may be True
        return job.result
    except:
        session.rollback()
        failed = True # obviously
        logger.warning("Fail: %s", 
            unicode(timeline).encode('utf8'),
            exc_info=True, extra={'data': {'id': timeline.id}})
        raise
    finally:
        timeline = session.merge(timeline) # no need
        timeline.state = failed and State.FAIL or State.DONE
        session.commit()
        session.close()
        logger.debug("End process")

def enqueue(timelines=[]):
    "Enqueue timelines to process."
    now = datetime.datetime.utcnow()
    logger.debug("Start enqueue")
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
                description = unicode(timeline).encode('utf8')
                if timeline.state == State.BUSY: # warning
                    logger.warning('Skipped: %s', description)
                else:
                    user_id = timeline.user_id
                    job = q.enqueue_call(func=process, args=(user_id,), 
                        description=description, result_ttl=RESULT_TTL) # job_id=unicode(user_id), result_ttl=0
                    timeline.state = State.BUSY
                    session.commit()
                    logger.info('Queued: %s', description)
    except:
        session.rollback()
        raise
    finally:
        session.close()
        logger.debug("End enqueue")
