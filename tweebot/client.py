import imghdr
import io
import subprocess
import os.path
import tweepy
from tweebot.console import Console
from tweebot.keys import TwitterKeys


TWITTER_FILESIZE_LIMIT = 2999000 # About 3 Meg, we round down


TWITTER_FILESIZE_LIMIT = 2999000 # About 3 Meg, we round down
NEW_FILESIZE_LIMIT = '1999kb'
OUT_FILENAME = 'out.png'
JPG_FILENAME = 'out{}.jpg'


class TwitterClient(object):
    def __init__(self, keys, console=None):
        self.__keys = TwitterKeys.of(keys)
        self.__console = Console.of(console)
        self.__api = None

    @property
    def api(self):
        if self.__api is None:
            auth = tweepy.OAuthHandler(self.__keys.CONSUMER_KEY, self.__keys.CONSUMER_SECRET)
            auth.set_access_token(self.__keys.ACCESS_KEY, self.__keys.ACCESS_SECRET)
            self.__api = tweepy.API(auth)
        return self.__api

    def autofollow(self, follow: bool = True, unfollow: bool = True):
        if not (follow or unfollow):
            return
        followers = set(tweepy.Cursor(self.twitter.followers_ids).items())
        friends = set(tweepy.Cursor(self.twitter.friends_ids).items())
        print(followers)
        print(friends)

        if follow:
            followed = followers - friends
            print('Need to follow: {}'.format(followed))
        else:
            followed = set()

        if unfollow:
            unfollowed = friends - followers
            print('Need to unfollow: {}'.format(unfollowed))
        else:
            unfollowed = set()

        for user_id in followed:
            self.twitter.create_friendship(user_id)

        for user_id in unfollowed:
            self.twitter.destroy_friendship(user_id)

        return followed, unfollowed

    def tweet(self,
              status: str = None,
              filename: str = None,
              image: bytes = None
      ):
        """Tweet a status update with, optionally, an image.

        :param status: Status string to tweet.
        :param filename: Filename of an image to tweet.
        :param bytes: Bytes of an image to tweet, may use instead of filename.
        :return: None
        """
        if status is None and self.default_status is not None:
            status = self.default_status() if callable(self.default_status) else self.default_status

        if not self.args or not self.args.keys:
            if self.verbose > 0:
                print('No twitter keys registered, pipeline stopping')
            return

        if status:
            kwargs = dict(status=status)
        else:
            kwargs = dict()

        if image:
            if not filename:
                filename = 'tweet.{}'.format(imghdr.what(None, h=image))
            kwargs.update(file=io.BytesIO(image))
            with self.__console.timed(
                    'Updating twitter status ({}kb)...'.format(os.path.getsize(filename) // 1024),
                    'Updated status in {0:.3f}s'
            ):
                self.twitter.update_with_media(filename, **kwargs)
        elif filename:
            filename = self._resize(filename)

            with self.__console.timed(
                'Updating twitter status ({}kb)...'.format(os.path.getsize(filename) // 1024),
                'Updated status in {0:.3f}s'
            ):
                self.twitter.update_with_media(filename, **kwargs)
        elif status:
            self.twitter.update_status(**kwargs)
        else:
            raise RuntimeError('Tweet requires status or filename')

    def _convert(self, filename, outname=OUT_FILENAME):
        if filename == outname:
            return outname

        if not self.args or not self.args.magick:
            raise RuntimeError('No ImageMagick handler registered & it\'s required to convert! Pipeline stopping')

        with self.__console.timed('Converting image...', 'Converted image in {0:.3f}s'):
            call_args = [
                self.args.magick, filename, outname
            ]
            subprocess.check_call(call_args)

        return outname

    def _resize(self, filename):
        if not self.args or not self.args.magick:
            raise RuntimeError('No ImageMagick handler registered & it\'s required to resize! Pipeline stopping')

        file_size = os.path.getsize(filename)

        attempt = 0
        while file_size > TWITTER_FILESIZE_LIMIT and attempt < 5:
            with self.__console.timed('Needs more jpeg...', 'Resized image in {0:.3f}s'):
                new_filename = JPG_FILENAME.format(attempt)
                call_args = [
                    self.args.magick, filename,
                    '-define', 'jpeg:extent={}'.format(NEW_FILESIZE_LIMIT),
                ]
                if attempt > 0:
                    call_args.extend(['-scale', '70%'])
                call_args.append(new_filename)
                subprocess.check_call(call_args)
                filename = new_filename
                file_size = os.path.getsize(filename)

        return filename
