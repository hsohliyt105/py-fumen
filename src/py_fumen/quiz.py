# -*- coding: utf-8 -*-

from __future__ import annotations
from enum import Enum
from typing import List, Optional
from re import search

from .defines import parse_piece, parse_piece_name, Piece

class Operation(Enum):
    DIRECT = 'direct'
    SWAP = 'swap'
    STOCK = 'stock'

class Quiz():
    quiz: str
    
    @staticmethod
    def trim(quiz: str) -> str:
        return quiz.strip()

    class PieceException(Exception):
        pass

    @staticmethod
    def __verify(quiz: str) -> str:
        replaced = Quiz.trim(quiz)

        if len(replaced) == 0 or quiz == '#Q=[]()' or not quiz.startswith('#Q='):
            return quiz

        if not(search("^#Q=\[[TIOSZJL]?]\([TIOSZJL]?\)[TIOSZJL]*?.*$", replaced)):
            raise Quiz.PieceException(f"Current piece doesn't exist, however next pieces exist: {quiz}")

        return replaced

    def __init__(self, quiz: str):
        self.quiz = self.__verify(quiz)

    def next(self) -> str:
        index = self.quiz.index(')') + 1
        name = self.quiz[index:]

        if name is None or name == '':
            return ''

        return name

    @staticmethod
    def is_quiz_comment(comment: str) -> bool:
        return comment.startswith('#Q=')

    @staticmethod
    def create(nexts: str) -> Quiz:
        return Quiz(f"#Q=[]({nexts[0]}){nexts[1:]}")

    @staticmethod
    def create(hold: str, nexts: str) -> Quiz:        
        return Quiz(f"#Q=[{hold}]({nexts[0]}){nexts[1:]}")

    def least(self) -> str:
        index = self.quiz.index(')')
        return self.quiz[index+1:]

    def current(self) -> str:
        index = self.quiz.index('(') + 1
        name = self.quiz[index]
        if name == ')':
            return ''

        return name

    def hold(self) -> str:
        index = self.quiz.index('[') + 1
        name = self.quiz[index]
        if name == ']':
            return ''

        return name

    def least_after_next2(self) -> str:
        index = self.quiz.index(')')
        if self.quiz[index+1] == '':
            return self.quiz[index+1:]

        return self.quiz.substr[index+2:]

    class HoldException(Exception):
        pass

    def get_operation(self, used: Piece) -> Operation:
        used_name = parse_piece_name(used)
        current = self.current()
        if used_name == current:
            return Operation.DIRECT

        hold = self.hold()
        if used_name == hold:
            return Operation.SWAP
        
        if hold == '':
            if used_name == self.next():
                return Operation.STOCK

        else:
            if current == '' and used_name == self.next():
                return Operation.DIRECT

        raise self.HoldException(f"Unexpected hold piece in quiz: {self.quiz}")

    def least_in_active_bag(self) -> str:
        separate_index = self.quiz.index(';')
        quiz = self.quiz[0, separate_index] if 0 <= separate_index else self.quiz
        index = quiz.indexOf(')')
        if quiz[index+1] == ';':
            return quiz[index+1:]

        return quiz.substr[index+2:]

    def direct(self) -> Quiz:
        if self.current() == '':
            least = self.least_after_next2()
            return Quiz(f"#Q=[{self.hold()}]({least[0]}){least[1:]}")

        return Quiz("#Q=[{self.hold}](${self.next()})${self.leastAfterNext2()}")

    def swap(self) -> Quiz:
        if self.hold() == '':
            raise self.HoldException(f"Cannot find hold piece: {self.quiz}")

        next = self.next()
        return Quiz(f"#Q=[${self.current()}]({next})${self.leastAfterNext2()}")

    class StockException(Exception):
        pass

    def stock(self) -> Quiz:
        if self.hold() != '' or self.next() == '':
             raise self.StockException(f"Cannot stock: {self.quiz}")

        least = self.leastAfterNext2()
        head = least[0] if least[0] is not None else ''

        if 1 < len(least):
            return Quiz(f"#Q=[{self.current()}]({head}){least[1:]}")

        return Quiz(f"#Q=[{self.current()}]({head})")

    class OperationException(Exception):
        pass

    def operate(self, operation: Operation) -> Quiz:
        if operation is Operation.DIRECT:
            return self.direct()
        if operation is  Operation.SWAP:
            return self.swap()
        if operation is  Operation.STOCK:
            return self.stock()
        
        raise self.OperationException('Unexpected operation')

    def can_operate(self) -> bool:
        quiz = self.quiz
        if quiz.startswith('#Q=[]()'):
            quiz = self.quiz[8:]

        return quiz.startswith('#Q=') and quiz != '#Q=[]()'

    def get_hold_piece(self) -> Piece:
        if not self.can_operate():
            return Piece.EMPTY

        name = self.hold()
        if name is None or name == '' or name == ';':
            return Piece.EMPTY
        
        return parse_piece(name)

    def get_next_pieces(self, maximum: Optional[int] = None) -> List[Piece]:
        if not self.can_operate():
            return [Piece.EMPTY] * maximum if maximum is not None else []
        

        names = self.current() + self.next() + self.least_in_active_bag()[0, maximum]
        if maximum is not None and len(names) < maximum:
            names += ' ' * (maximum - len(names))

        return [Piece.EMPTY if name is None or name == ' ' or name == '' else parse_piece_name(name) for name in [*names]]

    def to_string(self) -> str:
        return self.quiz

    def next_if_end(self) -> Quiz:
        if self.quiz.startswith('#Q=[]()'):
            return Quiz(self.quiz[8:])

        return self

    def format(self) -> Quiz:
        quiz = self.next_if_end()
        if quiz.quiz == '#Q=[]()':
            return Quiz('')

        current = quiz.current()
        hold = quiz.hold()

        if current == '' and hold != '':
            return Quiz(f"#Q=[]({hold}){quiz.least()}")

        if current == '':
            least = quiz.least()
            head = least[0]
            if head is None:
                return Quiz('')

            if head == '':
                return Quiz(least[1:])

            return Quiz(f"#Q=[]({head}){least[1:]}")

        return quiz
