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
    def __str__(self):
        return 'Empty data stack.'


class UndefinedVariableError(BaseInterpreterError):
    def __init__(self, name, frame):
        self.name = name
        self.frame = frame

    def __str__(self):
        return 'Undefined variable {}@{}.'.format(self.frame, self.name)


class UndeclaredVariableError(BaseInterpreterError):
    def __init__(self, name, frame):
        self.name = name
        self.frame = frame

    def __str__(self):
        return 'Undeclared variable {}@{}.'.format(self.frame, self.name)

class UnknownLabelError(BaseInterpreterError):
    def __init__(self, label_name):
        self.label_name = label_name

    def __str__(self):
        return 'Unknown label.'


class InvalidReturnError(BaseInterpreterError):
    def __str__(self):
        return 'Invalid return.'


class FrameError(BaseInterpreterError):
    def __str__(self):
        return 'Frame error.'
