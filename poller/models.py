"""
Models describing Twitter entities to be stored.
"""

from poller import db


class User(db.Model):
    """
    Twitter user that is tweeting links.
    """

    __tablename__ = 'twitter_users'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, nullable=False, unique=True)
    screen_name = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    profile_image_url = db.Column(db.String)
    friends_count = db.Column(db.Integer)
    followers_count = db.Column(db.Integer)

    def __repr__(self):
        return '<User: %r>' % self.screen_name


class Token(db.Model):
    """
    Twitter tokens used for polling.
    """

    __tablename__ = 'twitter_tokens'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, nullable=False, unique=True)
    key = db.Column(db.String, nullable=False)
    secret = db.Column(db.String, nullable=False)


class Timeline(db.Model):
    """
    Twitter timeline that is being polled.
    """
    
    __tablename__ = 'twitter_timelines'

    METHODS = (USER_TIMELINE, HOME_TIMELINE) = ('user', 'home')

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, nullable=False, unique=True)
    method = db.Column(db.Enum(*METHODS, name='timeline_method'), nullable=False)
    since_id = db.Column(db.BigInteger)
    prev_check = db.Column(db.DateTime(timezone=True))
    next_check = db.Column(db.DateTime(timezone=True))
    failures = db.Column(db.SmallInteger)
    frequency = db.Column(db.Integer)
    active = db.Column(db.Boolean)

