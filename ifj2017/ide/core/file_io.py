# coding=utf-8
from typing import Optional
from platform import system
from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot
from collections import defaultdict

FILE_PREFIX = defaultdict(lambda: "file://", **{
    "Windows": "file:///",
    "Linux": "file://",
    "Darwin": "file://"
})

class FileIO(QObject):
    sourceChanged = pyqtSignal(str, arguments=["source"])

    def __init__(self, parent: Optional[QObject]):
        super().__init__(parent)

        self._source = ""

    @staticmethod
    def removeFilePrefix(path: str) -> str:
        return path.replace(FILE_PREFIX[system()], "")

    @pyqtProperty(str, notify=sourceChanged)
    def source(self) -> str:
        return self._source

    @source.setter
    def source(self, v: str) -> None:
        if self._source != v:
            self._source = FileIO.removeFilePrefix(v)
            self.sourceChanged.emit(v)

    @pyqtSlot(str)
    def write(self, content: str) -> None:
        if not self._source:
            return

        with open(self._source, "wb") as f:
            f.write(bytes(content, encoding='utf-8'))

    @pyqtSlot(result=str)
    def read(self) -> str:
        if not self._source:
            return ""

        with open(self._source, "rb") as f:
            read_data = f.read()
        return str(read_data, encoding='utf-8')