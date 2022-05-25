import random
from content.dictionaries import BASIC_REPLIES_DICT, DENIAL_REPLIES_DICT


class Mallard:
    """
    Replies to stuff.
    """

    def __init__(self):
        pass

    def process(self, saying: str):
        """
        :param saying:
        """
        if len(saying) == 0:
            return None
        if (reply := self.check_basic_saying_based_on_dict(saying, BASIC_REPLIES_DICT)) is not None:
            return reply
        if (reply := self.check_basic_saying_based_on_dict(saying, DENIAL_REPLIES_DICT)) is not None:
            return reply

    @staticmethod
    def check_basic_saying_based_on_dict(saying: str, basic_dict):
        """
        Checks if saying has some basic words to reply (like "ква").
        :param saying:
        """
        saying = saying.upper()
        found_keywords = []
        for keyword in basic_dict.keys():
            if (upper := keyword.upper()) in saying and len(basic_dict[keyword]) > 0:
                found_keywords.append(upper)

        if (l := len(found_keywords)) > 0:
            chosen_keyword = found_keywords[random.randint(0, l - 1)]
            return basic_dict[chosen_keyword][random.randint(0, len(basic_dict[chosen_keyword]) - 1)]
        return None
