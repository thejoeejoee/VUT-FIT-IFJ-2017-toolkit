# coding=utf-8

from io import StringIO

from .operand import Operand
from .operand import TypeOperand


class State(object):
    program_counter = 0
    executed_instructions = 0

    def __init__(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.stdin = StringIO()
        self.temp_frame = {}
        self.frame_stack = []  # top at end of list
        self.global_frame = {}
        self.call_stack = []  # top at end of list
        self.data_stack = []  # top at end of list
        self.labels = {}

    @property
    def local_frame(self):
        return self.frame_stack[-1] if self.frame_stack else {}  # little bit fake

    def frame(self, frame):
        return {
            'TF': self.temp_frame,
            'LF': self.local_frame,
            'GF': self.global_frame,
        }.get(frame)

    def get_value(self, value):
        # type: (Operand) -> object
        if not value:
            return None
        if not isinstance(value, Operand):
            return value
        if value.type == TypeOperand.CONSTANT:
            return value.value
        elif value.type == TypeOperand.VARIABLE:
            # wanted key error
            return self.frame(value.frame)[value.name]

    def set_value(self, to, what):
        # type: (Operand, Operand|object) -> None
        self.frame(to.frame)[to.name] = self.get_value(what)

    def __str__(self):
        join = ', '.join
        return 'State(TF=({}), LF=({})({}), GF=({}), STACK=[{}], PC={}, EXECUTED={})'.format(
            join('{}: {}'.format(k, v) for k, v in self.temp_frame.items()) if self.temp_frame else '-',
            join('{}: {}'.format(k, v) for k, v in self.local_frame.items()) if self.local_frame else '-',
            len(self.frame_stack),
            join('{}: {}'.format(k, v) for k, v in self.global_frame.items()) if self.global_frame else '-',
            join(map(str, reversed(self.data_stack))),
            self.program_counter,
            self.executed_instructions,
        )

    # concrete state change implementations

    def pop_frame(self):
        self.temp_frame = self.frame_stack[-1]
        self.frame_stack = self.frame_stack[:-1]

    def define_variable(self, variable):
        # type: (Operand) -> None
        self.frame(variable.frame)[variable.name] = None

    def move(self, to, what):
        # type: (Operand, Operand) -> None
        self.frame(to.frame)[to.name] = what.value

    def call(self, op):
        # type: (Operand, Operand) -> None
        self.call_stack.append(self.program_counter)
        self.program_counter = self.labels.get(op.label)

    def return_(self):
        self.program_counter = self.call_stack[-1] + 1
        self.call_stack = self.call_stack[:-1]

    def jump(self, op):
        # type: (Operand) -> None
        self.program_counter = self.labels.get(op.label)

    def push_stack(self, op):
        self.data_stack.append(self.get_value(op))

    def pop_stack(self, op=None):
        # type: (Operand) -> object
        value = self.data_stack[-1]
        if op:
            # for operand is set, without is only returned
            self.set_value(op, value)

        self.data_stack = self.call_stack[:-1]
        return value

    def jump_if(self, op0, op1, op2, positive=True):
        equal = self.get_value(op1) == self.get_value(op2)
        if positive == equal:
            self.jump(op0)

    def set_char(self, where, index, from_):
        changed = self.get_value(where)
        changed[self.get_value(index)] = self.get_value(from_)[0]
        self.set_value(where, changed)

    def read(self, to, type_):
        # type: (Operand, Operand) -> None
        self.stdout.write('? ')
        loaded = []
        input_ = self.stderr.readline().strip()  # type: str
        if type_.data_type == Operand.CONSTANT_MAPPING_REVERSE.get(str):
            # is string
            i = 1
            while input_[i] != '"':
                loaded.append(input_[i])
                i += 1
            self.set_value(to, ''.join(loaded))
