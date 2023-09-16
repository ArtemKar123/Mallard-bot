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
    'ТЯВ': ['ТЯВТЯВ'],
    'МУМ': ['ЕМУМ'],
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
    TYAV = 13
    MUM = 14
    KUM = 15
    CRY = 16
    AWOOO = 17
    STOP = 18


TEXT_KEYWORDS = {
    'КВА': Keyword.KVA,
    'КАР': Keyword.KAR,
    'КРЯ': Keyword.KRYA,
    'ХРЮ': Keyword.HRYU,
    'МИУ': Keyword.MIU,
    'МАВ': Keyword.MAV,
    'ГАИНЬГ': Keyword.GAING,
    'ЧМОК': Keyword.KISS,
    'МЫЫЫ': Keyword.US,
    'МЫМЫ': Keyword.US,
    'ФТОО': Keyword.WHAT,
    'ФТОФТО': Keyword.WHAT,
    'ЧИВОО': Keyword.WHAT,
    'ARCH': Keyword.ARCH,
    'АРЧ': Keyword.ARCH,
    'ТЯВ': Keyword.WOOF,
    'ГАВ': Keyword.WOOF,
    'ТЯВТЯВ': Keyword.TYAV,
    'МУМ': Keyword.MUM,
    'КУМ': Keyword.KUM,
    'ХНЫ': Keyword.CRY,
    'АВУУУУ': Keyword.AWOOO,
    'ПРЕКРАТИТЬ': Keyword.STOP,
}

combined_text_replies = {
    Keyword.KVA: ['ква', 'ква!', 'ква-ква', 'ква)', 'ква\U0001F60C'],
    Keyword.KAR: ['кар', 'кар!', 'кар-кар', 'кар)', 'кар\U0001F60C'],
    Keyword.KRYA: ['кря', 'кря!', 'кря-кря', 'кря)', 'кря\U0001F60C'],
    Keyword.HRYU: ['хрю', 'хрюк', 'хрю-хрю'],
    Keyword.WOOF: ['тяв', 'тяв\U0001F60C', 'тяв-тяв'],
    Keyword.MIU: ['миy\U0001F60C'],
    Keyword.MAV: ['мав\U0001F60C'],
    Keyword.GAING: ['скр пяу гаиньг', 'скр пяу', 'гаиньг', 'ало русский рэп?'],
    Keyword.KISS: ['чмок', 'ты мне нравишься!!!', 'чмок\U0001F970'],
    Keyword.US: ['МЫЫЫЫЫЫЫЫЫЫ\U0001F970', 'МЫМЫМЫМЫ\U0001F970'],
    Keyword.WHAT: ['фтоооооо', 'чивоооооо', 'читоооооо'],
}
combined_sticker_replies = {
    Keyword.KVA: [
        'CAACAgIAAxkBAAIESWM1aZ9RdG-lmZp1s6G43v0AAWkz9wACaxEAAoQoUUjd6i8SNVbr1SoE',  # Frog with wine
        'CAACAgQAAxkBAAIEiWM1dv6UlBwAAakXetRKlhnhymykfwACawAD8YWLBHZImbEd8HQ_KgQ',  # Kermit hearts
        'CAACAgQAAxkBAAIEi2M1d3bG7EYGTY7qYCzWRQI-0xEqAAIiAQACqCEhBsMhKQ89A7XmKgQ',  # Dancing Apu
    ],
    Keyword.KRYA: [
        'CAACAgIAAxkBAAIER2M1aUsxYHmoj3SHqYn-X5mvCF98AAJqHQACYzEZSHXmSO3qgEwmKgQ',  # Spinning mallard
        'CAACAgIAAxkBAAIF-WObMH_7uR5FLesxAq6mLbTXgtcZAAL2AANWnb0K99tOIUA-pYosBA',  # Evil Duck
        'CAACAgIAAxkBAAIF_GObMIpWbfQUrqTOwEszPdmL14uTAAIJAQACVp29CtZmXIPXP6gdLAQ',  # Snow Duck
        'CAACAgIAAxkBAAIF_2ObMJTxuaUT2odpn6I13qe0ZFBnAAILAQACVp29Ck6x56YI--1JLAQ',  # Exploding Duck
    ],
    Keyword.MIU: [
        'CAACAgIAAxkBAAIElWM1eNbip3RITb16zOxw-wJDobgXAAIiEAACV2HJS1e96adku96ZKgQ',  # Cat jumps to you
        'CAACAgIAAxkBAAIEl2M1eN3VUarEYilDZ81I1IDILRcqAAI6FAACh9vJS7eEtmgl-WtUKgQ',  # Cat runs to you
    ],
    Keyword.MAV: [
        'CAACAgIAAxkBAAIElWM1eNbip3RITb16zOxw-wJDobgXAAIiEAACV2HJS1e96adku96ZKgQ',  # Cat jumps to you
        'CAACAgIAAxkBAAIEl2M1eN3VUarEYilDZ81I1IDILRcqAAI6FAACh9vJS7eEtmgl-WtUKgQ',  # Cat runs to you
    ],
    Keyword.WOOF: [
        'CAACAgIAAxkBAAI5vmOfEDYHgMiG9S5Gx4TKGTGF9mT9AALHLwACeIv4SEdXNRvd2S1SLAQ', # tax 1
        'CAACAgIAAxkBAAI5v2OfEDdh1Ocm8I6DdVGR-mm-qASWAAJ1IwACi5H4SH5HSf9EkicCLAQ', # tax 2
        'CAACAgIAAxkBAAI5wGOfEDfkM_gSvLpw5bNcpVdamKPjAAKYKAACgBz5SGvBWQcrxBnfLAQ', # tax 3
        'CAACAgIAAxkBAAI5wWOfEDgTSHy3vI8O_vURd34kfeAGAALsIgAC_lcAAUkD28bbNUrhISwE', # tax 4
        'CAACAgIAAxkBAAI5wmOfEDhXnlh2b8W9vyyqAAF13e0vCgACHiIAAq-d-UjzvXUoB6uYECwE', # tax 5
        'CAACAgIAAxkBAAI7nWOhYJEd8ZXuAAGHURhFvoPJxXal-QACGSAAAmHeEElmhbbxu-s_ECwE', # tax 6
        'CAACAgIAAxkBAAJk_2Qm0_56hGhTyAui8R5Bj3v1R4NtAAKXEwACqh6RSuc3arlfq1eXLwQ', # genshin 1
        'CAACAgIAAxkBAAJlAAFkJtQHi4gTGrzHB4f4mb85K_aMVAAChBIAAkxemEpTvqrozD5KdS8E', # genshin 2
        'CAACAgIAAxkBAAJlAWQm1B4Z6Xb06_mDsjVFe7l-G9NmAALnJwAC3xBRSYCQ-QNYUywRLwQ', # genshin 3
        'CAACAgIAAxkBAAJlAmQm1CernsAEzcBjntqkm5o_4P0EAAL3FgACxBKRSrU-68TdX4muLwQ', # genshin 4
    ],
    Keyword.TYAV: [
        'CAACAgUAAxkBAAJBdGUFfFivpX8NdwvTNdKzlTiHu3WJAAJIDAACQ-EpVbdNQTRI9ZdGMAQ', # genshin 1
        'CAACAgUAAxkBAAJBdmUFfGdMreyczm3GLzFCoGeDpmWZAAJECAACBXQoVQJEfF50Cn4SMAQ', # genshin 2
        'CAACAgIAAxkBAAJBeGUFfIQDytt-GkPaKKosq0fcy6HgAAL3FgACxBKRSrU-68TdX4muMAQ', # genshin 3
        'CAACAgUAAxkBAAJBcmUFfD2wbilsYL9otbX-KupwUnFuAAKoDAACgE0oVbcumpOFqJywMAQ', # genshin 4
        'CAACAgIAAxkBAAJBamUFe-OS0eogm6Q9SSHniKn5UNleAAKZNQACWv3ISnLIkUTOxbnjMAQ', # genshin 5
        'CAACAgIAAxkBAAJBbmUFfApNINhwnui19Zo7oR8T7LVxAALyLgAC7iPISpBoaFHx3-r_MAQ', # genshin 6
        'CAACAgUAAxkBAAJBcGUFfCl-wEK5ZZryJGY1akxzx4kjAAJkCgACvEIpVaJhoGKEuO_mMAQ', # genshin 7
    ],
    Keyword.AWOOO: [
        'CAACAgUAAxkBAAJBcGUFfCl-wEK5ZZryJGY1akxzx4kjAAJkCgACvEIpVaJhoGKEuO_mMAQ', # awooo
    ],
    Keyword.MUM: [
        'CAACAgIAAxkBAAJBlGUFfjdnwP9fMR0jvlUIbkinvQFPAAIyMAACSEPJSv18FlPudtmnMAQ', # MUM 1
        'CAACAgIAAxkBAAJBlmUFfkSszywITGEChHQLah3z_6ArAALsMgACSAzISqR7envspMgjMAQ', # MUM 2
        'CAACAgIAAxkBAAJBmGUFflMhYS-JZX-Uju6kL_6LsQ2kAAJtMwAC0CHJSmvz6yBgitNMMAQ', # MUM 3
        'CAACAgIAAxkBAAJBmmUFfmJH0SfX9FbuOwu2mA-CqPiJAALZMgAC_PTJSpnSIdOT7EndMAQ', # MUM 4
        'CAACAgIAAxkBAAJBnGUFfnHM7HatPDRtgxhBN_BMHa3bAALbLgACpqXIStLnXzlqxgHzMAQ', # MUM 5
        'CAACAgIAAxkBAAJBnmUFfpbLUCI1Z31okHHbhOPULbPnAALWLQAC1LDISvaxtxC4I4_7MAQ', # MUM 6
        'CAACAgIAAxkBAAJBkmUFfh2IW8K-4OPUN35S63rwO3YXAAIpMgACJnPISxrsjZAKWDA1MAQ', # MUM 7
    ],
    Keyword.KUM: [
        'CAACAgUAAxkBAAJBgmUFfOPbux40BJczFQSSpwcg-vwEAAKkCAAC9rs4VfJP3LJxMlHxMAQ', # kum
        'CAACAgUAAxkBAAJBgmUFfOPbux40BJczFQSSpwcg-vwEAAKkCAAC9rs4VfJP3LJxMlHxMAQ', # kum
        'CAACAgUAAxkBAAJBgmUFfOPbux40BJczFQSSpwcg-vwEAAKkCAAC9rs4VfJP3LJxMlHxMAQ', # kum
        'CAACAgUAAxkBAAJBgmUFfOPbux40BJczFQSSpwcg-vwEAAKkCAAC9rs4VfJP3LJxMlHxMAQ', # kum
        'CAACAgUAAxkBAAJBgmUFfOPbux40BJczFQSSpwcg-vwEAAKkCAAC9rs4VfJP3LJxMlHxMAQ', # kum
        'CAACAgIAAxkBAAJBhGUFfQG_lN4N5BwqlfwkZdLtE-S-AAL7NQACjKngS6qJ-6cyR8hzMAQ', # cooom
    ],
    Keyword.CRY: [
        'CAACAgUAAxkBAAJBiGUFfXKeuZ-cSB-MFCergbbEkUxqAALNCgACzqUpVQ7rlE3JhSUdMAQ', # genshin 1
        'CAACAgUAAxkBAAJBimUFfYadq0k2IxZIOtwtUdf_pgXPAAI2GAACCNApVbohev8pWVlYMAQ', # genshin 2
        'CAACAgUAAxkBAAJBjGUFfZ5fJPzDhYfJ9THWnhqG7aoFAAJtCgACLqUpVUWJN3-GQxp3MAQ', # genshin 3
        'CAACAgIAAxkBAAJBjmUFfbbZBC2bfgX9YKkveHrngaI2AALiMAACPlrJSlo1TJFjIEhQMAQ', # genshin 4
        'CAACAgIAAxkBAAJBkGUFfcMVLGmRUbc8YoHqvY7-XzdIAAJMMAACPKnJSiTf7_Uoy5B7MAQ', # genshin 5
    ],
    Keyword.STOP: [
        'CAACAgIAAxkBAAJBhmUFfRRnDIK1E9B8ytqe9G0CX7aHAAICEwACjV-RSvCl1POaUSO5MAQ', # stop the huynya
    ],
    Keyword.KISS: [
        'CAACAgIAAxkBAAIES2M1cN1wtBwRBVJUrc41Q8IqUpdRAALbIQACh2hISahd3FVgrVqvKgQ',  # Kissing sticker
        'CAACAgIAAxkBAAIEk2M1eL_ZB1rJK_YU3kPSepBCvIjPAAKfFQACXVnIS0QNrXBbo2y5KgQ',  # Cat kisses you
    ],
    Keyword.ARCH: [
        'CAACAgIAAxkBAAILu2NIDKKE4m9XSO6rZsFurosK4O4yAAJ2IAACIutBSpGemvhk_ISKKgQ',  # KhB arch sticker
    ],
    Keyword.US: [
        'CAACAgIAAxkBAAIFR2NIKRInpx4s4nZlKXaXFAJPikHyAAK8IwACSIZISahn5qW-aEGrKgQ',  # Hearts face
        'CAACAgIAAxkBAAIFSGNIKRvYzrUHB7ymrb-2XrATv8lzAALbIQACh2hISahd3FVgrVqvKgQ',  # Kiss
        'CAACAgIAAxkBAAIFSWNIKSTf0R73OxeQHRrMaSuwSzHRAAJZIgAC7tFJSQF3F2uCltD_KgQ',  # Cat us
    ],
    Keyword.WHAT: [
        'CAACAgIAAxkBAAIF42NO3T-ikTjWnaIKw4NXp3qlE7e_AALnIAACnBRISUlZeonw23gyKgQ',
        'CAACAgIAAxkBAAIF5GNO3URR4d7GRGkiPjPZxlpNIS3UAAK_FQACcPWhSzBi-XEOAbBAKgQ',
        'CAACAgIAAxkBAAIF_2ObMJTxuaUT2odpn6I13qe0ZFBnAAILAQACVp29Ck6x56YI--1JLAQ',  # Exploding Duck
    ],
}

basic_voice_replies = {
    Keyword.HRYU: ['hryak', 'hryak2', 'hryak3'],
    Keyword.MIU: ['purring1', 'purring2'],
    Keyword.MAV: ['purring1', 'purring2'],
    Keyword.US: ['us'],
    Keyword.GAING: ['gaing']
}

random_responses_text_list = [
    'очень умный',
    'этот человек прав во всём', 'у тебя красивые глаза', 'ты милашка', 'ты отправляешься в Бразилию', 'напиши в лс',
    'ты мне нравишься', 'сделай дз', 'может быть ты и не прав, но я все равно тебя поддержу', 'идейно',
    'все будет хорошо, не переживай', 'я знаю, что тебе нужна поддержка, поэтому я здесь\u2764\uFE0f️',
    'другие тоже могут ошибаться, не злись на них', 'выпей чаю с печеньками', 'ляг спать сегодня пораньше',
    'твоя красота неописуема', 'твой интеллект поражает'
]

# Don't care about readability lol.
# Use @idstickerbot to get sticker id.
random_responses_sticker_list = [
    'CAACAgIAAxkBAAEFBu9ipzuFG-20sV5OsUY4_hi5rJ18gAAC6RMAAuPsyUmr2ECISdqixiQE',
    'CAACAgIAAxkBAAEFBvNipzxf-63InNz8z0z_008NtJfLnAACbRgAAidlUUsdYl5S0stX3CQE',
    'CAACAgIAAxkBAAEFBvFipzxcQfLts3PjuWFbILGHmb_C0gAC0hYAAsFiEUnTxi3655QiryQE',
    'CAACAgIAAxkBAAEFBvVipzxh0njUgH15X4R9YINTk29ZdAACfyYAAglGKUmYCpp8HdAu_iQE',
    'CAACAgIAAxkBAAEFBvdipzxjTmbUT3R8VgK4ob7NAZOFOgACVRYAAmcMAUmsUhPTHzF5jyQE',
    'CAACAgIAAxkBAAEFBvlipzxrwNXzkvbQIyfT5rGCei2j8wACaxEAAoQoUUjd6i8SNVbr1SQE',
    'CAACAgIAAxkBAAEFBvtipzyjmJhpvn-uy8-mT6kfg933PQACbRQAAvh48Ev_35tLbqKxRyQE',
    'CAACAgIAAxkBAAEFBv1ipzylTIkGlWmCbCpuZZvFzKZBeQACewAD98zUGO4bzlUFJLDEJAQ',
    'CAACAgIAAxkBAAEFBv9ipzy6tbC_PLclcKaCRaMdeHdvkwAC-xQAAlp-iUgIYSgt4y85eyQE',
    'CAACAgIAAxkBAAEFBwFipz0IlP1KOq1tmW1Vy4q7XOC2IgACkygAAhGBkUrzg2u5NfjyRyQE',
   # 'CAACAgIAAxkBAAID6WMH4dKBcpmIl_dBAWaxm0yEsRmyAAISGQACrcYYSE_oIr7KN-mmKQQ',#
   # 'CAACAgIAAxkBAAID6mMH4dOy-c0LvTJEYYR3U5FjdPzsAAJ0GgACmwUZSOuvkMV9VT8YKQQ',#
   # 'CAACAgIAAxkBAAID62MH4dTXA5YsctmZlVUu3YM-gDikAAJGHAACPT4ZSKODGsM_nvvnKQQ',#
   # 'CAACAgIAAxkBAAID7GMH4diNKWofKaJMBbFohO7z5di7AAJ-HQACL6kgSN4Hywr1O8dXKQQ',#
   # 'CAACAgIAAxkBAAID7WMH4dvqg2m10EyBwXddhXc-1b4tAAIGHwAC-IIZSGxrn7WAl1D2KQQ',#
   # 'CAACAgIAAxkBAAID7mMH4d4pFa6aX3uX9Jq02y42rXfhAAJ6HQAC6VYhSIMXOJAX7sKkKQQ',#
   # 'CAACAgIAAxkBAAID72MH4d8wJ8C1AyLG_0OCcfPStsZiAALnHQACA7woSCTavYd7l5r_KQQ',#
   # 'CAACAgIAAxkBAAID8GMH4d9_Rp46uGXN85mt-uPRNhBaAAL7IAACDo8gSGhCetlzmDBvKQQ',#
   # 'CAACAgIAAxkBAAID8WMH4eBkZrSXradn0MbZOhplzO6JAAJVHwACp3NASCCGtxiyz6VgKQQ',#
    'CAACAgIAAxkBAAIF-WObMH_7uR5FLesxAq6mLbTXgtcZAAL2AANWnb0K99tOIUA-pYosBA',  # Evil Duck
    'CAACAgIAAxkBAAIF_GObMIpWbfQUrqTOwEszPdmL14uTAAIJAQACVp29CtZmXIPXP6gdLAQ',  # Snow Duck
    'CAACAgIAAxkBAAIF_2ObMJTxuaUT2odpn6I13qe0ZFBnAAILAQACVp29Ck6x56YI--1JLAQ',  # Exploding Duck
    'CAACAgIAAxkBAAI5wWOfEDgTSHy3vI8O_vURd34kfeAGAALsIgAC_lcAAUkD28bbNUrhISwE',  #Dog
    'CAACAgIAAxkBAAJk_2Qm0_56hGhTyAui8R5Bj3v1R4NtAAKXEwACqh6RSuc3arlfq1eXLwQ',
    'CAACAgIAAxkBAAJlAAFkJtQHi4gTGrzHB4f4mb85K_aMVAAChBIAAkxemEpTvqrozD5KdS8E',
    'CAACAgIAAxkBAAJlAWQm1B4Z6Xb06_mDsjVFe7l-G9NmAALnJwAC3xBRSYCQ-QNYUywRLwQ',
    'CAACAgIAAxkBAAJlAmQm1CernsAEzcBjntqkm5o_4P0EAAL3FgACxBKRSrU-68TdX4muLwQ',
]

random_responses_voice_list = [
    'hryak',
    'hryak2',
    'hryak3',
    'us',
    'loud',
    'gaing',
    'purring1',
    'purring2',
    'valera'
]

CREATURES_LIST = [
    'Я жабка! Ква-ква!\U0001F438',
    'Я уточка! Кря-кря!\U0001F986',
    'Я котик! Миууууу!\U0001F408',
    'Я пёсик! Тяв-тяв!\U0001F436',
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
