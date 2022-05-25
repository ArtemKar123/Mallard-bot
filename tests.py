from mallard import Mallard
from content.dictionaries import BASIC_REPLIES_DICT


def basic_reply_is_valid(reply: str, keyword):
    return reply is not None and reply in BASIC_REPLIES_DICT[keyword.upper()]


def test_basic_answers():
    mallard = Mallard()

    assert basic_reply_is_valid(mallard.check_simple_sayings('ква'), 'КВА')
    assert basic_reply_is_valid(mallard.check_simple_sayings('КвА'), 'КВА')
    assert basic_reply_is_valid(mallard.check_simple_sayings('квашеная капуста'), 'КВА')

    double_rep = mallard.check_simple_sayings('кряква')
    assert basic_reply_is_valid(double_rep, 'КВА') or basic_reply_is_valid(double_rep, 'КРЯ')

    double_rep = mallard.check_simple_sayings('квакря')
    assert basic_reply_is_valid(double_rep, 'КВА') or basic_reply_is_valid(double_rep, 'КРЯ')

    assert mallard.check_simple_sayings('абоба') is None
    assert mallard.check_simple_sayings('к в а') is None
