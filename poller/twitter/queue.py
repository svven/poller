"""
Poller Twitter queue.
"""
import logging
logger = logging.getLogger(__name__)

from . import config, db, r

from job import TimelineJob
from database.models import *

import datetime
from rq import Connection, Queue

QUEUE = config.POLLER_QUEUE
FREQUENCY = Timeline.MIN_FREQUENCY
RESULT_TTL = 1 * 60 # 1 min
TIMEOUT = 10 * 60 # 10 min

DEFAULT_TOKEN = config.TWITTER_DEFAULT_TOKEN
default_token = Token.query.filter_by(user_id=DEFAULT_TOKEN).one()

def process(user_id, list_id):
    "Process timeline of specified user or list."
    logger.debug("Start process")
    session = db.session()
    failed = False # yet
    timeline = session.query(Timeline).filter_by(user_id=user_id,
        list_id=list_id).one()
    user = session.query(TwitterUser).filter_by(user_id=user_id).one()
    users = [user]
    tokens = [user.token or default_token]
    try:
        job = TimelineJob(timeline, users, tokens)
        job.do(session)
        failed = job.failed # may be True
        log = failed and logger.warning or logger.info
        log("Proced %s: %s",
            unicode(timeline or user).encode('utf8'), job.result)
        return job.result
    except Exception, e:
        session.rollback()
        failed = True # obviously
        logger.error("Failed %s: %s", 
            unicode(timeline or user).encode('utf8'), repr(e))
        raise
    finally:
        if timeline:
            try:
                timeline = session.merge(timeline) # no need
                timeline.state = failed and State.FAIL or State.DONE
                session.commit()
            except:
                session.rollback()
        session.close()
        logger.debug("End process")

def enqueue(timelines=[]):
    "Enqueue timelines to process."
    now = datetime.datetime.utcnow()
    logger.debug("Start enqueue...")
    session = db.session()
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
                user_id, list_id = (timeline.user_id, timeline.list_id)
                job = q.enqueue_call(func=process, args=(user_id, list_id), 
                    description=description, result_ttl=RESULT_TTL, timeout=TIMEOUT) # job_id=unicode(user_id), result_ttl=0
                timeline.state = State.BUSY
                session.commit()
                logger.debug('Queued: %s', description)
    except:
        session.rollback()
        raise
    finally:
        session.close()
        logger.debug("End enqueue")
