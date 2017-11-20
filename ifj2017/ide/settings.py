# coding=utf-8
from enum import IntEnum

from PyQt5.QtCore import QObject, Q_ENUMS
from PyQt5.QtQml import QQmlEngine, QJSEngine

from ifj2017.interpreter.instruction import Instruction

ICON_SIZES = (16, 24, 32, 48, 256)
EXPRESSION_SPLITTERS = set(" \n\t")


class Expression(QObject):
    class ExpressionTypes(IntEnum):
        Instruction = 0
        Variable = 1
        Types = 2
        Header = 3

    Q_ENUMS(ExpressionTypes)

    @staticmethod
    def singletonProvider(engine: QQmlEngine, script_engine: QJSEngine) -> QObject:
        return Expression()


INSTRUCTIONS = tuple(sorted(list(Instruction._commands.keys())))
IDENTIFIER_PATTERN = r'[\w_\-\$&%*]+'

SEARCH_FORMAT = "yellow"

HIGHLIGHT_RULES = (
    (("".join(("(?i)", instruction)) for instruction in INSTRUCTIONS), "#1d73a3"),
    ((r'[LGT]F@', ), '#930c80'),
    ((r'(?<=[LGT]F@){identifier}'.format(identifier=IDENTIFIER_PATTERN), ), 'black'),
    ((r'(?i)(call|label|JUMP|jumpifeq|jumpifneq|jumpifeqs|jumpifneqs)(\s+)({identifier})'.format(identifier=IDENTIFIER_PATTERN), ), ("#1d73a3", None ,'#4c4c4c')),
    ((r'(float|int)(@)(-?[0-9.]+)', r'(bool)(@)((?i)(true|false))', r'(string)@(.*)'), '#1ed3a8'),

    ((r'#.*$', ), 'gray'),
    (("([nN])([yY])([aA])([nN])",), "#ED1869 #F2BC1F #39BFC1 #672980".split()),
)
