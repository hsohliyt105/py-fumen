# -*- coding: utf-8 -*-

import re

ORIGINAL_TABLE = "0123456789QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm@*_+-./"

def escape(string: str):
    result = ""
    for char in string:
        if char in ORIGINAL_TABLE:
            result += char

        else:
            char_index = ord(char)
            
            if char_index < 16**2:
                result += "%" + str(hex(char_index))[2:].upper()

            else:
                result += "%u" + str(hex(char_index))[2:].upper()

    return result

def unescape(string: str):
    result = re.sub(r'%u([a-fA-F0-9]{4})|%([a-fA-F0-9]{2})', parse, string)

    return result

def parse(hex_string: re.Match):
    hex_4, hex_2 = hex_string.groups()
    string = hex_4 if hex_4 is not None else hex_2
    return chr(int(string, 16))