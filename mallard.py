import random
from content.dictionaries import BASIC_REPLIES_DICT


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
        if (reply := self.check_simple_sayings(saying)) is not None:
            return reply

    def check_simple_sayings(self, saying: str):
        """
        Checks if saying has some basic words to reply (like "ква").
        :param saying:
        """
        saying = saying.upper()
        found_keywords = []
        for keyword in BASIC_REPLIES_DICT.keys():
            if (upper := keyword.upper()) in saying and len(BASIC_REPLIES_DICT[keyword]) > 0:
                found_keywords.append(upper)

        if (l := len(found_keywords)) > 0:
            chosen_keyword = found_keywords[random.randint(0, l - 1)]
            return BASIC_REPLIES_DICT[chosen_keyword][random.randint(0, len(BASIC_REPLIES_DICT[chosen_keyword]) - 1)]
        return None
