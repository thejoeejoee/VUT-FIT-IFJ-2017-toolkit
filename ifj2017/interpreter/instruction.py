# coding=utf-8
import codecs
import logging
import operator

from .operand import Operand
from .state import State


def _unknown_command(state, *args):
    logging.error('Unknown command.')


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
        state.push_stack(operator_(op1, op2))

    return inner


class Instruction(object):
    name = None
    op0 = None
    op1 = None
    op2 = None

    def __init__(self, line):
        # type: (str) -> None
        parts = line.split()
        assert parts
        count = len(parts)
        self.name = parts[0].upper()
        if count == 2:
            self.op0 = Operand(parts[1])
        if count == 3:
            self.op0 = Operand(parts[1])
            self.op1 = Operand(parts[2])
        if count == 4:
            self.op0 = Operand(parts[1])
            self.op1 = Operand(parts[2])
            self.op2 = Operand(parts[3])

    @property
    def operands(self):
        return filter(None, (self.op0, self.op1, self.op2,))

    _commands = {
        'MOVE': State.move,
        'CREATEFRAME': lambda state: state.temp_frame.clear(),
        'PUSHFRAME': lambda state: state.frame_stack.append(state.temp_frame.copy()),
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

        # TODO: formats based on type
        # magic with escaped chars: escaped \\n to real \n
        'WRITE': lambda state, op: state.stdout.write(codecs.decode(str(state.get_value(op)), 'unicode_escape')),

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

        # TODO: read
        'READ': lambda state, op0, op1: None,
        'TYPE': lambda state, op0, op1: state.set_value(
            op0,
            Operand.CONSTANT_MAPPING_REVERSE.get(type(state.get_value(op1))) if state.get_value(op1) is not None else ''
        ),

        'BREAK': lambda state: state.stderr.write('{}\n'.format(state)),
        'DPRINT': lambda state, op0: state.stderr.write('{}\n'.format(state.get_value(op0))),

        'CONCAT': lambda state, target, op0, op1: state.set_value(target, ''.join((
            state.get_value(op0),
            state.get_value(op1),
        ))),
        'STRLEN': lambda state, target, string: state.set_value(target, len(string)),
        'GETCHAR': lambda state, target, string, index: state.set_value(
            target,
            state.get_value(string)[state.get_value(index)]
        ),
        'SETCHAR': State.set_char,


    }

    def run(self, state):
        logging.info('Processing {}.'.format(self.name))
        command = self._commands.get(self.name, _unknown_command)
        command(state, *self.operands)  # fake instance argument
