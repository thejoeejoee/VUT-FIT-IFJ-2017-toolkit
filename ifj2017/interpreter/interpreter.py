# coding=utf-8
from ifj2017.interpreter.exceptions import InterpreterStopException
from .instruction import Instruction
from .state import State


class Interpreter(object):
    def __init__(self, code, stdin=None):
        # type: (str) -> None
        assert code.strip()
        self._code = code

        self._instructions = []

        self._load_code()

        self._stdin = stdin

    def _load_code(self):
        started = False
        # start from 1, .IFJcode17 striped
        for i, line in enumerate(self._code.split('\n'), start=1):
            line = line.strip()
            if not line or line.startswith('#'):
                # comment line
                continue
            if line == ".IFJcode17":
                started = True
                continue

            if not started:
                raise ValueError('Invalid code, expecting .IFJcode17, found {}.'.format(line))

            self._instructions.append(Instruction(line=line.strip(), line_index=i))

    def _load_labels(self, state):
        # type: (State) -> None
        for index, instruction in enumerate(self._instructions):
            if instruction.name == 'LABEL':
                state.labels[instruction.op0.label] = index

    def run(self):
        state = State()
        if self._stdin:
            state.stdin = self._stdin

        self._load_labels(state)
        program_length = len(self._instructions)
        while state.program_counter < program_length:
            program_counter = state.program_counter
            instruction = self._instructions[state.program_counter]  # type: Instruction
            try:
                instruction.run(state)
            except InterpreterStopException:
                break

            if program_counter == state.program_counter:
                # increment only in case of not manipulating with PC
                state.program_counter += 1

        return state
