# coding=utf-8

from .exceptions import InterpreterStopException, InvalidCodeException, BaseInterpreterError
from .instruction import Instruction
from .state import State


class Interpreter(object):
    def __init__(self, code, state_kwargs=None):
        # type: (str) -> None
        self._code = code
        self._instructions = []
        self._load_code()
        self._state_kwargs = state_kwargs
        self._active = True

    def _load_code(self):
        started = False
        if not self._code.strip():
            raise InvalidCodeException("Empty code")

        # _start from 1, .IFJcode17 striped
        for i, line in enumerate(self._code.splitlines(), start=1):
            line = line.strip().split('#', 1)[0].strip()  # naive method to strip comment?
            if not line or line.startswith('#'):
                # comment line
                continue
            if line == ".IFJcode17" and not started:
                started = True
                continue

            if not started:
                raise InvalidCodeException(
                    InvalidCodeException.MISSING_HEADER,
                    line=line,
                    line_index=i
                )

            self._instructions.append(Instruction(line=line.strip(), line_index=i))

    def _load_labels(self, state):
        # type: (State) -> None
        for index, instruction in enumerate(self._instructions):
            if instruction.name == 'LABEL':
                state.labels[instruction.op0.label] = index

    def _prepare_state(self):
        state = State(**(self._state_kwargs or {}))

        state.program_line = self._instructions[0].line_index if self._instructions else -1
        self._load_labels(state)

        return state, len(self._instructions)

    def run(self):
        state, program_length = self._prepare_state()

        while state.program_counter < program_length and self._active:
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

    def debug(self):
        state, program_length = self._prepare_state()
        while state.program_counter < program_length and self._active:
            yield state  # can be modified
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

    def program_line(self, program_counter):
        # type: (State) -> int
        instruction = self._instructions[program_counter]  # type:  Instruction
        return instruction.line_index
