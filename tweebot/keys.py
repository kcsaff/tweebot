import json
from tweepy import OAuthHandler


CONSUMER_KEY = "CONSUMER_KEY"
CONSUMER_SECRET = "CONSUMER_SECRET"
ACCESS_KEY = "ACCESS_KEY"
ACCESS_SECRET = "ACCESS_SECRET"


class TwitterKeys(object):
    """
    Reads / holds keys required for the standard Twitter developer API
    """
    REQUIRED_KEYS = (CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)

    @classmethod
    def of(cls, obj):
        if isinstance(obj, cls):
            return obj
        else:
            return cls(obj)

    def __init__(self, keys_filename: str):
        """
        Take the filename where you're storing your keys (since you shouldn't do that here.)
        This is just a file that looks like:

                CONSUMER_KEY: dsafsafafsd
                CONSUMER_SECRET: iuhbfusdfiu44
                ACCESS_KEY: vjhbv99889
                ACCESS_SECRET: ivfjslfiguhg98

        (Or the equivalent in JSON)
        """
        self.__auth = None
        if keys_filename is None:
            raise RuntimeError('No twitter keys registered, pipeline stopping')
        with open(keys_filename, 'r') as f:
            data = f.read().strip()
        if data.startswith('{'):
            self.__dict__.update({
                '_'.join(key.strip().upper().split()): value.strip()
                for key, value in json.loads(data).items()
            })
        else:
            for line in data.splitlines(False):
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    self.__dict__[
                        '_'.join(key.strip().strip('{}",').strip().upper().split())
                    ] = value.strip().strip('{}",').strip()

        missing = 0
        for key in self.REQUIRED_KEYS:
            if key not in self.__dict__:
                print('Missing required key: {}'.format(key))
                missing += 1

        if missing:
            raise RuntimeError('I do not have all required keys')

    @property
    def auth(self):
        if self.__auth is None:
            self.__auth = OAuthHandler(self.CONSUMER_KEY, self.CONSUMER_SECRET)
            self.__auth.set_access_token(self.ACCESS_KEY, self.ACCESS_SECRET)
        return self.__auth

