# coding=utf-8
import re
from enum import IntEnum
from typing import Match

CONSTANT_RE = re.compile(r'^(?P<type>bool|int|string|float)@(?P<value>.*)$', re.IGNORECASE)
VARIABLE_RE = re.compile(r'^(?P<frame>[GLT]F)@(?P<name>.*)$', re.IGNORECASE)
TYPE_RE = re.compile(r'^(?P<type>int|string|bool|float)$', re.IGNORECASE)


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
        # is label
        self.label = value
        self.type = TypeOperand.LABEL

    def _resolve_constant(self, constant_match):
        # type: (Match) -> None
        type_, value = constant_match.groups()
        self.value = self.CONSTANT_MAPPING.get(type_.lower())(value)
        self.type = TypeOperand.CONSTANT

    def _resolve_variable(self, variable_match):
        # type: (Match) -> None
        frame, name = variable_match.groups()
        self.frame = frame
        self.name = name
        self.type = TypeOperand.VARIABLE

    def _resolve_type(self, type_match):
        # type: (Match) -> None
        self.data_type = type_match.group(1)
        self.type = TypeOperand.DATA_TYPE
