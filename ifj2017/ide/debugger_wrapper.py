# coding=utf-8
from typing import Optional, Union
from PyQt5.QtCore import QObject, pyqtSlot, QVariant, pyqtProperty, pyqtSignal
from PyQt5.QtQml import QJSValue

from ifj2017.ide.io_wrapper import IOWrapper
from ifj2017.ide.core.tree_view_model import TreeViewModel
from ifj2017.interpreter.debugger import Debugger
from ifj2017.interpreter.state import State


class DebuggerWrapper(QObject):
    breakpointsChanged = pyqtSignal(QVariant)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        self._debugger = Debugger()
        self._model = None
        self._io_wrapper = None

    @pyqtProperty(IOWrapper)
    def ioWrapper(self) -> IOWrapper:
        return self._io_wrapper

    @ioWrapper.setter
    def ioWrapper(self, v: IOWrapper) -> None:
        self._io_wrapper = v
        if self._io_wrapper:
            self._debugger._state_kwargs = dict(
                stdout=self._io_wrapper,
                stdin=self._io_wrapper,
                stderr=self._io_wrapper
            )

    @pyqtProperty(TreeViewModel)
    def model(self) -> Union[TreeViewModel, None]:
        return self._model

    @model.setter
    def model(self, v: TreeViewModel) -> None:
        self._model = v
        print(self._model)

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
        print(self._debugger.breakpoints)
        self.breakpointsChanged.emit(self.breakpoints)

    @pyqtSlot(str)
    def debug(self, code: str) -> None:
        self._debugger.debug(code, self._debugger.breakpoints)

    @pyqtSlot(str)
    def run(self, code: str) -> None:
        self._debugger.run(code)

    @pyqtProperty(QVariant, notify=breakpointsChanged)
    def breakpoints(self) -> QVariant:
        return QVariant(list(self._debugger.breakpoints))

    @pyqtSlot()
    def runToNextBreakPoint(self):
        state = self._debugger.run_to_next_breakpoint()

        self.set_model_data(state)

    @pyqtSlot()
    def runToNextLine(self):
        pass

    def set_model_data(self, state: State):
        for var_name, var_value in state.frame("GF").items():
            self._model.add_item("GF", str(var_name), str(var_value), type(var_value).__name__)
