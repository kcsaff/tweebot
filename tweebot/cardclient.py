from tweebot.console import Console
import requests
import json


class CardClient(object):
    """
    Reads / holds keys required for specialized Twitter developer API calls - currently just cards
    """

    def __init__(self, headers, console=None):
        self.__headers = headers
        self.__loaded_headers = None
        self.__console = Console.of(console)

    @property
    def headers(self):
        if self.__loaded_headers is None:
            self.__loaded_headers = self._read_headers(self.__headers)
        return self.__loaded_headers

    def create_card(self, card_data):
        card_result = requests.post('https://caps.twitter.com/v2/cards/create.json',
                                    headers=self.headers, data={'card_data': json.dumps(card_data)})

        try:
            card_uri = card_result.json()['card_uri']
        except:
            self.__console.print(card_result)
            self.__console.print(card_result.request)
            self.__console.print(card_result.request.headers)
            self.__console.print(card_result.request.body)
            self.__console.print(card_result.headers)
            self.__console.print(card_result.text)
            self.__console.print(card_result.json())
            raise
        else:
            return card_uri

    def create_poll(self, *choices):
        assert 2 <= len(choices) <= 4
        poll_json = {
            'twitter:api:api:endpoint': '1',
            'twitter:card': f'poll{len(choices)}choice_text_only',
            'twitter:long:duration_minutes': '60'
        }
        for i, choice in enumerate(choices, 1):
            poll_json[f'twitter:string:choice{i}_label'] = choice
        return self.create_card(poll_json)

    @staticmethod
    def _read_headers(headers_filename: str):
        if headers_filename is None:
            raise RuntimeError('No header file provided, stopping')
        result = {}
        with open(headers_filename, 'r') as f:
            data = f.read().strip()
            for line in data.splitlines(False):
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    result[key.strip()] = value.strip()
        return result
