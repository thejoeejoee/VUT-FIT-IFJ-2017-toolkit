# coding=utf-8
import re

from typing import Optional, List

from PyQt5.QtCore import QObject, QRegularExpression, pyqtProperty, pyqtSlot
from PyQt5.QtCore import QVariant
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtGui import QTextCharFormat
from PyQt5.QtQml import QJSValue
from PyQt5.QtQuick import QQuickItem

from ifj2017.ide.code.expression import SyntaxHighlighter, HighlightRule
from ifj2017.ide.settings import SEARCH_FORMAT

__author__ = "Son Hai Nguyen"
__copyright__ = "Copyright 2017, /dej/uran/dom team"
__credits__ = ["Josef Kolář", "Son Hai Nguyen", "Martin Omacht", "Robert Navrátil"]
__license__ = "GNU GPL Version 3"


class ExpSyntaxHighlighter(QObject):
    """
    Class which wraps SyntaxHighliter and expose only target
    """

    searchMatchedLinesChanged = pyqtSignal(QVariant, arguments=["lines"])

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        self._syntax_highlighter = SyntaxHighlighter(self)
        self._base_font = None
        self._search_matched_lines = []

    def _setupFormat(self, color: QColor, fontSettings: QFont, colorIsForeground: bool = True) -> QTextCharFormat:
        pattern_format = QTextCharFormat()
        if color and colorIsForeground:
            pattern_format.setForeground(color)
        if color and (not colorIsForeground):
            pattern_format.setBackground(color)
        pattern_format.setFontItalic(fontSettings.italic())
        pattern_format.setFontWeight(fontSettings.bold())

        return pattern_format

    @pyqtSlot(list, QJSValue, QFont)
    def addHighlightMultiColorRule(self, patterns: List[str], color: QJSValue,
                                   fontSettings: QFont) -> None:
        """
        Adds highlight rule to syntax highlighter
        :param patterns: Regexp pattners to be matched
        :param color: Foreground color of matched text
        :param fontSettings: Determinates font weight and italic
        """

        pattern_format = list()
        self._base_font = fontSettings

        for single_color in color.toVariant():
            pattern_format.append(self._setupFormat(QColor(single_color), fontSettings))

        for single_pattern in patterns:
            self._syntax_highlighter.addHighlightRule(
                HighlightRule(pattern_format, QRegularExpression(single_pattern))
            )

    @pyqtSlot(list, QColor, QFont)
    def addHighlightSingleColorRule(self, patterns: List[str], color: QColor, fontSettings: QFont) -> None:
        """
        Adds highlight rule to syntax highlighter
        :param patterns: Regexp pattners to be matched
        :param color: Foreground color of matched text
        :param fontSettings: Determinates font weight and italic
        """

        pattern_format = self._setupFormat(color, fontSettings)
        self._base_font = fontSettings

        for single_pattern in patterns:
            self._syntax_highlighter.addHighlightRule(
                HighlightRule(pattern_format, QRegularExpression(single_pattern))
            )

    @pyqtSlot(str)
    def setSearchPattern(self, pattern: str) -> None:
        pattern_format = self._setupFormat(QColor(SEARCH_FORMAT), self._base_font, False)
        if pattern:
            self._syntax_highlighter.setSearchRule(
                HighlightRule(pattern_format, QRegularExpression(re.escape(pattern), QRegularExpression.CaseInsensitiveOption))
            )
        else:
            self._syntax_highlighter.setSearchRule(None)
        self._syntax_highlighter.rehighlight()

        self._search_matched_lines = self._syntax_highlighter.searchMatchedLines()
        self.searchMatchedLinesChanged.emit(QVariant(self._search_matched_lines))

    @pyqtProperty(QVariant, notify=searchMatchedLinesChanged)
    def searchMatchedLines(self):
        return QVariant(self._search_matched_lines)

    @pyqtProperty(QQuickItem)
    def target(self) -> None:
        return self._syntax_highlighter.target

    @target.setter
    def target(self, v: QQuickItem) -> None:
        self._syntax_highlighter.target = v
