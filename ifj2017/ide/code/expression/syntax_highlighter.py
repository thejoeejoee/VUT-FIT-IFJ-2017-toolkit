# coding=utf-8
from typing import Optional, Union, Sequence

from collections import Iterable

from PyQt5.QtCore import pyqtSignal, QObject, pyqtProperty, QRegularExpression, pyqtSlot
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat
from PyQt5.QtQuick import QQuickItem, QQuickTextDocument


class HighlightRule(QObject):
    def __init__(self, textFormat: Optional[Union[QTextCharFormat, Sequence[QTextCharFormat]]] = None,
                 matchPattern: Optional[QRegularExpression] = None) -> None:
        """
        :param textFormat: Text format of text mathched by pattern
        :param matchPattern: Regex pattern to match wanted text
        """

        super().__init__(None)

        self._text_format = textFormat
        self._match_pattern = matchPattern

    @property
    def text_format(self) -> Union[QTextCharFormat, Sequence[QTextCharFormat], None]:
        return self._text_format

    @property
    def match_pattern(self) -> Union[QRegularExpression, None]:
        return self._match_pattern


class SyntaxHighlighter(QSyntaxHighlighter):
    """
    SyntaxHighlighter, which highlights text pattern with certain text format
    """

    targetChanged = pyqtSignal(QQuickItem)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)

        self._target = None
        self._highlight_rules = list()
        self._search_rule = None

        self.targetChanged.connect(self._setupNewDocument)

    def _setFormat(self, start: int, length: int, text_format: QTextCharFormat) -> None:
        self.setFormat(
            start,
            length,
            text_format
        )

    def highlightBlock(self, p_str: str) -> None:
        """
         Virtual method, which is called when block of text changed
         :param p_str: Block of text which changed
        """

        for rule in self._highlight_rules + [self._search_rule]:
            if not rule:
                continue
            cursor = 0
            match_pattern = rule.match_pattern

            while match_pattern.match(p_str, cursor).hasMatch():
                match = match_pattern.match(p_str, cursor)

                if isinstance(rule.text_format, Iterable):
                    assert len(rule.text_format) == match.lastCapturedIndex(), "Patterns count does not match colors count."
                    for i in range(1, match.lastCapturedIndex() + 1):
                        self._setFormat(match.capturedStart(i), match.capturedLength(i), rule.text_format[i - 1])
                        cursor = match.capturedStart(i) + match.capturedLength(i)
                else:
                    self._setFormat(match.capturedStart(), match.capturedLength(), rule.text_format)
                    cursor = match.capturedStart() + match.capturedLength()

    def searchMatchedLines(self):
        text = self.document().toPlainText().split("\n")
        matched_lines = []

        if not self._search_rule:
            return matched_lines

        for line, line_text in enumerate(text):
            if self._search_rule.match_pattern.match(line_text).hasMatch():
                matched_lines.append(line + 1)

        return matched_lines


    def addHighlightRule(self, highlightRule: HighlightRule) -> None:
        self._highlight_rules.append(highlightRule)

    def setSearchRule(self, searchRule: Optional[HighlightRule]) -> None:
        self._search_rule = searchRule

    @pyqtSlot(QQuickItem)
    def _setupNewDocument(self, target: QQuickItem) -> None:
        """
        Extract set new document from target
        :param target: Item, from which document which will extracted
        """

        self.setDocument(target.property("textDocument").textDocument())

    @pyqtProperty(QQuickItem)
    def target(self) -> QQuickItem:
        return self._target

    @target.setter
    def target(self, v: QQuickItem) -> None:
        if self._target != v:
            self._target = v
            self.targetChanged.emit(v)