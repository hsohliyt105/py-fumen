# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import List, Optional, Tuple
from math import floor
from urllib.parse import unquote

from .inner_field import InnerField
from .field import Field, Mino, Operation, create_inner_field

@dataclass
class Flags():
    lock: Optional[bool] = True
    mirror: Optional[bool] = False
    colorize: Optional[bool] = True
    rise: Optional[bool] = False
    quiz: Optional[bool] = False

@dataclass
class Refs():
    field: Optional[int] = None
    comment: Optional[int] = None

class Page():
    index: Optional[int]
    __field: Optional[InnerField]
    operation: Optional[Operation]
    comment: Optional[str]
    flag: Optional[Flags]
    refs: Optional[Refs]

    def __init__(self, index: Optional[int] = None, field: Optional[InnerField] = None, operation: Optional[Operation] = None, comment: Optional[str] = None, flags: Optional[Flags] = None, refs: Optional[Refs] = None):
        self.index = index
        self.__field = field.copy()
        self.operation = operation
        self.comment = comment
        self.flags = flags
        self.refs = refs

        return

    def get_field(self) -> Field:
        return Field(self.__field.copy())

    def set_field(self, field: Field):
        self.__field = create_inner_field(field)

    def mino(self) -> Mino:
        return Mino.minoFrom(self.operation)