DEMON_TYPE_DICT = {
    0: 0,
    1: 3,
    2: 4,
    3: 0,
    4: 5,
    5: 6
}

DIFFICULTY_TYPE_DICT = {
    1: 1,
    2: 1,
    3: 2,
    4: 3,
    5: 3,
    6: 4,
    7: 4,
    8: 5,
    9: 5,
    10: 5
}


def demon_conv(demon_type):
    return DEMON_TYPE_DICT[int(demon_type)]


def diff_conv(diff_type):
    return DIFFICULTY_TYPE_DICT[int(diff_type)]
