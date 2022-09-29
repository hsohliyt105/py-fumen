# -*- coding: utf-8 -*-

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .inner_field import get_block_xys, InnerField, PlayField
from .defines import parse_piece, parse_piece_name, parse_rotation
from .constants import FieldConstants

@dataclass
class Operation():
    piece_type: str
    rotation: str
    x: int
    y: int

@dataclass
class XY():
    x: int
    y: int

@dataclass
class Mino():
    piece_type: str
    rotation: str
    x: int
    y: int

    @staticmethod
    def mino_from(operation: Operation) -> Mino:
        return Mino(operation.piece_type, operation.rotation, operation.x, operation.y)

    @staticmethod
    def get_sort_xy(xy: XY) -> Tuple[int, int]:
        return xy.y, xy.x

    def positions(self) -> List[XY]:
        return get_block_xys(parse_piece(self.piece_type), parse_rotation(self.rotation), self.x, self.y).sort(key=self.get_sort_xy)

    def operation(self) -> Operation:
        return Operation(self.piece_type, self.rotation, self.x, self.y)

    def isValid(self) -> bool:
        try:
            parse_piece(self.piece_type)
            parse_rotation(self.rotation)

        except Exception as e:
            return False

        return all(0 <= position.x and position.x < 10 and 0 <= position.y and position.y < 23 for position in self.positions())

    def copy(self) -> Mino:
        return Mino(self.piece_type, self.rotation, self.x, self.y)

def to_mino(operation_or_mino: Operation | Mino) -> Mino:
    return operation_or_mino.copy() if operation_or_mino is Mino else Mino.mino_from(operation_or_mino)

class Field():
    __field: InnerField

    def __init__(self, field: InnerField):
        self.__field = field

    @staticmethod
    def create(field: Optional[str], garbage: Optional[str]) -> Field:
        return Field(InnerField(field=PlayField.load(field) if field is not None else None, garbage=PlayField.load_minify(garbage) if garbage is not None else None))

    def can_fill(self, operation: Optional[Operation | Mino]) -> bool:
        if operation is None:
            return True

        mino = to_mino(operation)
        return self.__field.can_fill_all(mino.positions())

    def can_lock(self, operation: Optional[Operation | Mino]) -> bool:
        if operation is None:
            return True

        if not self.can_fill(operation):
            return False

        # Check on the ground
        return not self.can_fill(Operation(operation.piece_type, operation.rotation, operation.x, operation.y-1))

    class FillException(Exception):
        pass

    def fill(self, operation: Optional[Operation | Mino], force: bool = False) -> Optional[Mino]:
        if operation is None:
            return None

        mino = to_mino(operation)

        if not (force or self.can_fill(mino)):
            raise self.FillException('Cannot fill piece on field')

        self.__field.fill_all(mino.positions(), parse_piece(mino.type))

        return mino

    class PutException(Exception):
        pass

    def put(self, operation: Optional[Operation | Mino]) -> Optional[Mino]:
        if operation is None:
            return None

        mino = to_mino(operation)

        while 0 <= mino.y:
            if not self.can_lock(mino):
                continue

            mino.y -= 1

            self.fill(mino)

            return mino

        raise self.PutException('Cannot put piece on field')

    def clear_line(self):
        self.__field.clear_line()

    def at(self, x: int, y: int) -> str:
        return parse_piece_name(self.__field.get_number_at(x, y))

    def set(self, x: int, y: int, type: str):
        self.__field.set_number_at(x, y, parse_piece(type))

    def copy(self) -> Field:
        return Field(self.__field.copy())

    @dataclass
    class Option():
        reduced: Optional[bool] = None
        separator: Optional[str] = None
        garbage: Optional[bool] = None

    def string(self, option: Option = Option()) -> str:
        skip = option.reduced if option.reduced is not None else True
        separator = option.separator if option.separator is not None else '\n'
        min_y = -1 if option.garbage is None or option.garbage else 0

        output = ''

        for y in range (22, min_y - 1, -1):
            line = ''
            for x in range(10):
                line += self.at(x, y)

            if skip and line == '__________':
                continue

            skip = False
            output += line
            if y != min_y:
                output += separator

        return output

def create_new_inner_field() -> InnerField:
    return InnerField()

def create_inner_field(field: Field) -> InnerField:
    inner_field = InnerField()
    for y in range(-1, FieldConstants.HEIGHT):
        for x in range(0,  FieldConstants.WIDTH):
            at = field.at(x, y)
            inner_field.set_number_at(x, y, parse_piece(at))

    return inner_field