# coding=utf-8
from enum import IntEnum

from PyQt5.QtCore import QObject, Q_ENUMS
from PyQt5.QtQml import QQmlEngine, QJSEngine


ICON_SIZES = (16, 24, 32, 48, 256)
EXPRESSION_SPLITTERS = set(" \n\t")


class Expression(QObject):
    class ExpressionTypes(IntEnum):
        Instruction = 0
        Variable = 1

    Q_ENUMS(ExpressionTypes)

    @staticmethod
    def singletonProvider(engine: QQmlEngine, script_engine: QJSEngine) -> QObject:
        return Expression()

INSTRUCTIONS = (
    'jump',
    'label'
)

HIGHLIGHT_RULES = (
    (INSTRUCTIONS, "red"),
    ((r'\d+',), 'purple'),
    (("([nN])([yY])([aA])([nN])",), "#ED1869 #F2BC1F #39BFC1 #672980".split()),
)

