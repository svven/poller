"""
Twitter models used by the poller.
"""
from . import db


class Tweeter(db.Model):
    "Twitter user that is tweeting links."

    __tablename__ = 'twitter_tweeters'

    id = db.Column(db.BigInteger, primary_key=True)
    tweeter_id = db.Column(db.BigInteger, nullable=False, unique=True)
    screen_name = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    profile_image_url = db.Column(db.String)
    protected = db.Column(db.Boolean)
    friends_count = db.Column(db.Integer)
    followers_count = db.Column(db.Integer)

    tweets = db.relationship('Tweet', backref='tweeter', lazy='dynamic')
    timeline = db.relationship('Timeline', backref='tweeter', uselist=False)
    token = db.relationship('Token', backref='tweeter', uselist=False)

    def __init__(self, user):
        "Param `user` is a Twitter API user."
        self.tweeter_id = user.id
        self.screen_name = user.screen_name
        self.name = user.name
        self.description = user.description
        self.profile_image_url = user.profile_image_url
        self.protected = user.protected
        self.friends_count = user.friends_count
        self.followers_count = user.followers_count

    def __repr__(self):
        return '<Tweeter (%s): @%s>' % (self.tweeter_id, self.screen_name)


class Token(db.Model):
    "Twitter API access token for user."

    __tablename__ = 'twitter_tokens'

    id = db.Column(db.BigInteger, primary_key=True)
    tweeter_id = db.Column(db.BigInteger, 
        db.ForeignKey('twitter_tweeters.tweeter_id'), nullable=False, unique=True)
    key = db.Column(db.String, nullable=False)
    secret = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<Token (%s): %s>' % (self.tweeter_id, self.key.split('-')[1])


class Timeline(db.Model):
    "Twitter timeline that is being polled."

    __tablename__ = 'twitter_timelines'

    # METHODS = (USER_TIMELINE, HOME_TIMELINE) = ('user', 'home')
    DEFAULT_FREQUENCY = 15 * 60 # 15 mins
    MIN_FREQUENCY = 2 * 60 # 2 mins
    MAX_FREQUENCY = 24 * 3600 # 1 day
    MAX_FAILURES = 3 # to keep enabled

    id = db.Column(db.BigInteger, primary_key=True)
    tweeter_id = db.Column(db.BigInteger, 
        db.ForeignKey('twitter_tweeters.tweeter_id'), nullable=False, unique=True)
    # method = db.Column(db.Enum(*METHODS, name='timeline_method'), nullable=False)
    since_id = db.Column(db.BigInteger)
    next_check = db.Column(db.DateTime, default=db.func.now())
    prev_check = db.Column(db.DateTime)
    frequency = db.Column(db.Integer, nullable=False, default=DEFAULT_FREQUENCY)
    failures = db.Column(db.SmallInteger, nullable=False, default=0)
    enabled = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return '<Timeline (%s): @%s>' % (self.tweeter_id, self.tweeter.screen_name)


class Tweet(db.Model):
    "Twitter status containing a link by tweeter."

    __tablename__ = 'twitter_tweets'

    id = db.Column(db.BigInteger, primary_key=True)
    status_id = db.Column(db.BigInteger, nullable=False, unique=True)
    tweeter_id = db.Column(db.BigInteger, 
        db.ForeignKey('twitter_tweeters.tweeter_id'), nullable=False)
    source_url = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    link_id = db.Column(db.String)
        # db.ForeignKey('news_links.link_id')
    processed = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, status):
        "Param `status` is a Twitter API status."
        self.status_id = status.id
        self.tweeter_id = status.user.id
        self.created_at = status.created_at

    def __repr__(self):
        return '<Tweet (%s): %s>' % (self.status_id, self.source_url)

