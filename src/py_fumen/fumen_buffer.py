# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List
from math import floor

ENCODE_TABLE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def decode_to_value(v: str) -> int:
    return ENCODE_TABLE.index(v)

def encode_from_value(index: int) -> str:
    return ENCODE_TABLE[index]

class FumenBuffer(object):
    table_length: int = len(ENCODE_TABLE)

    values: List[int]

    class FumenException(Exception):
        pass

    def __init__(self, data: str = "") -> None:
        try:
            self.values = [ENCODE_TABLE.index(char) for char in [*data]]

        except:
            raise self.FumenException('Unexpected fumen')

        return

    def poll(self, maximum: int) -> int:
        value = 0

        for count in range(maximum):
            v = self.values.pop(0)

            if v is None:
                raise self.FumenException('Unexpected fumen')

            value += v * self.table_length ** count

        return value

    def push(self, value: int, split_count: int = 1):
        current = value
        for count in range(split_count):
            self.values.append(current % FumenBuffer.table_length)
            current = floor(current / FumenBuffer.table_length)

        return

    def merge(self, post_buffer: FumenBuffer):
        for value in post_buffer.values:
            self.values.append(value)

        return

    def is_empty(self) -> bool:
        return len(self.values) == 0

    def length(self) -> int:
        return len(self.values)

    def get(self, index: int) -> int:
        return self.values[index]

    def set(self, index: int, value: int) -> None:
        self.values[index] = value
        return

    def to_string(self) -> str:
        return ''.join(map(encode_from_value, self.values))