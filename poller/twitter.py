"""
Tweepy wrapper using RateLimitHandler with multiple access tokens,
based on this fork https://github.com/svven/tweepy.
It also handles API method cursors and splits input param lists in 
chunks if neccessary.
"""

from tweepy import API, Cursor
from tweepy import RateLimitHandler
from tweepy.error import TweepError

from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKENS


class Twitter(object):
    "Tweepy wrapper class."

    def __init__(self, 
        consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, 
        access_tokens=ACCESS_TOKENS):
        """
        Initialize params for RateLimitHandler to pass to Tweepy API.
        Param `access_tokens` must be a dictionary but it can be loaded
        later just before the first API method call, and has to be like
        { user_id: (access_token_key, access_token_secret) }.
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_tokens = access_tokens

    _api = None

    def _get_api(self):
        "Initialize Tweepy API object with RateLimitHandler auth."
        auth = RateLimitHandler(self.consumer_key, self.consumer_secret)
        for key, secret in self.access_tokens.values():
            try:
                auth.add_access_token(key, secret)
            except Exception, e:
                print key, e
        print 'Token pool size: %d' % len(auth.tokens)
        return API(auth, retry_count=2, retry_delay=3,
            wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    @property
    def api(self):
        "Lazy loaded Tweepy API object."
        if not self._api:
            self._api = self._get_api()
        return self._api


    # Tweepy API methods
    def get_user(self, **kwargs):
        """
        https://dev.twitter.com/rest/reference/get/users/show
        http://docs.tweepy.org/en/latest/api.html#API.get_user
        Parameters: id|user_id|screen_name
        """
        return self.api.get_user(**kwargs)

    def lookup_users(self, **kwargs):
        """
        https://dev.twitter.com/rest/reference/get/users/lookup
        """
        param = ('user_ids' in kwargs and 'user_ids') or \
                ('screen_names' in kwargs and 'screen_names')
        items = ('user_ids' in kwargs and kwargs['user_ids']) or \
                ('screen_names' in kwargs and kwargs['screen_names'])
        assert param and items

        def chunks(l, n):
            for i in xrange(0, len(l), n):
                yield l[i:i+n]

        for items_chunk in chunks(items, 100): # 100 ids at a time
            chunk = self.api.lookup_users(**dict([(param, items_chunk)]))
            for u in chunk: yield u

    def user_timeline(self, user_id, since_id=None, max_id=None):
        """
        https://dev.twitter.com/rest/reference/get/statuses/user_timeline
        http://docs.tweepy.org/en/latest/api.html#API.user_timeline
        """
        for s in Cursor(self.api.user_timeline, 
            user_id=user_id, since_id=since_id, max_id=max_id).items():
            yield s

    def home_timeline(self, user_id, since_id=None, max_id=None):
        """
        https://dev.twitter.com/rest/reference/get/statuses/home_timeline
        http://docs.tweepy.org/en/latest/api.html#API.home_timeline
        """
        key, secret = self.access_tokens[user_id]
        self.api.auth.fixed_access_token = key
        try:
            for s in Cursor(self.api.home_timeline, 
                since_id=since_id, max_id=max_id).items():
                yield s
        finally:
            self.api.auth.fixed_access_token = None

    def friends_ids(self, user_id):
        """
        https://dev.twitter.com/rest/reference/get/friends/ids
        http://docs.tweepy.org/en/latest/api.html#API.friends_ids
        """
        for friends_ids_chunk in Cursor(self.api.friends_ids, user_id=user_id).pages():
            for f in friends_ids_chunk: yield f

    def followers_ids(self, user_id):
        """
        https://dev.twitter.com/rest/reference/get/followers/ids
        http://docs.tweepy.org/en/latest/api.html#API.followers_ids
        """
        for followers_ids_chunk in Cursor(self.api.followers_ids, user_id=user_id).pages():
            for f in followers_ids_chunk: yield f

    def update_status(self, user_id, status):
      """
      https://dev.twitter.com/rest/reference/post/statuses/update
      http://docs.tweepy.org/en/latest/api.html#API.update_status
      """
      key, secret = self.access_tokens[user_id]
      self.api.auth.fixed_access_token = key
      try:
          self.api.update_status(status)
      finally:
          self.api.auth.fixed_access_token = None
