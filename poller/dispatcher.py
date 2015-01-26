"""
Poller dispatcher.
"""
import config
import logging, logging.config, yaml
logging.config.dictConfig(yaml.load(config.LOGGING))
logger = logging.getLogger(__name__)

import time
from twitter import queue


def dispatch():
    "Polling timelines periodically."
    while True:
        queue.enqueue()
        logger.info('Sleeping')
        time.sleep(queue.FREQUENCY)
