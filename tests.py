from mallard import Mallard

RANDOM_ANSWER_RATE = 100
mallard = Mallard(random_answer_rate=RANDOM_ANSWER_RATE)


def test_random_answers():
    N_TESTS = 5000
    cnt = 0
    for i in range(N_TESTS):
        resp, resp_type = mallard.process("aboba")
        if resp is not None:
            cnt += 1
    assert 0 < cnt < N_TESTS * 2 / RANDOM_ANSWER_RATE
