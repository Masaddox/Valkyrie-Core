import itertools


def xor(string, key):
    result = ""
    for string_char, key_char in zip(string, itertools.cycle(key)):
        result += chr(ord(string_char) ^ ord(key_char))
    return result
