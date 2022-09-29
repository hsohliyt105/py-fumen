# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import Enum

class Piece(Enum):
    EMPTY = 0
    I = 1 # Illegal naming convention but just followed knewjade
    L = 2
    O = 3 # Same here
    Z = 4
    T = 5
    J = 6
    S = 7
    GRAY = 8

def is_mino_piece(piece: Piece):
    return piece is not Piece.EMPTY and piece is not Piece.GRAY

class PieceException(Exception):
    pass

def parse_piece_name(piece: Piece) -> str:
    if piece is Piece.I:
        return 'I'
    if piece is Piece.L:
        return 'L'
    if piece is Piece.O:
        return 'O'
    if piece is Piece.Z:
        return 'Z'
    if piece is Piece.T:
        return 'T'
    if piece is Piece.J:
        return 'J'
    if piece is Piece.S:
        return 'S'
    if piece is Piece.GRAY:
        return 'X'
    if piece is Piece.EMPTY:
        return '_'

    raise PieceException(f'Unknown piece: {repr(piece)}')

def parse_piece(piece: str) -> Piece:
    piece = piece.upper()
    if piece in Piece.__members__.keys():
        return Piece[piece]

    if piece == "X":
        return Piece.GRAY

    if piece == " " or piece == "_":
        return Piece.EMPTY

    raise PieceException(f'Unknown piece: {piece}')

class Rotation(Enum):
    SPAWN = 2
    RIGHT = 1
    REVERSE = 0
    LEFT = 3

class RotationException(Exception):
    pass

def parse_rotation_name(rotation: Rotation) -> str:
    if rotation is Rotation.SPAWN:
        return 'spawn'
    if rotation is Rotation.LEFT:
        return 'left'
    if rotation is Rotation.RIGHT:
        return 'right'
    if rotation is Rotation.REVERSE:
        return 'reverse'
    
    raise RotationException(f'Unknown rotation: {repr(rotation)}')

def parse_rotation(rotation: str) -> Rotation:
    rotation = rotation.lower()
    
    if rotation == 'spawn':
        return Rotation.SPAWN
    if rotation == 'left':
        return Rotation.LEFT
    if rotation == 'right':
        return Rotation.RIGHT
    if rotation == 'reverse':
        return Rotation.REVERSE

    raise RotationException(f'Unknown rotation: {rotation}')

@dataclass
class InnerOperation():
    piece_type: Piece
    rotation: Rotation
    x: int
    y: int