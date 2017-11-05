# coding=utf-8
from html import escape, unescape
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtGui import QGuiApplication

class Core(QObject):
    @pyqtSlot(str, result=str)
    def htmlEscape(self, text: str) -> str:
        return escape(text)

    @pyqtSlot(str, result=str)
    def htmlUnescape(self, text: str) -> str:
        return unescape(text)

    @pyqtSlot(float, result=float)
    def scaledSize(self, ref_size: float) -> float:
        if ref_size == 0.0:
            return 0.0
        dpi = QGuiApplication.primaryScreen().logicalDotsPerInch();
        ref_dpi = 96

        return ref_size * (dpi / ref_dpi)
