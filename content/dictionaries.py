import typing
from responses import *
from enum import Enum

BASIC_REPLIES_DICT: typing.Dict[str, typing.List[Response]]
RANDOM_RESPONCES_LIST: typing.List[Response]


def generate_dictionary(target: typing.Dict, dictionary: typing.Dict, response_type: ResponseType):
    for key in dictionary.keys():
        if key not in target:
            target[key] = []
        for entry in dictionary[key]:
            target[key].append(Response(entry, response_type))


def generate_list(target: typing.List, dictionary: typing.List, response_type: ResponseType):
    for entry in dictionary:
        target.append(Response(entry, response_type))


EXCEPTIONS_DICT = {
    'КАР': ['КАРТ'],
}


class Keyword(Enum):
    KVA = 1
    KAR = 2
    KRYA = 3
    HRYU = 4
    MIU = 5
    MAV = 6
    GAING = 7
    KISS = 8
    US = 9
    WHAT = 10
    ARCH = 11,
    WOOF = 12


TEXT_KEYWORDS = {
    'КВА': Keyword.HRYU,
    'КАР': Keyword.HRYU,
    'КРЯ': Keyword.HRYU,
    'ХРЮ': Keyword.HRYU,
    'МИУ': Keyword.HRYU,
    'МАВ': Keyword.HRYU,
    'ГАИНЬГ': Keyword.HRYU,
    'ЧМОК': Keyword.HRYU,
    'МЫЫЫ': Keyword.HRYU,
    'МЫМЫ': Keyword.HRYU,
    'ФТОО': Keyword.HRYU,
    'ФТОФТО': Keyword.HRYU,
    'ЧИВОО': Keyword.HRYU,
    'ARCH': Keyword.HRYU,
    'АРЧ': Keyword.HRYU,
    'ТЯВ': Keyword.HRYU,
    'ГАВ': Keyword.HRYU,
}

combined_text_replies = {
    Keyword.HRYU: ['хрю', 'хрюк', 'хрю-хрю', 'хрюююю', 'хрюю хрю хрюююю!', 'хрююююю хрююююю хрююююю!'],
}
combined_sticker_replies = {
    Keyword.HRYU: [
        'CAACAgIAAxkDAAJTcWP-bvqLjCjxLL4ZrW8VSM4vtAfBAAL3JwACkcn4S2jiB1acghudLgQ',
        'CAACAgIAAxkDAAJTcmP-bw6pBLPQS-o2oyUCQRlqR7JRAAK1JwACNKX5S5bvnuL10NmnLgQ',
        'CAACAgIAAxkDAAJTc2P-bw-Up2YIMTuLh7rHnpn_KmyHAAKAIwACi7b4Sxgh31eg7mbTLgQ',
        'CAACAgIAAxkDAAJTdGP-bw8ncwLJm2mFbB7fpJSbmsZ8AAKCJAACr3X5S5LwVUIzZ0jpLgQ'
    ]
}

basic_voice_replies = {
    Keyword.HRYU: ['hryak', 'hryak2', 'hryak3'],
}

random_responses_text_list = [
    'хрюююю', 'хрюю хрю хрюююю!', 'хрююююю хрююююю хрююююю!', 'хрюхрюхрю', 'хрю-хрю хрююю хрю'
]

# Don't care about readability lol.
# Use @idstickerbot to get sticker id.
random_responses_sticker_list = [
    'CAACAgIAAxkDAAJTcWP-bvqLjCjxLL4ZrW8VSM4vtAfBAAL3JwACkcn4S2jiB1acghudLgQ',
    'CAACAgIAAxkDAAJTcmP-bw6pBLPQS-o2oyUCQRlqR7JRAAK1JwACNKX5S5bvnuL10NmnLgQ',
    'CAACAgIAAxkDAAJTc2P-bw-Up2YIMTuLh7rHnpn_KmyHAAKAIwACi7b4Sxgh31eg7mbTLgQ',
    'CAACAgIAAxkDAAJTdGP-bw8ncwLJm2mFbB7fpJSbmsZ8AAKCJAACr3X5S5LwVUIzZ0jpLgQ'
]

random_responses_voice_list = [
    'hryak',
    'hryak2',
    'hryak3',
]

CREATURES_LIST = [
    'Я хрюшка! Хрю-хрю!\U0001F437',
]

BASIC_REPLIES_DICT = {}
generate_dictionary(target=BASIC_REPLIES_DICT, dictionary=combined_text_replies, response_type=ResponseType.TEXT)
generate_dictionary(target=BASIC_REPLIES_DICT, dictionary=combined_sticker_replies, response_type=ResponseType.STICKER)
generate_dictionary(target=BASIC_REPLIES_DICT, dictionary=basic_voice_replies, response_type=ResponseType.VOICE)

RANDOM_RESPONCES_LIST = []
generate_list(target=RANDOM_RESPONCES_LIST, dictionary=random_responses_text_list,
              response_type=ResponseType.TEXT)
generate_list(target=RANDOM_RESPONCES_LIST, dictionary=random_responses_sticker_list,
              response_type=ResponseType.STICKER)
generate_list(target=RANDOM_RESPONCES_LIST, dictionary=random_responses_voice_list,
              response_type=ResponseType.VOICE)

if __name__ == '__main__':
    print(len(BASIC_REPLIES_DICT))
    print(len(RANDOM_RESPONCES_LIST))
