# -*- coding: utf-8 -*-

from math import floor

COMMENT_TABLE = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'
MAX_COMMENT_CHAR_VALUE = len(COMMENT_TABLE) + 1

class CommentParser():
    def decode(v: int) -> str:
        string = ''
        value = v
        for count in range (4):
            index = value % MAX_COMMENT_CHAR_VALUE
            string += COMMENT_TABLE[index]
            value = floor(value / MAX_COMMENT_CHAR_VALUE)

        return string

    def encode(ch: str, count: int) -> int:
        return COMMENT_TABLE.index(ch) * (MAX_COMMENT_CHAR_VALUE ** count)