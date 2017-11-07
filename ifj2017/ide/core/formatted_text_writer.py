# coding=utf-8
from typing import Optional
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QTextCharFormat
from PyQt5.QtGui import QTextCursor
from PyQt5.QtQuick import QQuickItem


class FormattedTextWriter(QObject):
    targetChanged = pyqtSignal(QQuickItem)

    def __init__(self, parent: Optional[QObject]):
        super().__init__(parent)

        self._target = None
        self._document = None
        self._cursor = None
        self.targetChanged.connect(self._setupNewDocument)

    def _setupFormat(self, color: QColor) -> QTextCharFormat:
        pattern_format = QTextCharFormat()
        if color is not None:
            pattern_format.setForeground(color)
        pattern_format.setFontItalic(self._target.property("font").italic())
        pattern_format.setFontWeight(self._target.property("font").bold())

        return pattern_format

    @pyqtSlot()
    def clear(self) -> None:
        self._cursor.select(QTextCursor.Document)
        self._cursor.removeSelectedText()

    @pyqtSlot(str, QColor)
    def write(self, text: str, color: QColor) -> None:
        self._cursor.movePosition(QTextCursor.End)
        self._cursor.insertText(text, self._setupFormat(color))

    @pyqtSlot(QQuickItem)
    def _setupNewDocument(self, target: QQuickItem) -> None:
        """
        Extract set new document from target
        :param target: Item, from which document which will extracted
        """

        self._document = target.property("textDocument").textDocument()
        self._cursor = QTextCursor(self._target.property("textDocument").textDocument())

    @pyqtProperty(QQuickItem)
    def target(self) -> QQuickItem:
        return self._target

    @target.setter
    def target(self, v: QQuickItem) -> None:
        if self._target != v:
            self._target = v
            self.targetChanged.emit(v)