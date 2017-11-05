# coding=utf-8
from operator import itemgetter
from typing import Optional, Union
from PyQt5.QtCore import QObject, pyqtSlot, QVariant, pyqtProperty, pyqtSignal
from PyQt5.QtQml import QJSValue

from ifj2017.ide.io_wrapper import IOWrapper
from ifj2017.ide.core.tree_view_model import TreeViewModel
from ifj2017.interpreter.debugger import Debugger
from ifj2017.interpreter.state import State


class DebuggerWrapper(QObject):
    breakpointsChanged = pyqtSignal(QVariant)
    currentLineChanged = pyqtSignal(int, arguments=["line"])
    programEnded = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        self._debugger = Debugger()
        self._model = None
        self._io_wrapper = None
        self._program_line = -1

    def _check_program_end(self, state: Union[State, None]) -> bool:
        if state is None:
            self.programEnded.emit()
        return state is None

    def _update_program_line(self, state: State) -> None:
        if self._debugger._interpreter:
            self._program_line = self._debugger._interpreter.program_line(state)
        else:
            self._program_line = -1
        self.currentLineChanged.emit(self._program_line)

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
        self.breakpointsChanged.emit(self.breakpoints)

    @pyqtSlot(str)
    def debug(self, code: str) -> None:
        state = self._debugger.debug(code, self._debugger.breakpoints)
        self._update_program_line(state)
        self.set_model_data(state)

    @pyqtSlot(str)
    def run(self, code: str) -> None:
        self._debugger.run(code)
        self.programEnded.emit()

    @pyqtProperty(QVariant, notify=breakpointsChanged)
    def breakpoints(self) -> QVariant:
        return QVariant(list(self._debugger.breakpoints))

    @pyqtProperty(int, notify=currentLineChanged)
    def currentLine(self) -> int:
        return self._program_line

    @pyqtSlot()
    def runToNextBreakpoint(self):
        state = self._debugger.run_to_next_breakpoint()
        if self._check_program_end(state):
            return

        self._update_program_line(state)
        self.set_model_data(state)

    @pyqtSlot()
    def runToNextLine(self):
        state = self._debugger.run_to_next_line()
        if self._check_program_end(state):
            return

        self._update_program_line(state)
        self.set_model_data(state)

    def set_model_data(self, state: State):
        for var_name, var_value in sorted(state.frame("GF").items(), key=itemgetter(0)):
            self._model.add_item("GF", str(var_name), str(var_value), type(var_value).__name__)

    @pyqtSlot()
    def stop(self):
        self._io_wrapper.unblockWaitSignal.emit()
        self._debugger.stop()
        self._program_line = -1
        self._model.clear()
        self.currentLineChanged.emit(-1)