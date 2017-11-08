# coding=utf-8
from typing import Set
from .state import State
from .interpreter import Interpreter


class Debugger(object):
    def __init__(self, state_kwargs=None):
        self._breakpoints = set()
        self._interpreter = None  # type: Interpreter
        self._state = None
        self._active = False
        self._state_kwargs = state_kwargs
        self._debugger_iterator = None

    def _start(self, code):
        self._interpreter = Interpreter(
            code=code,
            state_kwargs=self._state_kwargs
        )
        self._active = True

    def add_breakpoint(self, line):
        self._breakpoints.add(line)

    def remove_breakpoint(self, line):
        self._breakpoints.remove(line)

    def run(self, code):
        self._start(code)
        self._state = self._interpreter.run()

    def debug(self, code, breakpoints=None):
        self._start(code)
        self._breakpoints = set(breakpoints) if breakpoints else set()
        self._debugger_iterator = self._interpreter.debug()
        return self.run_to_next_breakpoint()

    def stop(self):
        self._active = False
        self._state = self._debugger_iterator = None
        if self._interpreter:
            self._interpreter._active = False

    def run_to_next_breakpoint(self):
        if not self._active:
            raise RuntimeError()

        for state in self._debugger_iterator:
            self._state = state
            if not self._active:
                return None

            if self._interpreter.program_line(self._state.program_counter) in self._breakpoints:
                return self._state
        self._active = False

    def run_to_next_line(self):
        # type: () -> State
        if not self._active:
            raise RuntimeError()
        try:
            self._state = next(self._debugger_iterator)
        except StopIteration:
            self._active = None
            return None

        return self._state

    @property
    def breakpoints(self) -> Set[int]:
        return self._breakpoints

    @breakpoints.setter
    def breakpoints(self, v: Set[int]) -> None:
        self._breakpoints = v
