# -*- coding: utf-8 -*-

class FieldConstants():
    GARBAGE_LINE = 1
    WIDTH = 10
    HEIGHT = 23
    PLAY_BLOCKS = WIDTH * HEIGHT
    MAX_HEIGHT = HEIGHT + GARBAGE_LINE
    MAX_BLOCKS = MAX_HEIGHT * WIDTH

PREFIX = "v"
VERSION = "115"
SUFFIX = "@"
VERSION_INFO = PREFIX + VERSION + SUFFIX