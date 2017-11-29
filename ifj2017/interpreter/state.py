# coding=utf-8
import logging
import re
from io import StringIO
from typing import Optional, Union

from ifj2017.interpreter.exceptions import UnknownDataTypeError, StringError
from .exceptions import EmptyDataStackError, UndefinedVariableError, UndeclaredVariableError, \
    FrameError, UnknownLabelError, InvalidReturnError, InvalidOperandTypeError
from .operand import Operand, TypeOperand
from .prices import InstructionPrices


class State(object):
    program_counter = 0
    executed_instructions = 0
    program_line = 0

    def __init__(self, stdout=None, stderr=None, stdin=None):
        self.stdout = stdout or StringIO()
        self.stderr = stderr or StringIO()
        self.stdin = stdin or StringIO()
        self.temp_frame = None
        self.frame_stack = []  # top at end of list
        self.global_frame = {}
        self.call_stack = []  # top at end of list
        self.data_stack = []  # top at end of list
        self.labels = {}

        self.instruction_price = 0
        self.operand_price = 0

    # concrete state change implementations

    @property
    def local_frame(self):
        if not self.frame_stack:
            raise FrameError('Access to non existing local frame.')
        return self.frame_stack[-1]

    def frame(self, frame):
        return {
            'TF': lambda: self.temp_frame,
            'LF': lambda: self.local_frame,
            'GF': lambda: self.global_frame,
        }.get(frame)()

    def create_frame(self):
        self.temp_frame = {}

    def push_frame(self):
        if self.temp_frame is None:
            raise FrameError('Temp frame to push is undefined.')

        self.frame_stack.append(self.temp_frame.copy())
        self.temp_frame = None

    def pop_frame(self):
        if not self.frame_stack:
            raise FrameError('Non-existing frame to pop.')
        self.temp_frame = self.frame_stack[-1]
        self.frame_stack = self.frame_stack[:-1]

    def get_value(self, value: Optional[Operand]) -> Union[None, int, str, float]:
        if value is None:
            # variable declaration
            return None

        if not isinstance(value, Operand):
            return value
        if value.type == TypeOperand.CONSTANT:
            self.operand_price += InstructionPrices.OPERAND_CONSTANT
            return value.value
        elif value.type == TypeOperand.VARIABLE:
            # wanted key error
            self.operand_price += InstructionPrices.OPERAND_VARIABLE
            variable_value = self.frame(value.frame)[value.name]
            if variable_value is None:
                raise UndefinedVariableError(value.name, value.frame)
            return variable_value
        raise InvalidOperandTypeError()

    def set_value(self, to, what):
        # type: (Operand, Operand|object) -> None
        if to.type != TypeOperand.VARIABLE:
            raise InvalidOperandTypeError()

        frame = self.frame(to.frame)
        if frame is None:
            raise FrameError('Non existing frame {}'.format(to.frame))
        if to.name not in frame and what is not None:  # declared or declaration
            raise UndeclaredVariableError(to.name, to.frame)
        frame[to.name] = self.get_value(what)

        # explicit variable access, only declaration
        self.operand_price += InstructionPrices.OPERAND_VARIABLE

    def define_variable(self, variable):
        # type: (Operand) -> None
        self.frame(variable.frame)[variable.name] = None

    def call(self, op):
        # type: (Operand, Operand) -> None
        if op.label not in self.labels:
            raise UnknownLabelError(op.label)

        self.call_stack.append(self.program_counter)
        self.program_counter = self.labels.get(op.label)

    def return_(self):
        if not self.call_stack:
            raise InvalidReturnError()
        self.program_counter = self.call_stack[-1] + 1
        self.call_stack = self.call_stack[:-1]

    def jump(self, op):
        # type: (Operand) -> None
        if op.label not in self.labels:
            raise UnknownLabelError(op.label)

        self.program_counter = self.labels.get(op.label)

    def push_stack(self, op):
        value = self.get_value(op)
        logging.debug("Push {} to stack.".format(value))
        self.data_stack.append(value)
        self.operand_price += InstructionPrices.OPERAND_STACK

    def pop_stack(self, op=None):
        # type: (Operand) -> object
        if not self.data_stack:
            raise EmptyDataStackError()

        value = self.data_stack[-1]
        logging.debug("Pop {} from stack.".format(value))
        if op:
            # for operand is set, without is only returned
            self.set_value(op, value)

        self.operand_price += InstructionPrices.OPERAND_STACK
        self.data_stack = self.data_stack[:-1]
        return value

    def jump_if(self, op0, op1, op2, positive=True):
        equal = self.get_value(op1) == self.get_value(op2)
        if positive == equal:
            self.jump(op0)

    def set_char(self, where, index, from_):
        changed = self.get_value(where)
        changed[self.get_value(index)] = self.get_value(from_)[0]
        self.set_value(where, changed)

    def get_char(self, target, string, index):
        source = self.get_value(string)
        try:
            self.set_value(
                target,
                source[self.get_value(index)]
            )
        except IndexError:
            raise StringError(source, self.get_value(index))

    def str_len(self, target, string):
        return self.set_value(target, len(self.get_value(string)))

    def read(self, to, type_):
        # type: (Operand, Operand) -> None
        loaded = []
        input_ = self.stdin.readline().strip()  # type: str
        input_len = len(input_)
        if type_.data_type == Operand.CONSTANT_MAPPING_REVERSE.get(str):
            # is string
            i = input_[0] == "\""
            while i < input_len and input_[i] != '"':
                loaded.append(input_[i])
                i += 1
            try:
                self.set_value(to, ''.join(loaded))
            except ValueError:
                self.set_value(to, "")
        elif type_.data_type == Operand.CONSTANT_MAPPING_REVERSE.get(int):
            # is string
            i = 0
            while i < input_len and input_[i].isdecimal():
                loaded.append(input_[i])
                i += 1
            try:
                self.set_value(to, int(''.join(loaded)))
            except ValueError:
                self.set_value(to, 0)
        elif type_.data_type == Operand.CONSTANT_MAPPING_REVERSE.get(Operand.CONSTANT_MAPPING.get('float')):
            float_re = re.compile(r'^(\d+\.\d+)|(\d+[Ee][+-]?\d+)|(\d+)')
            match = float_re.match(input_)
            assert match
            try:
                self.set_value(to, Operand.CONSTANT_MAPPING.get('float')(match.group(0)))
            except ValueError:
                self.set_value(to, .0)
        elif type_.data_type == Operand.CONSTANT_MAPPING_REVERSE.get(bool):
            bool_re = re.compile(r'^(true|false)', re.IGNORECASE)
            match = bool_re.match(input_)
            if match:
                self.set_value(to, Operand.BOOL_LITERAL_MAPPING.get(match.group(0).lower()))
            else:
                self.set_value(to, False)
        else:
            raise UnknownDataTypeError()

    ESCAPE_RE = re.compile(r'\\([0-9]{3})')

    def write(self, op):
        value = self.get_value(op)
        rendered = str(value)
        if isinstance(value, bool):
            rendered = str(value).lower()
        elif isinstance(value, int):
            rendered = '{: d}'.format(value)
        elif isinstance(value, float):
            rendered = '{: g}'.format(value)

        self.stdout.write(rendered)

    def string_to_int_stack(self):
        index = self.pop_stack()
        what = self.pop_stack()

        self.push_stack(
            ord(what[index])
        )

    def __str__(self):
        join = ', '.join
        return 'State(TF=({}), LF=({})({}), GF=({}), STACK=[{}], PC={}, EXECUTED={}, PRICE={}({}+{}))'.format(
            join('{}: {}'.format(k, v) for k, v in self.temp_frame.items()) if self.temp_frame else '-',
            join('{}: {}'.format(k, v) for k, v in self.local_frame.items()) if self.frame_stack else '-',
            len(self.frame_stack),
            join('{}: {}'.format(k, v) for k, v in self.global_frame.items()) if self.global_frame else '-',
            join(map(str, reversed(self.data_stack))),
            self.program_counter,
            self.executed_instructions,
            self.instruction_price + self.operand_price,
            self.instruction_price,
            self.operand_price
        )

    def program_counter_to_label(self, pc):
        return {v: k for k, v in self.labels.items()}.get(pc) or ''

    @property
    def price(self):
        return self.operand_price + self.instruction_price
