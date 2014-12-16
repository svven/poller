"""
Poller dispatcher.
"""
import time
from twitter import queue


def dispatch():
    "Polling timelines periodically."
    while True:
        queue.enqueue()
        print '%s Sleeping' % time.strftime('%X')
        time.sleep(queue.FREQUENCY)
