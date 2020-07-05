import imghdr
import io
import subprocess
import os.path
import tweepy
from tweebot.cardclient import CardClient
from tweebot.console import Console
from tweebot.keys import TwitterKeys


TWITTER_FILESIZE_LIMIT = 2999000  # About 3 Meg, we round down


TWITTER_FILESIZE_LIMIT = 2999000  # About 3 Meg, we round down
NEW_FILESIZE_LIMIT = '1999kb'
OUT_FILENAME = 'out.png'
JPG_FILENAME = 'out{}.jpg'


TWEET_LENGTH = 280


class TwitterClient(object):
    CHOICE_BEGIN = '* '

    def __init__(self, keys, console=None, headers=None):
        self.__console = Console.of(console)
        self.__keys = TwitterKeys.of(keys)
        self.__card_api = CardClient(headers)
        self.__api = None

    @property
    def api(self) -> tweepy.API:
        """
        Direct access to the internal tweepy API.
        :return: Tweepy API object.
        """
        if self.__api is None:
            self.__api = tweepy.API(self.__keys.auth)
            me = self.__api.me()
            self.__console.okay(f'Connected to twitter as @{me.screen_name}: "{me.name}"')
        return self.__api

    def autofollow(self, follow: bool = True, unfollow: bool = True):
        """
        Attempt to follow new followers and/or unfollow unfollowers.

        Current limitations: only fetches the first page of users, about 50, and may be a bit
        unpredictable past that point.

        :param follow: Set to follow new followers (default True)
        :param unfollow: Set to unfollow new unfollowers (default True)
        :return:
        """
        if not (follow or unfollow):
            return (), ()
        followers = set(tweepy.Cursor(self.api.followers_ids).items())
        friends = set(tweepy.Cursor(self.api.friends_ids).items())
        self.__console[2].info(followers)
        self.__console[2].info(friends)

        if follow:
            followed = followers - friends
            self.__console[1].info('Need to follow: {}'.format(followed))
        else:
            followed = set()

        if unfollow:
            unfollowed = friends - followers
            self.__console[1].info('Need to unfollow: {}'.format(unfollowed))
        else:
            unfollowed = set()

        for user_id in followed:
            self.api.create_friendship(user_id)
            self.__console.okay(f'Followed {user_id}')

        for user_id in unfollowed:
            self.api.destroy_friendship(user_id)
            self.__console.okay(f'Unfollowed {user_id}')

        return followed, unfollowed

    def tweet(self,
              status: str = None,
              filename: str = None,
              image: bytes = None):
        """Tweet a status update with, optionally, an image.

        :param status: Status string to tweet.
        :param filename: Filename of an image to tweet.
        :param image: Bytes of an image to tweet, may use instead of filename.
        :return: None
        """
        if status is None and self.default_status is not None:
            status = self.default_status() if callable(self.default_status) else self.default_status

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
                result = self.api.update_with_media(filename, **kwargs)
        elif filename:
            filename = self._resize(filename)

            with self.__console.timed(
                'Updating twitter status ({}kb)...'.format(os.path.getsize(filename) // 1024),
                'Updated status in {0:.3f}s'
            ):
                result = self.api.update_with_media(filename, **kwargs)
        elif status:
            result = self.api.update_status(**kwargs)
        else:
            raise RuntimeError('Tweet requires status or filename')

        self.__print_tweet_result(result)
        return result

    def poll(self, status: str, *choices: str):
        if not choices:
            status, choices = self.find_choices(status)
        choices = [choice.strip()[:25] for choice in choices][:4]
        if not choices:
            raise RuntimeError('No poll options provided!')
        status = status[:TWEET_LENGTH]
        card_uri = self.__card_api.create_poll(*choices)
        result = self.api.update_status(status=status, card_uri=card_uri)
        self.__print_tweet_result(result)

    def __print_tweet_result(self, result):
        if result is not None:
            self.__console.okay(f'Posted tweet #{result.id_str}: "{result.text}"')
            self.__console.okay(f'https://twitter.com/{result.user.screen_name}/status/{result.id_str}')

    def _convert(self, filename: str, outname: str=OUT_FILENAME) -> str:
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

    def _resize(self, filename: str) -> str:
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

    def find_choices(self, text: str):
        lines = text.strip().splitlines(True)
        choices = []
        others = []
        for line in reversed(lines):
            if line.startswith(self.CHOICE_BEGIN) and not others:
                choices.append(line[len(self.CHOICE_BEGIN):].strip())
            else:
                others.append(line)
        text = ''.join(reversed(others)).strip()
        choices = reversed(choices)
        return text, choices
