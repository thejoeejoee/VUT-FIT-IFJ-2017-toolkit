# coding=utf-8
from typing import Optional
from platform import system
from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot
from collections import defaultdict

FILE_PREFIX = defaultdict(lambda: "file://", **{
    "Windows": "file:///",
    "Linux": "file://"
})

class FileIO(QObject):
    sourceChanged = pyqtSignal()

    def __init__(self, parent: Optional[QObject]):
        super().__init__(parent)

        self._source = ""

    @pyqtProperty(str, notify=sourceChanged)
    def source(self) -> str:
        return self._source

    @source.setter
    def source(self, v: str) -> None:
        if self._source != v:
            self._source = v.replace(FILE_PREFIX[system()], "")
            self.sourceChanged.emit()

    @pyqtSlot(str)
    def write(self, content: str) -> None:
        if not self._source:
            return

        with open(self._source, "w") as f:
            f.write(content)

    @pyqtSlot(result=str)
    def read(self) -> str:
        if not self._source:
            return ""

        with open(self._source, "r") as f:
            read_data = f.read()
        return read_data