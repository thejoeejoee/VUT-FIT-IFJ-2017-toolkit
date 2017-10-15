# coding=utf-8
from PyQt5.QtCore import QObject, pyqtSlot, Q_ENUMS
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtQml import QQmlEngine, QJSEngine

from ifj2017.ide.settings import Expression, HIGHLIGHT_RULES, EXPRESSION_SPLITTERS, INSTRUCTIONS


class CodeAnalyzer(QObject):
    _instance = None
    completerModelChanged = pyqtSignal(QVariant)

    instructions = [{"identifier": func, "type": Expression.ExpressionTypes.Instruction}
                              for func in INSTRUCTIONS]

    @pyqtProperty(QVariant, notify=completerModelChanged)
    def completerModel(self) -> QVariant:
        # TODO return keywords
        return QVariant(CodeAnalyzer.instructions)

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
