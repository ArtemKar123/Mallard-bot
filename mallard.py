import random

import typing

from content.dictionaries import BASIC_REPLIES_DICT, RANDOM_RESPONCES_LIST, EXCEPTIONS_DICT, TEXT_KEYWORDS, \
    CREATURES_LIST
from responses import *
import hashlib
import datetime


class Mallard:
    """
    Replies to stuff.
    """

    def __init__(self, random_answer_rate=200):
        self.RANDOM_ANSWER_RATE = random_answer_rate
        pass

    def get_creature(self, ):
        return random.choice(CREATURES_LIST)

    def process(self, saying: str) -> typing.Tuple[typing.Union[str, None], typing.Union[ResponseType, None]]:
        """
        :param saying:

        :return: reply, is_sticker
        """
        if len(saying) == 0:
            return None, None
        if (reply := self.check_basic_saying_based_on_dict(saying, basic_dict=BASIC_REPLIES_DICT)) is not None:
            return reply
        if (reply := self.generate_random_answer()) is not None:
            return reply
        return None, None

    @staticmethod
    def check_basic_saying_based_on_dict(saying: str, basic_dict, keywords=TEXT_KEYWORDS, ):
        """
        Checks if saying has some basic words to reply (like "ква").
        :param saying:
        """
        saying = saying.upper()
        found_keywords = []
        for keyword in keywords.keys():
            if (upper := keyword.upper()) in saying and len(basic_dict[keywords[keyword]]) > 0:
                found_keywords.append(upper)

        for i in range(len(found_keywords)):
            if found_keywords[i] not in EXCEPTIONS_DICT:
                continue
            for exception in EXCEPTIONS_DICT[found_keywords[i]]:
                if exception.upper() in saying:
                    found_keywords.remove(found_keywords[i])
                    break

        if (l := len(found_keywords)) > 0:
            chosen_keyword = keywords[found_keywords[random.randint(0, l - 1)]]
            ret = basic_dict[chosen_keyword][random.randint(0, len(basic_dict[chosen_keyword]) - 1)]
            return ret.text, ret.type
        return None

    def generate_random_answer(self):
        """
        says random stuff
        :return:
        """
        if random.randrange(self.RANDOM_ANSWER_RATE) != 0:
            return None

        ret = random.choice(RANDOM_RESPONCES_LIST)
        return ret.text, ret.type
