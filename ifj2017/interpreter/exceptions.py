# coding=utf-8

class InterpreterStopException(RuntimeError):
    pass


class InvalidCodeException(ValueError):
    UNKNOWN_INSTRUCTION = 0
    INVALID_OPERAND = 1
    INVALID_OPERAND_COUNT = 2

    def __init__(self, type_, line_index=None, line=None):
        self._type = type_
        self.line_index = line_index
        self.line = line

    def __str__(self):
        return 'Invalid line {}: {}.'.format(self.line_index, self.line)


class BaseInterpreterError(RuntimeError):
    pass


class EmptyDataStackError(BaseInterpreterError):
    pass


class UndefinedVariableError(BaseInterpreterError):
    def __init__(self, name, frame):
        self.name = name
        self.frame = frame


class UndeclaredVariableError(BaseInterpreterError):
    def __init__(self, name, frame):
        self.name = name
        self.frame = frame


class UnknownLabelError(BaseInterpreterError):
    pass


class InvalidReturnError(BaseInterpreterError):
    pass


class FrameError(BaseInterpreterError):
    pass
