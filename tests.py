from mallard import Mallard
from content.dictionaries import BASIC_REPLIES_DICT, RANDOM_RESPONCES_DICT, RANDOM_STICKERS

mallard = Mallard()


def basic_reply_is_valid(reply, keyword, desired_dict=BASIC_REPLIES_DICT):
    reply, is_sticker = reply
    return reply is not None and reply in desired_dict[keyword.upper()]


def test_basic_answers():
    assert basic_reply_is_valid(mallard.process('ква'), 'КВА')
    assert basic_reply_is_valid(mallard.process('КвА'), 'КВА')
    assert basic_reply_is_valid(mallard.process('квашеная капуста'), 'КВА')

    double_rep = mallard.process('кряква')
    assert basic_reply_is_valid(double_rep, 'КВА') or basic_reply_is_valid(double_rep, 'КРЯ')

    double_rep = mallard.process('квакря')
    assert basic_reply_is_valid(double_rep, 'КВА') or basic_reply_is_valid(double_rep, 'КРЯ')

    assert mallard.process('абоба')[0] is None
    assert mallard.process('к в а')[0] is None

def test_random_answers():
    cnt = 0
    for i in range(5000):
        resp, is_sticker = mallard.process("aboba")
        if resp is not None:
            assert (is_sticker is not True and resp in RANDOM_RESPONCES_DICT) or (
                        is_sticker and resp in RANDOM_STICKERS)
            cnt += 1
    assert 0 < cnt < 50
