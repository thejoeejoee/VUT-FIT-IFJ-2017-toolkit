# coding=utf-8
import re
from typing import Optional, List
from difflib import unified_diff
from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot
from PyQt5.QtCore import QVariant


class DiffCodeAnalyzer(QObject):
    codeChanged = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        self._code = "\n"

    @pyqtProperty(str, notify=codeChanged)
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, v: str) -> None:
        if self._code != v:
            self._code = v
            self.codeChanged.emit(v)

    @pyqtSlot(str, result=QVariant)
    def compare(self, new_code: str) -> QVariant:
        diff_lines = []
        hunk = []

        diff = list(unified_diff(self._code.splitlines(True), new_code.splitlines(True)))[2::]

        for line in diff:
            hunk_info_match = re.match(r'@@ -\d+,?\d* \+\d+,?\d* @@', line)
            if hunk_info_match is not None:
                diff_lines.extend(self._process_hunk(hunk))
                hunk = []
            hunk.append(line)

        if hunk:
            diff_lines.extend(self._process_hunk(hunk))
        return QVariant(diff_lines)


    def _process_hunk(self, hunk: List[str]) -> List[int]:
        if not hunk:
            return []
        hunk_info_match = re.match(r'@@ -(?P<line_start>\d+),?\d* \+\d+,?\d* @@', hunk[0])
        print(hunk)
        line_start = int(hunk_info_match.group('line_start'))
        hunk = hunk[1::]
        # remove removed lines
        hunk = filter(lambda x: x[0] is not '-', hunk)
        diff_lines = [i + line_start for i, v in enumerate(hunk) if v[0] is "+"]
        return diff_lines