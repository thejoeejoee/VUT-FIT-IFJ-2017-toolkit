# coding=utf-8
import re
from typing import Optional, List, Tuple
from difflib import unified_diff
from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot
from PyQt5.QtCore import QVariant


class DiffCodeAnalyzer(QObject):
    codeChanged = pyqtSignal(str)
    removedLines = pyqtSignal(QVariant, arguments=["lines"])
    addedLines = pyqtSignal(QVariant, arguments=["lines"])

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        self._code = "\n"
        self._temp_code = "\n"

    @pyqtSlot(str)
    def saveTempCode(self, code: str) -> None:
        self._temp_code = code

    @pyqtProperty(str, notify=codeChanged)
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, v: str) -> None:
        if self._code != v:
            self._code = v
            self.codeChanged.emit(v)

    def _get_lines_diffs(self, new_code: str) -> Tuple[List[int], List[int]]:
        added_lines = []
        removed_lines = []
        hunk = []

        temp_code_diff = list(unified_diff(self._temp_code.splitlines(True), new_code.splitlines(True)))[2::]

        for line in temp_code_diff:
            hunk_info_match = re.match(r'@@ -\d+,?\d* \+\d+,?\d* @@', line)
            if hunk_info_match is not None:
                hunk_added_lines, hunk_removed_lines = self._get_line_hunk_diffs(hunk)
                added_lines.extend(hunk_added_lines)
                removed_lines.extend(hunk_removed_lines)

                hunk = []
            hunk.append(line)

        if hunk:
            hunk_added_lines, hunk_removed_lines = self._get_line_hunk_diffs(hunk)
            added_lines.extend(hunk_added_lines)
            removed_lines.extend(hunk_removed_lines)

        return added_lines, removed_lines

    @pyqtSlot(str, result=QVariant)
    def compare(self, new_code: str) -> QVariant:
        diff_lines = []
        hunk = []

        diff = list(unified_diff(self._code.splitlines(True), new_code.splitlines(True)))[2::]
        temp_code_diff = list(unified_diff(self._temp_code.splitlines(True), new_code.splitlines(True)))[2::]

        for line in diff:
            hunk_info_match = re.match(r'@@ -\d+,?\d* \+\d+,?\d* @@', line)
            if hunk_info_match is not None:
                diff_lines.extend(self._get_modified_lines(hunk))
                hunk = []
            hunk.append(line)

        if hunk:
            diff_lines.extend(self._get_modified_lines(hunk))

        added_lines, removed_lines = self._get_lines_diffs(new_code)

        if added_lines:
            self.addedLines.emit(QVariant(added_lines))
        if removed_lines:
            self.removedLines.emit(QVariant(removed_lines))

        return QVariant(diff_lines)

    def _get_modified_lines(self, hunk: List[str]) -> List[int]:
        if not hunk:
            return []
        hunk_info_match = re.match(r'@@ -(?P<line_start>\d+),?\d* \+\d+,?\d* @@', hunk[0])
        line_start = int(hunk_info_match.group('line_start'))
        raw_hunk = hunk[1::]
        # remove removed lines
        raw_hunk = filter(lambda x: x[0] is not '-', raw_hunk)
        diff_lines = [i + line_start for i, v in enumerate(raw_hunk) if v[0] is "+"]
        return diff_lines

    def _get_line_hunk_diffs(self, hunk: List[str]) -> Tuple[List[int], List[int]]:
        if not hunk:
            return [], []

        hunk_info_match = re.match(r'@@ -(?P<line_start>\d+),?\d* \+\d+,?\d* @@', hunk[0])
        line_start = int(hunk_info_match.group('line_start'))
        raw_hunk = hunk[1::]    # remove header

        line_mod_marks = ''.join([line[0] for line in raw_hunk])

        regexp = re.compile(r'-\|*\+')
        match = regexp.search(line_mod_marks)

        # keep only added or removed lines
        while match is not None:
            span_start, span_end = match.span()
            mods_count = match.group().count('|')
            line_mod_marks = ''.join(
                [line_mod_marks[0:span_start:], "|" * (mods_count + 1), line_mod_marks[span_end::]])
            match = regexp.search(line_mod_marks)

        removed_lines = [i + line_start for i, v in enumerate(line_mod_marks) if v is "-"]
        added_lines = [i + line_start for i, v in enumerate(line_mod_marks) if v is "+"]

        return added_lines, removed_lines
