# -*- coding: utf-8 -*-

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from math import floor
from copy import deepcopy

from .defines import InnerOperation, parse_piece, Piece, Rotation
from .constants import FieldConstants

class PieceException(Exception):
    pass

class RotationException(Exception):
    pass

def get_pieces(piece: Piece) -> List[List[int]]:
    if piece is Piece.I:
        return [[0, 0], [-1, 0], [1, 0], [2, 0]]
    if piece is Piece.T:
        return [[0, 0], [-1, 0], [1, 0], [0, 1]]
    if piece is Piece.O:
        return [[0, 0], [1, 0], [0, 1], [1, 1]]
    if piece is Piece.L:
        return [[0, 0], [-1, 0], [1, 0], [1, 1]]
    if piece is Piece.J:
        return [[0, 0], [-1, 0], [1, 0], [-1, 1]]
    if piece is Piece.S:
        return [[0, 0], [-1, 0], [0, 1], [1, 1]]
    if piece is Piece.Z:
        return [[0, 0], [1, 0], [0, 1], [-1, 1]]

    raise PieceException('Unsupported piece')

def rotate_right(positions: List[List[int]]) -> List[List[int]]:
    return [[current[1], -current[0]] for current in positions]

def rotate_left(positions: List[List[int]]) -> List[List[int]]:
    return [[-current[1], current[0]] for current in positions]

def rotate_reverse(positions: List[List[int]]) -> List[List[int]]:
    return [[-current[0], -current[1]] for current in positions]

def get_blocks(piece: Piece, rotation: Rotation) -> List[List[int]]:
    blocks = get_pieces(piece)
    if rotation is Rotation.SPAWN:
        return blocks
    if rotation is Rotation.LEFT:
        return rotate_left(blocks)
    if rotation is Rotation.REVERSE:
        return rotate_reverse(blocks)
    if rotation is Rotation.RIGHT:
        return rotate_right(blocks)

    raise RotationException('Unsupported rotation')

def get_block_positions(piece: Piece, rotation: Rotation, x: int, y: int) -> List[List[int]]:
    return [[position[0]+x, position[1]+y] for position in get_blocks(piece, rotation)]

@dataclass
class XY():
    x: int
    y: int

def get_block_xys(piece: Piece, rotation: Rotation, x: int, y: int) -> List[XY]:
    return [XY(position[0]+x, position[1]+y) for position in get_blocks(piece, rotation)]

class PlayField():
    __pieces: List[Piece]
    __length: int

    def __init__(self, pieces: List[Piece] = None, length: int = FieldConstants.PLAY_BLOCKS):
        if pieces is not None:
            self.__pieces = pieces
        else:
            self.__pieces = [Piece.EMPTY for i in range(length)]
        
        self.__length = length

    def get(self, x: int, y: int) -> Piece:
        return self.__pieces[x + y * FieldConstants.WIDTH]

    def add_offset(self, x: int, y: int, value: int):
        self.__pieces[x + y * FieldConstants.WIDTH] = Piece(self.__pieces[x + y * FieldConstants.WIDTH].value+value)
        return

    def set_at(self, index: int, piece: Piece):
        self.__pieces[index] = piece
        return

    def set(self, x: int, y: int, piece: Piece):
        self.set_at(x + y * FieldConstants.WIDTH, piece)

    class BlockCountException(Exception):
        pass

    @staticmethod
    def load_inner(blocks: str, length: Optional[int] = None) -> PlayField:
        inner_len = length if length is not None else len(blocks)
        if inner_len % 10 != 0: 
            raise PlayField.BlockCountException('Num of blocks in field should be mod 10')

        field = PlayField(length=length) if length is not None else PlayField()

        for index in range(inner_len):
            block = blocks[index]
            field.set(index % 10, floor((inner_len - index - 1) / 10), parse_piece(block))

        return field
    
    @staticmethod
    def load(lines: List[str]) -> PlayField:
        blocks = ''.join(lines).strip()
        return PlayField.load_inner(blocks)
    
    @staticmethod
    def load_minify(lines: List[str]) -> PlayField:
        blocks = ''.join(lines).strip()
        return PlayField.load_inner(blocks, len(blocks))

    def fill(self, operation: InnerOperation):
        blocks = get_blocks(operation.piece_type, operation.rotation)
        for block in blocks:
            nx, ny = operation.x + block[0], operation.y + block[1]
            self.set(nx, ny, operation.piece_type)

    def fill_all(self, positions: List[XY], piece_type: Piece):
        for xy in positions:
            self.set(xy.x, xy.y, piece_type)

    def clear_line(self):
        new_field = deepcopy(self.__pieces)
        top = int(len(self.__pieces) / FieldConstants.WIDTH - 1)

        for y in range(top, -1, -1):
            line = self.__pieces[y * FieldConstants.WIDTH : (y + 1) * FieldConstants.WIDTH]
            is_filled = Piece.EMPTY not in line
            if is_filled:
                bottom = new_field[0:y * FieldConstants.WIDTH]
                over = new_field[(y + 1) * FieldConstants.WIDTH:]
                new_field = bottom + over + ([Piece.EMPTY] * FieldConstants.WIDTH)

        self.__pieces = new_field

    def up(self, block_up: PlayField):
        self.__pieces = (block_up.__pieces + (self.__pieces))[0:self.__length]

    def mirror(self):
        new_field: List[Piece] = []
        for y in range(len(self.__pieces)):
            line = self.__pieces[y * FieldConstants.WIDTH : (y + 1) * FieldConstants.WIDTH]
            line.reverse()
            for obj in line:
                new_field.append(obj)

        self.__pieces = new_field

    def shift_to_left(self):
        height = int(self.__pieces.length / 10)
        for y in range(height):
            for x in range(FieldConstants.WIDTH - 1):
                self.__pieces[x + y * FieldConstants.WIDTH] = self.__pieces[x + 1 + y * FieldConstants.WIDTH]
            self.__pieces[9 + y * FieldConstants.WIDTH] = Piece.EMPTY

    def shift_to_right(self):
        height = self.__pieces.length / 10
        for y in range(height):
            for x in range(FieldConstants.WIDTH - 1, -1, -1):
                self.__pieces[x + y * FieldConstants.WIDTH] = self.__pieces[x - 1 + y * FieldConstants.WIDTH]

            self.__pieces[y * FieldConstants.WIDTH] = Piece.EMPTY

    def shift_to_up(self):
        blanks = [Piece.EMPTY] * FieldConstants.WIDTH
        self.__pieces = (blanks + self.__pieces)[0 : self.__length]

    def shift_to_bottom(self):
        blanks = [Piece.EMPTY] * FieldConstants.WIDTH
        self.__pieces = self.__pieces[10:self.__length] + blanks

    def to_array(self) -> List[Piece]:
        return deepcopy(self.__pieces)

    def num_of_blocks(self) -> int:
        return len(self.__pieces)

    def copy(self) -> PlayField:
        return PlayField(pieces = deepcopy(self.__pieces), length = self.__length)

    def to_shallow_array(self) -> List[Piece]:
        return self.__pieces

    def clear_all(self):
        self.__pieces = [Piece.EMPTY] * len(self.__pieces)

    def equals(self, other: PlayField) -> bool:
        if len(self.__pieces) != len(other.__pieces):
            return False

        for index in range(len(self.__pieces)):
            if self.__pieces[index] != other.__pieces[index]:
                return False

        return True

class InnerField():
    __field: PlayField
    __garbage: PlayField

    @staticmethod
    def __create(length: int) -> PlayField:
        return PlayField(length=length)

    def __init__(self, field: Optional[PlayField] = None, garbage: Optional[PlayField] = None):
        if field is None:
            field = self.__create(FieldConstants.PLAY_BLOCKS)
        if garbage is None:
            garbage = self.__create(FieldConstants.WIDTH)
        self.__field = field
        self.__garbage = garbage

    def fill(self, operation: InnerOperation):
        self.__field.fill(operation)

    def fill_all(self, positions: List[XY], type: Piece):
        self.__field.fill_all(positions, type)

    def can_fill(self, piece: Piece, rotation: Rotation, x: int, y: int) -> bool:
        positions = get_block_positions(piece, rotation, x, y)

        return all(0 <= px and px < 10 and 0 <= py and py < FieldConstants.HEIGHT and self.get_number_at(px, py) is Piece.EMPTY for px, py in positions)

    def can_fill_all(self, positions: List[XY]) -> bool:
        return all(0 <= position.x and position.x < 10 and 0 <= position.y and position.y < FieldConstants.HEIGHT and self.get_number_at(position.x, position.y) is Piece.EMPTY for position in positions)

    def is_on_ground(self, piece: Piece, rotation: Rotation, x: int, y: int):
        return not self.can_fill(piece, rotation, x, y - 1)

    def clear_line(self):
        self.__field.clear_line()

    def rise_garbage(self):
        self.__field.up(self.__garbage)
        self.__garbage.clear_all()

    def mirror(self):
        self.__field.mirror()

    def shift_to_left(self):
        self.__field.shift_to_left()

    def shift_to_right(self):
        self.__field.shift_to_right()

    def shift_to_up(self):
        self.__field.shift_to_up()

    def shift_to_bottom(self):
        self.__field.shift_to_bottom()

    def copy(self) -> InnerField:
        return InnerField(field=self.__field.copy(), garbage=self.__garbage.copy())

    def equals(self, other: InnerField) -> bool:
        return self.__field.equals(other.field) and self.__garbage.equals(other.garbage)

    def add_number(self, x: int, y: int, value: int):
        if 0 <= y:
            self.__field.add_offset(x, y, value)
        else:
            self.__garbage.add_offset(x, -(y + 1), value)

    def set_number_field_at(self, index: int, value: int):
        self.__field.set_at(index, value)

    def set_number_garbage_at(self, index: int, value: int):
        self.__garbage.set_at(index, value)

    def set_number_at(self, x: int, y: int, value: int):
        self.__field.set(x, y, value) if 0 <= y else self.__garbage.set(x, -(y + 1), value)

    def get_number_at(self, x: int, y: int) -> Piece:
        return self.__field.get(x, y) if 0 <= y else self.__garbage.get(x, -(y + 1))

    def get_number_at_index(self, index: int, is_field: bool) -> Piece:
        if is_field:
            return self.get_number_at(index % 10, floor(index / 10))
        return self.get_number_at(index % 10, -(floor(index / 10) + 1))

    def to_field_number_array(self) -> List[Piece]:
        return self.__field.to_array()

    def to_garbage_number_array(self) -> List[Piece]:
        return self.__garbage.to_array()