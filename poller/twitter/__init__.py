"""
Poller package for Twitter data.
"""
from .. import config, db, r

from database.models import Token
get_default_token = lambda: \
    Token.query.filter_by(user_id=config.TWITTER_DEFAULT_TOKEN).one()
