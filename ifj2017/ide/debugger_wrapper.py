# coding=utf-8
from collections import Callable
from operator import itemgetter
from typing import Optional, Union

from PyQt5.QtCore import QObject, pyqtSlot, QVariant, pyqtProperty, pyqtSignal
from PyQt5.QtCore import QThread
from PyQt5.QtQml import QJSValue

from enum import IntEnum

from ifj2017.ide.core.tree_view_model import TreeViewModel
from ifj2017.ide.io_wrapper import IOWrapper
from ifj2017.interpreter.debugger import Debugger
from ifj2017.interpreter.exceptions import InvalidCodeException, BaseInterpreterError
from ifj2017.interpreter.interpreter import Interpreter
from ifj2017.interpreter.state import State


class DebuggerWorker(QThread):
    class CommandType(IntEnum):
        RUN = 1
        DEBUG_RUN = 2
        DEBUG_NEXT_LINE = 3
        DEBUG_NEXT_BREAKPOINT = 4

    programEnded = pyqtSignal()
    stateChanged = pyqtSignal(State, arguments=["state"])
    programEndedWithError = pyqtSignal(str, arguments=["msg"])
    currentLineChanged = pyqtSignal(int, arguments=["line"])

    def __init__(self, debugger, parent: Optional[QObject] = None):
        super().__init__(parent)

        self._debugger = debugger
        self.code = ""
        self.command_type = DebuggerWorker.CommandType.RUN

        self._commands = {
            DebuggerWorker.CommandType.RUN: self._run,
            DebuggerWorker.CommandType.DEBUG_RUN: self._debug_run,
            DebuggerWorker.CommandType.DEBUG_NEXT_LINE: self._debug_next_line,
            DebuggerWorker.CommandType.DEBUG_NEXT_BREAKPOINT: self._debug_next_breakpoint
        }

    def save_interpreter_command(self, command, *args, **kwargs):
        try:
            if isinstance(command, Callable):
                return command(*args, **kwargs), None
        except (InvalidCodeException, BaseInterpreterError) as e:
            return None, str(e)
        return None, None

    def _update_program_line(self, state: State) -> None:
        if self._debugger._interpreter and state:
            self.currentLineChanged.emit(self._debugger._interpreter.program_line(state.program_counter))
        else:
            self.currentLineChanged.emit(-1)

    def _run_debug_command(self, command, *args, **kwargs):
        state, error = self.save_interpreter_command(command, *args, **kwargs)
        self._update_program_line(state)
        if error:
            self.programEndedWithError.emit(error)

        elif not self._check_program_end(state):
            self.stateChanged.emit(state)

    def _debug_next_line(self):
        self._run_debug_command(self._debugger.run_to_next_line)

    def _debug_next_breakpoint(self):
        self._run_debug_command(self._debugger.run_to_next_breakpoint)

    def _debug_run(self):
        self._run_debug_command(self._debugger.debug, self.code, self._debugger.breakpoints)

    def _run(self):
        _, error = self.save_interpreter_command(self._debugger.run, self.code)
        if error:
            self.programEndedWithError.emit(error)
        else:
            self.programEnded.emit()

    def run(self):
        command = self._commands.get(self.command_type, None)
        if command:
            command()

    def _check_program_end(self, state: Union[State, None]) -> bool:
        if state is None:
            self.programEnded.emit()
        return state is None


class DebuggerWrapper(QObject):
    breakpointsChanged = pyqtSignal(QVariant)
    currentLineChanged = pyqtSignal(int, arguments=["line"])
    programEnded = pyqtSignal()
    programEndedWithError = pyqtSignal(str, arguments=["msg"])
    callStackModelChanged = pyqtSignal(QVariant, arguments=["model"])

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        self._debugger = Debugger()
        self._model = None
        self._io_wrapper = None
        self._program_line = -1
        self._call_stack_model = []

        self._init_debug_worker()

    def _init_debug_worker(self):
        self._debugger_worker = DebuggerWorker(self._debugger, self)
        self._debugger_worker.programEnded.connect(self.programEnded)
        self._debugger_worker.programEndedWithError.connect(self.programEndedWithError)
        self._debugger_worker.currentLineChanged.connect(self._update_program_line)
        self._debugger_worker.stateChanged.connect(self._set_model_data)

    @pyqtProperty(QVariant, notify=callStackModelChanged)
    def callStackModel(self) -> QVariant:
        return QVariant(self._call_stack_model)

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

    @pyqtSlot(int)
    def _update_program_line(self, v: int) -> None:
        self._program_line = v
        self.currentLineChanged.emit(v)

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
        self._debugger_worker.command_type = DebuggerWorker.CommandType.DEBUG_RUN
        self._debugger_worker.code = code
        self._debugger_worker.start()

    @pyqtSlot(str)
    def run(self, code: str) -> None:
        self._debugger_worker.command_type = DebuggerWorker.CommandType.RUN
        self._debugger_worker.code = code
        self._debugger_worker.start()

    @pyqtProperty(QVariant, notify=breakpointsChanged)
    def breakpoints(self) -> QVariant:
        return QVariant(list(self._debugger.breakpoints))

    @pyqtProperty(int, notify=currentLineChanged)
    def currentLine(self) -> int:
        return self._program_line

    @pyqtSlot()
    def runToNextBreakpoint(self):
        self._debugger_worker.command_type = DebuggerWorker.CommandType.DEBUG_NEXT_BREAKPOINT
        self._debugger_worker.start()

    @pyqtSlot()
    def runToNextLine(self):
        self._debugger_worker.command_type = DebuggerWorker.CommandType.DEBUG_NEXT_LINE
        self._debugger_worker.start()

    def save_interpreter_command(self, command, *args, **kwargs):
        try:
            if isinstance(command, Callable):
                return command(*args, **kwargs), None
        except (InvalidCodeException, BaseInterpreterError) as e:
            return None, str(e)
        return None, None

    def _set_model_data(self, state: State):
        # frames
        for frame in ("GF", "TF"):
            self._model.clear_sub_tree([], frame)
            if state.frame(frame):
                for var_name, var_value in sorted(state.frame(frame).items(), key=itemgetter(0)):
                    self._model.set_item_data([frame], str(var_name), str(var_value), type(var_value).__name__)

        self._model.clear_sub_tree([], "LF")
        if state.frame_stack:
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
                self._model.set_item_data(["Frame stack", "[{index}]".format(index=i)], str(var_name), str(var_value),
                                          type(var_value).__name__)

        for i in range(len(state.frame_stack), self._model.rowCount(frame_stack_model_item_index)):
            self._model.remove_sub_tree(["Frame stack"], "[{}]".format(i))

        self._model.set_item_data(
            [],
            "Price", '{} ({}+{})'.format(
                state.instruction_price + state.operand_price,
                state.instruction_price,
                state.operand_price
            ),
            ''
        )

        self._call_stack_model = [
            [
                self._debugger._interpreter.program_line(x),
                (
                    self._debugger._interpreter._instructions[x].op0.label
                 if x != state.program_counter
                    else None
                ) or ''
            ]
            for x in state.call_stack + [state.program_counter]
            ][::-1]
        self.callStackModelChanged.emit(QVariant(self._call_stack_model))

    @pyqtSlot()
    def stop(self):
        self._debugger.stop()
        self._io_wrapper.unblockWaitSignal.emit()
        self._program_line = -1
        self._model.clear()
        self._call_stack_model = []
        self.callStackModelChanged.emit(QVariant(self._call_stack_model))
        self.currentLineChanged.emit(-1)
