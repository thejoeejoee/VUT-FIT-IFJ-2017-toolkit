# coding=utf-8
from operator import itemgetter
from typing import Optional, Union
from collections import Callable
from PyQt5.QtCore import QObject, pyqtSlot, QVariant, pyqtProperty, pyqtSignal
from PyQt5.QtQml import QJSValue

from ifj2017.interpreter.exceptions import InvalidCodeException, BaseInterpreterError
from ifj2017.ide.io_wrapper import IOWrapper
from ifj2017.ide.core.tree_view_model import TreeViewModel
from ifj2017.interpreter.debugger import Debugger
from ifj2017.interpreter.state import State


class DebuggerWrapper(QObject):
    breakpointsChanged = pyqtSignal(QVariant)
    currentLineChanged = pyqtSignal(int, arguments=["line"])
    programEnded = pyqtSignal()
    programEndedWithError = pyqtSignal(str, arguments=["msg"])

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
        state, error = self.save_interpreter_command(self._debugger.debug, code, self._debugger.breakpoints)
        if error:
            self.programEndedWithError.emit(error)

        elif not self._check_program_end(state):
            self._update_program_line(state)
            self.set_model_data(state)

    @pyqtSlot(str)
    def run(self, code: str) -> None:
        _, error = self.save_interpreter_command(self._debugger.run, code)
        if error:
            self.programEndedWithError.emit(error)
        else:
            self.programEnded.emit()

    @pyqtProperty(QVariant, notify=breakpointsChanged)
    def breakpoints(self) -> QVariant:
        return QVariant(list(self._debugger.breakpoints))

    @pyqtProperty(int, notify=currentLineChanged)
    def currentLine(self) -> int:
        return self._program_line

    @pyqtSlot()
    def runToNextBreakpoint(self):
        state, error = self.save_interpreter_command(self._debugger.run_to_next_breakpoint)
        if error:
            self.programEndedWithError.emit(error)

        elif not self._check_program_end(state):
            self._update_program_line(state)
            self.set_model_data(state)

    @pyqtSlot()
    def runToNextLine(self):
        state, error = self.save_interpreter_command(self._debugger.run_to_next_line)
        if error:
            self.programEndedWithError.emit(error)

        elif not self._check_program_end(state):
            self._update_program_line(state)
            self.set_model_data(state)

    def save_interpreter_command(self, command, *args, **kwargs):
        try:
            if isinstance(command, Callable):
                return command(*args, **kwargs), None
        except (InvalidCodeException, BaseInterpreterError) as e:
            return None, str(e)
        return None, None

    def set_model_data(self, state: State):
        # frames
        for frame in ["GF", "TF"]:
            if state.frame(frame):
                self._model.clear_sub_tree([], frame)
                for var_name, var_value in sorted(state.frame(frame).items(), key=itemgetter(0)):
                    self._model.set_item_data([frame], str(var_name), str(var_value), type(var_value).__name__)
        if len(state.frame_stack):
            self._model.clear_sub_tree([], "LF")
            for var_name, var_value in sorted(state.frame("LF").items(), key=itemgetter(0)):
                self._model.set_item_data(["LF"], str(var_name), str(var_value), type(var_value).__name__)

        # data stack
        self._model.clear_sub_tree([], "Data stack")
        for i, value in enumerate(state.data_stack[::-1]):
            self._model.set_item_data(["Data stack"], "[{index}]".format(index=i), str(value), type(value).__name__)

        # frames stack9
        frame_stack_model_item_index = self._model.get_item([], "Frame stack").index()
        for i, frame in enumerate(state.frame_stack[::-1]):
            self._model.clear_sub_tree(["Frame stack"], "[{}]".format(i))
            for var_name, var_value in sorted(frame.items(), key=itemgetter(0)):
                self._model.set_item_data(["Frame stack", "[{index}]".format(index=i)], str(var_name), str(var_value), type(var_value).__name__)

        for i in range(len(state.frame_stack), self._model.rowCount(frame_stack_model_item_index)):
            self._model.remove_sub_tree(["Frame stack"], "[{}]".format(i))



    @pyqtSlot()
    def stop(self):
        self._debugger.stop()
        self._io_wrapper.unblockWaitSignal.emit()
        self._program_line = -1
        self._model.clear()
        self.currentLineChanged.emit(-1)