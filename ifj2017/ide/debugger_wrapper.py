# coding=utf-8
from typing import Optional
from PyQt5.QtCore import QObject, pyqtSlot, QVariant, pyqtProperty, pyqtSignal
from PyQt5.QtQml import QJSValue

from ifj2017.interpreter.debugger import Debugger


class DebuggerWrapper(QObject):
    breakpointsChanged = pyqtSignal(QVariant)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        self._debugger = Debugger()

    @pyqtSlot(QJSValue)
    def handleRemovedLines(self, lines: QJSValue) -> None:
        lines = lines.toVariant()
        breakpoints = self._debugger.breakpoints
        
        for removed_line in lines:
            if removed_line in breakpoints:
                breakpoints.remove(removed_line)
            breakpoints = set(x if x < removed_line else int(x) - 1 for x in breakpoints)

        self._debugger.breakpoints = breakpoints
        self.breakpointsChanged.emit(self.breakpoints)

    @pyqtSlot(QJSValue)
    def handleAddedLines(self, lines: QJSValue) -> None:
        lines = lines.toVariant()
        breakpoints = self._debugger.breakpoints

        for added_line in lines:
            breakpoints = set(x if x < added_line else int(x) + 1 for x in breakpoints)
        self._debugger.breakpoints = breakpoints
        self.breakpointsChanged.emit(self.breakpoints)

    @pyqtSlot(int)
    def toggleBreakpoint(self, line: int) -> None:
        breakpoints = self._debugger.breakpoints

        if line in breakpoints:
            self._debugger.remove_breakpoint(line)
        else:
            self._debugger.add_breakpoint(line)
        self.breakpointsChanged.emit(self.breakpoints)

    @pyqtSlot(str)
    def debug(self, code: str) -> None:
        self._debugger.debug(code)

    @pyqtSlot(str)
    def run(self, code: str) -> None:
        self._debugger.run(code)

    @pyqtProperty(QVariant, notify=breakpointsChanged)
    def breakpoints(self) -> QVariant:
        return QVariant(list(self._debugger.breakpoints))

    @pyqtSlot()
    def runToNextBreakPoint(self):
        pass

    @pyqtSlot()
    def runToNextLine(self):
        pass