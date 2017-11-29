# coding=utf-8
import logging
import math
import operator
from inspect import getfullargspec

from .exceptions import InvalidCodeException, BaseInterpreterError
from .operand import Operand
from .prices import InstructionPrices
from .state import State


def even_round(v: int) -> int:
    return int(round(v))


def odd_round(v: int) -> int:
    return int(
        (
            math.floor,
            math.ceil,
            math.floor,
            lambda v: math.floor(v) if v % 2.0 == 1.5 else math.ceil(v)
        )[
            int(((v % 2) // 0.5))
        ](v)
    )


def _unknown_command(state, *args):
    raise InvalidCodeException(InvalidCodeException.UNKNOWN_INSTRUCTION)


def _operator_command(operator_):
    # type: (callable) -> callable
    def inner(state, op0, op1, op2):
        # type: (State, Operand, Operand, Operand) -> None
        state.set_value(op0, operator_(state.get_value(op1), state.get_value(op2)))

    return inner


def _operator_stack_command(operator_):
    # type: (callable) -> callable
    def inner(state):
        # type: (State, Operand, Operand, Operand) -> None
        op2 = state.pop_stack()
        op1 = state.pop_stack()
        logging.debug("Stack operation {} {} {}.".format(op1, operator_.__name__, op2))
        state.push_stack(operator_(op1, op2))

    return inner


class Instruction(object):
    name = None
    op0 = None
    op1 = None
    op2 = None

    def __init__(self, line, line_index):
        # type: (str) -> None
        parts = line.split()
        assert parts
        count = len(parts)
        self.name = parts[0].upper()
        self.line_index = line_index
        self._line = line

        command = self._commands.get(self.name)

        if not command or not callable(command):
            raise InvalidCodeException(line_index=line, type_=InvalidCodeException.UNKNOWN_INSTRUCTION)

        spec = getfullargspec(command)
        if len(spec.args) != count:
            raise InvalidCodeException(InvalidCodeException.INVALID_OPERAND_COUNT, line_index, line)

        try:
            if count > 3:
                self.op2 = Operand(parts[3])
            if count > 2:
                self.op1 = Operand(parts[2])
            if count > 1:
                self.op0 = Operand(parts[1])
        except InvalidCodeException as e:
            e.line_index = line_index
            e.line = line
            raise

    @property
    def operands(self):
        return filter(None, (self.op0, self.op1, self.op2,))

    _commands = {
        'MOVE': State.set_value,
        'CREATEFRAME': State.create_frame,
        'PUSHFRAME': State.push_frame,
        'POPFRAME': State.pop_frame,
        'DEFVAR': lambda state, op: state.set_value(op, None),
        'JUMP': State.jump,
        'CALL': State.call,
        'RETURN': State.return_,
        'LABEL': lambda s, o: None,

        'JUMPIFEQ': lambda state, op0, op1, op2: state.jump_if(op0, op1, op2, positive=True),
        'JUMPIFNEQ': lambda state, op0, op1, op2: state.jump_if(op0, op1, op2, positive=False),
        'JUMPIFEQS': lambda state, op0: state.jump_if(op0, state.pop_stack(), state.pop_stack(), positive=True),
        'JUMPIFNEQS': lambda state, op0: state.jump_if(op0, state.pop_stack(), state.pop_stack(), positive=False),

        'WRITE': State.write,

        'PUSHS': State.push_stack,
        'POPS': State.pop_stack,
        'CLEARS': lambda state: state.data_stack.clear(),

        'ADD': _operator_command(operator.add),
        'SUB': _operator_command(operator.sub),
        'MUL': _operator_command(operator.mul),
        'DIV': _operator_command(operator.truediv),
        'ADDS': _operator_stack_command(operator.add),
        'SUBS': _operator_stack_command(operator.sub),
        'MULS': _operator_stack_command(operator.mul),
        'DIVS': _operator_stack_command(operator.truediv),

        'LT': _operator_command(operator.lt),
        'GT': _operator_command(operator.gt),
        'EQ': _operator_command(operator.eq),
        'LTS': _operator_stack_command(operator.lt),
        'GTS': _operator_stack_command(operator.gt),
        'EQS': _operator_stack_command(operator.eq),

        'AND': _operator_command(operator.and_),
        'OR': _operator_command(operator.or_),
        'NOT': lambda state, op0, op1: state.set_value(op0, not state.get_value(op1)),
        'ANDS': _operator_stack_command(operator.and_),
        'ORS': _operator_stack_command(operator.or_),
        'NOTS': lambda state: state.push_stack(not state.pop_stack(None)),

        'READ': State.read,
        'TYPE': lambda state, op0, op1: state.set_value(
            op0,
            Operand.CONSTANT_MAPPING_REVERSE.get(type(state.get_value(op1))) if state.get_value(op1) is not None else ''
        ),

        'BREAK': lambda state: state.stderr.write('{}\n'.format(state)),
        'DPRINT': lambda state, op0: state.stderr.write('{}\n'.format(state.get_value(op0))),
        'GROOT': lambda state: state.stderr.write('Price: {} ({}+{}).\n'.format(state.price, state.instruction_price, state.operand_price)),

        'CONCAT': lambda state, target, op0, op1: state.set_value(target, ''.join((
            state.get_value(op0),
            state.get_value(op1),
        ))),
        'STRLEN': State.str_len,
        'GETCHAR': State.get_char,
        'SETCHAR': State.set_char,

        'INT2FLOAT': lambda state, op0, op1: state.set_value(op1, float(state.get_value(op1))),
        'FLOAT2INT': lambda state, op0, op1: state.set_value(op1, int(state.get_value(op1))),
        'FLOAT2R2EINT': lambda state, op0, op1: state.set_value(
            op0,
            even_round(state.get_value(op1))
        ),
        'FLOAT2R2OINT': lambda state, op0, op1: state.set_value(
            op0,
            odd_round(state.get_value(op1))
        ),
        'INT2CHAR': lambda state, to, what: state.set_value(to, chr(state.get_value(what))),
        'STRI2INT': lambda state, to, what, index: state.set_value(
            to,
            ord(state.get_value(what)[state.get_value(index)])
        ),

        'INT2FLOATS': lambda state: state.push_stack(float(state.pop_stack())),
        'FLOAT2INTS': lambda state: state.push_stack(int(state.pop_stack())),
        'FLOAT2R2EINTS': lambda state: state.push_stack(
            even_round(state.pop_stack())
        ),
        'FLOAT2R2OINTS': lambda state: state.push_stack(
            odd_round(state.pop_stack())
        ),
        'INT2CHARS': lambda state: state.push_stack(chr(state.pop_stack())),
        'STRI2INTS': State.string_to_int_stack,
    }

    def run(self, state: State):
        logging.info('Processing {} on {}.'.format(self.name, self.line_index))
        command = self._commands.get(self.name, _unknown_command)
        price = InstructionPrices.INSTRUCTIONS.get(self.name)
        try:
            command(state, *self.operands)  # fake instance argument
        except BaseInterpreterError as e:
            e.line_index = self.line_index
            e.line = self._line
            raise
        state.instruction_price += price
        state.executed_instructions += 1
        state.program_line = self.line_index
