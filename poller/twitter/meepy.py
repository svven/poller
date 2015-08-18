from datetime import datetime

class User(object):

    def __init__(self, user_id):
        self.id = user_id
        self.screen_name = user_id
        self.name = user_id
        self.description = 'Mock User'
        self.profile_image_url = ''
        self.protected = False
        self.friends_count = 0
        self.followers_count = 0

class Status(object):

    next_statusid = 1

    def __init__(self, url, user_id):
        # URL stuff
        self.url = url
        self.entities = dict()
        self.entities['urls'] = [dict(expanded_url=self.url)]

        # User stuff
        self.user = User(user_id)

        # Other
        # self.id = Status.next_statusid
        self.id = datetime.now().strftime("%Y%m%d%H%M%S")
        Status.next_statusid += 1
        self.created_at =datetime.now()



def url_list(n):
    return [('http://www.ne.url.com/' + str(i) + '/' + str(datetime.now().strftime("%Y%m%d%H%M%S"))) for i in range(1, n)]


class Twitter(object):

    def __init__(self, key, secret, tokens):
        print key,secret,tokens

    """
    Return a list of tweets which contain URLs
    """
    def home_timeline(self, user_id, since_id, count):
        print "1. In Mock home_timeline"
        return [(Status(url, user_id)) for url in url_list(5)]

    def user_timeline(self, user_id, count):
        print "2. In Mock user_timeline"
        return [(Status(url, user_id)) for url in url_list(5)]

    def list_timeline(self, user_id, since_id, count):
        print "3. In Mock list_timeline"
        return [(Status(url, user_id)) for url in url_list(5)]




