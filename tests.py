from mallard import Mallard
from content.dictionaries import BASIC_REPLIES_DICT, DENIAL_REPLIES_DICT

mallard = Mallard()


def basic_reply_is_valid(reply: str, keyword, desired_dict=BASIC_REPLIES_DICT):
    return reply is not None and reply in desired_dict[keyword.upper()]


def test_basic_answers():
    assert basic_reply_is_valid(mallard.process('ква'), 'КВА')
    assert basic_reply_is_valid(mallard.process('КвА'), 'КВА')
    assert basic_reply_is_valid(mallard.process('квашеная капуста'), 'КВА')

    double_rep = mallard.process('кряква')
    assert basic_reply_is_valid(double_rep, 'КВА') or basic_reply_is_valid(double_rep, 'КРЯ')

    double_rep = mallard.process('квакря')
    assert basic_reply_is_valid(double_rep, 'КВА') or basic_reply_is_valid(double_rep, 'КРЯ')

    assert mallard.process('абоба') is None
    assert mallard.process('к в а') is None


def test_basic_order():
    assert basic_reply_is_valid(mallard.process('ква миу'), 'КВА')
    assert basic_reply_is_valid(mallard.process('миуква'), 'КВА')


def test_denial_answers():
    assert basic_reply_is_valid(mallard.process('миу'), 'МИУ', DENIAL_REPLIES_DICT)
    assert basic_reply_is_valid(mallard.process('миУ'), 'МИУ', DENIAL_REPLIES_DICT)
    assert mallard.process('миy') is None
