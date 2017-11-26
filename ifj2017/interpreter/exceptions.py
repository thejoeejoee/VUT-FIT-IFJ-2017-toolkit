# coding=utf-8

class InterpreterStopException(RuntimeError):
    pass


class InvalidCodeException(ValueError):
    UNKNOWN_INSTRUCTION = 0
    INVALID_OPERAND = 1
    INVALID_OPERAND_COUNT = 2
    MISSING_HEADER = 3

    def __init__(self, type_, line_index=None, line=None):
        self._type = type_
        self.line_index = line_index
        self.line = line

    def __str__(self):
        messages = {
            self.UNKNOWN_INSTRUCTION: 'Unknown instruction on line {self.line_index}: {self.line}.',
            self.INVALID_OPERAND: 'Invalid operand on line {self.line_index}: {self.line}.',
            self.INVALID_OPERAND_COUNT: 'Invalid count of operands on line {self.line_index}: {self.line}.',
            self.MISSING_HEADER: 'Missing .IFJcode17 header on line {self.line_index}.'
        }
        return messages.get(
            self._type,
            'Invalid line {self.line_index}: {self.line}.'
        ).format(self=self)


class BaseInterpreterError(RuntimeError):
    msg = None
    line_index = None
    line = None

    def __init__(self, msg=None):
        super().__init__()
        self.msg = msg

    @property
    def on_line(self):
        return ' on line {}: {}.'.format(self.line_index, self.line)

    def __str__(self):
        return self.msg or 'Interpreter error{}'.format(self.on_line)


class UnknownDataTypeError(BaseInterpreterError):
    def __str__(self):
        return 'Unknown data type error{}'.format(self.on_line)


class StringError(BaseInterpreterError):
    def __init__(self, source, index):
        self._source = source
        self._index = index

    def __str__(self):
        return 'Invalid index {} on string "{}"{}'.format(self._index, self._source, self.on_line)


class EmptyDataStackError(BaseInterpreterError):
    def __str__(self):
        return 'Empty data stack error{}'.format(self.on_line)


class InvalidOperandTypeError(BaseInterpreterError):
    def __str__(self):
        return 'Invalid operand type{}'.format(self.on_line)


class UndefinedVariableError(BaseInterpreterError):
    def __init__(self, name, frame):
        self.name = name
        self.frame = frame

    def __str__(self):
        return 'Undefined variable {}@{}{}'.format(self.frame, self.name, self.on_line)


class UndeclaredVariableError(BaseInterpreterError):
    def __init__(self, name, frame):
        self.name = name
        self.frame = frame

    def __str__(self):
        return 'Undeclared variable {}@{}{}'.format(self.frame, self.name, self.on_line)


class UnknownLabelError(BaseInterpreterError):
    def __init__(self, label_name):
        self.label_name = label_name

    def __str__(self):
        return 'Unknown label {}{}'.format(self.label_name, self.on_line)


class InvalidReturnError(BaseInterpreterError):
    def __str__(self):
        return 'Invalid return error{}'.format(self.on_line)


class FrameError(BaseInterpreterError):
    def __str__(self):
        return 'Frame error{}'.format(self.on_line)
