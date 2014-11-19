"""
Polling Twitter timelines.
"""
from .. import db
from models import User, Token, Timeline


class BaseTimeline(object):
    """
    Polling generic timeline.
    """
    def __init__(self, timeline):
        self.token = None
        self.timeline = timeline

    def get_token(self):
        pass

    def poll(self):
        pass


class UserTimeline(BaseTimeline):
    pass


class HomeTimeline(BaseTimeline):
    pass