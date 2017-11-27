# coding=utf-8
import re
from enum import IntEnum
from typing import Match

from .exceptions import InvalidCodeException

_IDENTIFIER_RE_PART = r'[a-z_\-$&%*][\w_\-$&%*]*'
CONSTANT_RE = re.compile(r'^(?P<type>bool|int|string|float)@(?P<value>.*)$', re.IGNORECASE)
VARIABLE_RE = re.compile(r'^(?P<frame>[GLT]F)@(?P<name>{})$'.format(_IDENTIFIER_RE_PART), re.IGNORECASE)
TYPE_RE = re.compile(r'^(?P<type>int|string|bool|float)$', re.IGNORECASE)
LABEL_RE = re.compile(r'^{}$'.format(_IDENTIFIER_RE_PART), re.IGNORECASE)

float_ = float


def float(value):
    # sorry, Python builtin
    try:
        return float_(value)
    except ValueError:
        return float_.fromhex(value)


ESCAPE_RE = re.compile(r'\\([0-9]{3})')


def unquote_escape_sequences(value):
    def __(m):
        # magic for decimal \ddd to octal \ooo
        return chr(int(m.group(1)))

    return ESCAPE_RE.sub(__, value)


class TypeOperand(IntEnum):
    VARIABLE = 1
    CONSTANT = 2
    LABEL = 3
    DATA_TYPE = 4


class Operand(object):
    type = None
    # constant
    value = None
    # variable
    frame = None
    name = None
    # data type
    data_type = None
    # label
    label = None

    CONSTANT_MAPPING = {
        'bool': bool,
        'int': int,
        'float': float,
        'string': str,
    }

    CONSTANT_MAPPING_REVERSE = {k: v for v, k in CONSTANT_MAPPING.items()}

    BOOL_LITERAL_MAPPING = {'true': True, 'false': False}

    def __init__(self, value):
        # type: (str) -> None
        constant_match = CONSTANT_RE.match(value)
        if constant_match:
            self._resolve_constant(constant_match)
            return
        variable_match = VARIABLE_RE.match(value)
        if variable_match:
            self._resolve_variable(variable_match)
            return
        type_match = TYPE_RE.match(value)
        if type_match:
            self._resolve_type(type_match)
            return
        label_match = LABEL_RE.match(value)
        if label_match:
            # is label
            self.label = value
            self.type = TypeOperand.LABEL
            return

        raise InvalidCodeException(InvalidCodeException.INVALID_OPERAND)

    def _resolve_constant(self, constant_match: Match[str]) -> None:
        type_, value = constant_match.groups()  # type: str, str
        type_ = type_.lower().strip()
        try:
            self.value = self.CONSTANT_MAPPING.get(type_)(value)
            if type_ == self.CONSTANT_MAPPING_REVERSE.get(bool):
                self.value = self.BOOL_LITERAL_MAPPING.get(value.lower())
            elif type_ == self.CONSTANT_MAPPING_REVERSE.get(str):
                self.value = unquote_escape_sequences(value=self.value)
        except ValueError:
            pass
        if self.value is None:
            raise InvalidCodeException(type_=InvalidCodeException.INVALID_OPERAND)
        self.type = TypeOperand.CONSTANT

    def _resolve_variable(self, variable_match: Match[str]) -> None:
        # type: (Match) -> None
        frame, name = variable_match.groups()
        if not (frame and name):
            raise InvalidCodeException(type_=InvalidCodeException.INVALID_OPERAND)
        self.frame = frame
        self.name = name
        self.type = TypeOperand.VARIABLE

    def _resolve_type(self, type_match: Match[str]) -> None:
        # type: (Match[str]) -> None
        self.data_type = type_match.group(1).lower()
        if self.data_type not in self.CONSTANT_MAPPING:
            raise InvalidCodeException(type_=InvalidCodeException.INVALID_OPERAND)
        self.type = TypeOperand.DATA_TYPE

    def __str__(self):
        return 'Operand({})'.format(
            self.value or self.name or self.label
        )
