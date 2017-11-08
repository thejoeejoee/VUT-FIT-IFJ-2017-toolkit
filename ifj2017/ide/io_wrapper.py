# coding=utf-8
from time import sleep
from typing import Optional

from PyQt5.QtCore import QEventLoop, QObject, pyqtSlot
from io import StringIO

from PyQt5.QtCore import pyqtSignal


class IOWrapper(QObject):
    unblockWaitSignal = pyqtSignal()
    readRequest = pyqtSignal()
    writeRequest = pyqtSignal(str, arguments=["text"])

    def __init__(self, parent: Optional[QObject]):
        super().__init__(parent)
        self._text = ""

    @pyqtSlot(str)
    def handleConsoleRead(self, text: str) -> None:
        self._text = text
        self.unblockWaitSignal.emit()

    def write(self, text: str) -> None:
        self.writeRequest.emit(text)
        sleep(0.001)

    def block_until_emit(self, unblock_signal):
        loop = QEventLoop()
        unblock_signal.connect(loop.quit)

        loop.exec_(QEventLoop.AllEvents)

    def readline(self):
        self.readRequest.emit()
        self.block_until_emit(self.unblockWaitSignal)
        text = self._text
        self._text = ""

        return text