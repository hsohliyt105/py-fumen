# -*- coding: utf-8 -*-

from typing import List, Optional, Tuple
from urllib.parse import quote
from re import findall

from .page import Page, Flags
from .inner_field import InnerField
from .fumen_buffer import FumenBuffer
from .field import create_inner_field, create_new_inner_field, Field, Operation
from .defines import is_mino_piece, parse_piece, parse_rotation, Piece, Rotation, InnerOperation
from .action import ActionEncoder, Action
from .comments import CommentParser
from .quiz import Quiz
from .constants import FieldConstants, VERSION_INFO
from .js_escape import escape

# Calculate difference from previous field: 0 to 16
def get_diff(prev: InnerField, current: InnerField, x_index: int, y_index: int) -> int:
    y: int = FieldConstants.HEIGHT - y_index - 1
    return current.get_number_at(x_index, y).value - prev.get_number_at(x_index, y).value + 8

# data recording
def record_block_counts(fumen_buffer: FumenBuffer, diff: int, counter: int):
    value: int = diff * FieldConstants.MAX_BLOCKS + counter
    fumen_buffer.push(value, 2)

# encode the field
# Specify an empty field if there is no previous field
# The input field has a height of 23 and a width of 10
def encode_field(prev: InnerField, current: InnerField) -> Tuple[bool, FumenBuffer]:
    fumen_buffer = FumenBuffer()

    # Convert from field value to number of consecutive blocks
    changed = True
    prev_diff = get_diff(prev, current, 0, 0)
    counter = -1
    for y_index in range(FieldConstants.MAX_HEIGHT):
        for x_index in range(FieldConstants.WIDTH):
            diff = get_diff(prev, current, x_index, y_index)
            if diff != prev_diff:
                record_block_counts(fumen_buffer, prev_diff, counter)
                counter = 0
                prev_diff = diff
            else:
                counter += 1

    # process last contiguous block
    record_block_counts(fumen_buffer, prev_diff, counter)
    if prev_diff == 8 and counter == FieldConstants.MAX_BLOCKS - 1:
        changed = False

    return (changed, fumen_buffer)

def ensure_bool(obj: Optional[bool]) -> bool:
    return False if obj is None else obj

def encode(pages: List[Page]) -> str:
    last_repeat_index = -1
    fumen_buffer = FumenBuffer()
    prev_field = create_new_inner_field()

    action_encoder = ActionEncoder(FieldConstants.WIDTH, FieldConstants.HEIGHT, FieldConstants.GARBAGE_LINE)

    prev_comment: Optional[str] = ''
    prev_quiz: Optional[Quiz] = None    

    for index in range(0, len(pages)):
        current_page = pages[index]
        current_page.flags = current_page.flags if current_page.flags is not None else Flags()

        if isinstance(current_page, Page):
            field: Field = current_page.get_field()
            
        else:
            field: Field = current_page.field

        current_field: InnerField = create_inner_field(field) if field is not None else prev_field.copy()

        # Field update
        changed, values = encode_field(prev_field, current_field)

        if changed:
            # Record field and end repeat
            fumen_buffer.merge(values)
            last_repeat_index = -1

        elif last_repeat_index < 0 or fumen_buffer.get(last_repeat_index) == FumenBuffer.table_length - 1:
            # Record a field and start repeating
            fumen_buffer.merge(values)
            fumen_buffer.push(0)
            last_repeat_index = fumen_buffer.length() - 1

        elif fumen_buffer.get(last_repeat_index) < FumenBuffer.table_length - 1:
            # Do not record the field, advance the repeat
            current_repeat_value = fumen_buffer.get(last_repeat_index)
            fumen_buffer.set(last_repeat_index, current_repeat_value + 1)

        # Update action
        current_comment = (current_page.comment if index != 0 or current_page.comment != '' else None) if current_page.comment is not None else None

        piece = InnerOperation(parse_piece(current_page.operation.piece_type), 
                          parse_rotation(current_page.operation.rotation), 
                          current_page.operation.x, 
                          current_page.operation.y) if current_page.operation is not None else InnerOperation(Piece.EMPTY, Rotation.REVERSE, 0, 22,)

        next_comment: Optional[str] = None
        if current_comment is not None:
            if current_comment.startswith('#Q='):
                # Quiz on
                if prev_quiz is not None and prev_quiz.format().to_string() == current_comment:
                    next_comment = None
                else:
                    next_comment = current_comment
                    prev_comment = next_comment
                    prev_quiz = Quiz(current_comment)
                
            else:
                # Quiz off
                if prev_quiz is not None and prev_quiz.format().to_string() == current_comment:
                    next_comment = None
                    prev_comment = current_comment
                    prev_quiz = None
                else:
                    next_comment = current_comment if prev_comment != current_comment else None
                    prev_comment = next_comment if prev_comment != current_comment else prev_comment
                    prev_quiz = None
            
        else:
            next_comment = None
            prev_quiz = None

        if prev_quiz is not None and prev_quiz.can_operate() and current_page.flags.lock:
            if is_mino_piece(piece.piece_type):
                try:
                    next_quiz = prev_quiz.next_if_end()
                    operation = next_quiz.get_operation(piece.piece_type)
                    prev_quiz = next_quiz.operate(operation)
                except Exception as e:
                    # console.error(e.message)

                    # Not operate
                    prev_quiz = prev_quiz.format()

            else:
                prev_quiz = prev_quiz.format()

        current_flags = current_page.flags

        action = Action(piece, 
                        ensure_bool(current_flags.rise), 
                        ensure_bool(current_flags.mirror), 
                        ensure_bool(current_flags.colorize), 
                        next_comment is not None,
                        ensure_bool(current_flags.lock),)

        action_number = action_encoder.encode(action)

        fumen_buffer.push(action_number, 3)

        # Comment update
        if next_comment is not None:
            comment: str = escape(current_page.comment)
            comment_length = min(len(comment), 4095)

            fumen_buffer.push(comment_length, 2)

            # Encode comments
            for index in range(0, comment_length, 4):
                value = 0
                for count in range (4):
                    new_index = index + count
                    if comment_length <= new_index:
                        break

                    ch = comment[new_index]
                    value += CommentParser.encode(ch, count)

                fumen_buffer.push(value, 5)

        elif current_page.comment is None:
            prev_comment = None

        # terrain update
        if action.lock:
            if is_mino_piece(action.piece.piece_type):
                current_field.fill(action.piece)

            current_field.clear_line()

            if action.rise:
                current_field.rise_garbage()

            if action.mirror:
                current_field.mirror()

            prev_field = current_field

    # If the teto score is short, output it as is
    # A ? is inserted every 47 characters, but v115@ is actually placed at the beginning, so the first ? is 42 characters later.
    data = fumen_buffer.to_string()
    if len(data) < 41:
        return VERSION_INFO + data

    # ?to insert
    head = [data[0:42]]
    tails = data[42:]
    split = findall("[\S]{1,47}", tails)

    return VERSION_INFO + '?'.join(head + split)
