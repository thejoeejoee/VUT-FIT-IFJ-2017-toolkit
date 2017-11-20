# coding=utf-8
import re
from typing import Optional

from PyQt5.QtCore import QObject, QVariant, pyqtProperty, pyqtSignal
from PyQt5.QtQml import QQmlEngine, QJSEngine

from ifj2017.ide.settings import Expression, HIGHLIGHT_RULES, EXPRESSION_SPLITTERS, INSTRUCTIONS


class CodeAnalyzer(QObject):
    _instance = None
    completerModelChanged = pyqtSignal()

    VARIABLE_RE = re.compile(r'[GLT]F@[A-Za-z0-9_\-\$&%\*]+', re.IGNORECASE)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        self._code = ''

    @pyqtProperty(str)
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, v: str) -> None:
        self._code = v
        self.completerModelChanged.emit()

    @pyqtProperty(QVariant, notify=completerModelChanged)
    def completerModel(self) -> QVariant:
        return QVariant(
            [
                dict(
                    identifier='.IFJcode17',
                    type=Expression.ExpressionTypes.Header
                )
            ] if '.IFJcode17' not in self.code else [] + [
                dict(
                    identifier=match,
                    type=Expression.ExpressionTypes.Types
                ) for match in sorted(("int", "bool", "float", "string"))
            ] + [
                dict(
                    identifier=func,
                    type=Expression.ExpressionTypes.Instruction
                ) for func in INSTRUCTIONS
            ] + [
                dict(
                    identifier=match,
                    type=Expression.ExpressionTypes.Variable
                ) for match in sorted(set(self.VARIABLE_RE.findall(self._code)))
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
