# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import List, Optional, Tuple
from math import floor

from .page import Page, Flags, Refs
from .inner_field import InnerField
from .fumen_buffer import FumenBuffer
from .defines import is_mino_piece, parse_piece_name, parse_rotation_name, Piece
from .action import ActionDecoder
from .comments import CommentParser
from .quiz import Quiz
from .field import create_new_inner_field, Mino, Operation
from .constants import FieldConstants
from .js_escape import unescape

class VersionException(Exception):
    pass

def format_data(version: str, data: str) -> Tuple[str, str]:
    trim = data.strip().replace("?", "")
    return (version, trim)

def extract(string: str) -> Tuple[str, str]:
    data = string

    # url parameters
    param_index = data.find('&')
    if 0 <= param_index:
        data = data[0:param_index]
        
    for version in [ "115", "110" ]:
        for prefix in [ "v", "m", "d" ]:
            match = string.find(prefix+version)
            if match != -1:
                sub = data[match + 5:]
                return format_data(version, sub)

    raise VersionException("Unsupported fumen version")

def decode(fumen: str) -> List[Page]:
    version, data = extract(fumen)
    if version == "115":
        return inner_decode(data, 23)
    if version == "110":
        return inner_decode(data, 21)

    raise VersionException("Unsupported fumen version")

@dataclass
class RefIndex():
    comment: int
    field: int

@dataclass
class Store():
    repeat_count: int
    ref_index: RefIndex
    last_comment_text: str
    quiz: Optional[Quiz] = None

@dataclass
class FieldObj():
    changed: bool
    field: InnerField

@dataclass
class Comment():
    text: Optional[str] = None
    ref: Optional[int] = None

@dataclass
class PageField():
    ref: Optional[int] = None

def inner_decode(data: str, field_top: int) -> List[Page]:
    field_max_height = field_top + FieldConstants.GARBAGE_LINE
    num_field_blocks = field_max_height * FieldConstants.WIDTH

    fumen_buffer = FumenBuffer(data)

    page_index = 0
    prev_field = create_new_inner_field()

    store = Store(-1, RefIndex(0, 0), '', None)

    pages: List[Page] = []
    action_decoder = ActionDecoder(FieldConstants.WIDTH, field_top, FieldConstants.GARBAGE_LINE)

    while not fumen_buffer.is_empty():
        # Parse field
        current_field_obj = FieldObj(False, create_new_inner_field())

        if 0 < store.repeat_count:
            current_field_obj = FieldObj(False, prev_field)

            store.repeat_count -= 1

        else:
            result = FieldObj(True, prev_field.copy())
            index = 0
            while index < num_field_blocks:
                diff_block = fumen_buffer.poll(2)
                diff = floor(diff_block / num_field_blocks)

                num_of_blocks = diff_block % num_field_blocks

                if diff == 8 and num_of_blocks == num_field_blocks - 1:
                    result.changed = False

                for block in range(0, num_of_blocks + 1):
                    x = index % FieldConstants.WIDTH
                    y = field_top - floor(index / FieldConstants.WIDTH) - 1
                    result.field.add_number(x, y, diff - 8)
                    index += 1

            current_field_obj = result

            if not current_field_obj.changed:
                store.repeat_count = fumen_buffer.poll(1)

        # Parse action
        action_value = fumen_buffer.poll(3)

        action = action_decoder.decode(action_value)

        # Parse comment
        comment: Comment
        if action.comment:

            # when there is an update in the comment
            comment_values: List[int] = []
            comment_length = fumen_buffer.poll(2)

            for comment_counter in range(0, floor((comment_length + 3) / 4)):
                comment_value = fumen_buffer.poll(5)

                comment_values.append(comment_value)

            flatten: str = ''
            for value in comment_values:
                flatten += CommentParser.decode(value)

            #this is the problem. javascript escape vs python quote
            comment_text = unescape(flatten[0:comment_length])
            store.last_comment_text = comment_text
            comment = Comment(text=comment_text)
            store.ref_index.comment = page_index

            text = comment.text
            if Quiz.is_quiz_comment(text):
                try:
                    store.quiz = Quiz(text)
                except:
                    store.quiz = None
                
            else:
                store.quiz = None
            
        elif page_index == 0:
            # When there is no update in the comment but on the first page
            comment = Comment(text='')
        else:
            # when there is no update in the comment
            comment = Comment(text=store.quiz.format().to_string() if store.quiz is not None else None, ref=store.ref_index.comment)

        # Acquire the operation for Quiz and advance the Quiz at the beginning of the next page by one step
        quiz = False
        if store.quiz is not None:
            quiz = True

            if store.quiz.can_operate() and action.lock:
                if is_mino_piece(action.piece.piece_type):
                    try:
                        next_quiz = store.quiz.next_if_end()
                        operation = next_quiz.get_operation(action.piece.piece_type)
                        store.quiz = next_quiz.operate(operation)

                    except Exception as e:
                        # print(e)

                        # Not operate
                        store.quiz = store.quiz.format()

                else:
                    store.quiz = store.quiz.format()

        # process for data processing
        current_piece: Optional[Operation] = None

        if action.piece.piece_type is not Piece.EMPTY:
            current_piece = action.piece

        # page creation
        field: PageField
        if current_field_obj.changed or page_index == 0:
            # when there is a change in the field
            # When the field did not change, but it was the first page
            field = PageField()
            store.ref_index.field = page_index
        else:
            # when there is no change in the field
            field = PageField(ref=store.ref_index.field)

        pages.append(Page(
                          page_index,
                          current_field_obj.field,
                          Mino.mino_from(Operation(parse_piece_name(current_piece.piece_type),
                                                   parse_rotation_name(current_piece.rotation),
                                                   current_piece.x,
                                                   current_piece.y))
                                         if current_piece is not None else None,
                          comment.text if comment.text is not None else store.last_comment_text,
                          Flags(action.lock, action.mirror, action.colorize, action.rise, quiz),
                          Refs(field=field.ref, comment=comment.ref)
                          ))

        """ callback(
            currentFieldObj.field.copy()
            , currentPiece
            , store.quiz !== undefined ? store.quiz.format().toString() : store.lastCommentText,
            )
        """

        page_index += 1

        if action.lock:
            if is_mino_piece(action.piece.piece_type):
                current_field_obj.field.fill(action.piece)

            current_field_obj.field.clear_line()

            if action.rise:
                current_field_obj.field.rise_garbage()

            if action.mirror:
                current_field_obj.field.mirror()

        prev_field = current_field_obj.field

    return pages
