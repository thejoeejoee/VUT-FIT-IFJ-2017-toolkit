# coding=utf-8
import re

from PyQt5.QtCore import QObject
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtQml import QQmlEngine, QJSEngine

from ifj2017.ide.settings import Expression, HIGHLIGHT_RULES, EXPRESSION_SPLITTERS, INSTRUCTIONS


class CodeAnalyzer(QObject):
    _instance = None
    completerModelChanged = pyqtSignal(QVariant)

    VARIABLE_RE = re.compile(r'^[GLT]F@[A-z_\-$&%*]$', re.IGNORECASE)

    @property
    def code(self):
        return ''

    @pyqtProperty(QVariant, notify=completerModelChanged)
    def completerModel(self) -> QVariant:
        return QVariant(
            [
                dict(
                    identifier=func,
                    type=Expression.ExpressionTypes.Instruction
                ) for func in INSTRUCTIONS
            ] + [
                dict(
                    identifier=match.group(0),
                    type=Expression.ExpressionTypes.Instruction
                ) for match in self.VARIABLE_RE.findall(self.code)
            ]
        )

    @pyqtProperty(QVariant)
    def highlightRules(self) -> QVariant:
        return QVariant([dict(pattern=pattern, color=color)
                         for (pattern, color) in HIGHLIGHT_RULES]
                        )

    @pyqtProperty(QVariant)
    def expressionSplitters(self) -> QVariant:
        return QVariant(list(EXPRESSION_SPLITTERS))

    @staticmethod
    def singletonProvider(engine: QQmlEngine, script_engine: QJSEngine) -> QObject:
        if CodeAnalyzer._instance is None:
            CodeAnalyzer._instance = CodeAnalyzer()
        return CodeAnalyzer._instance
