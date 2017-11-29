# coding=utf-8
from collections import namedtuple

from ..interpreter.state import State

TestInfo = namedtuple(
    'TestInfo',
    "name code stdin stdout compiler_exit_code interpreter_exit_code info section_dir extensions timeout"
)


class TestReport(object):
    compiler_stdout = None
    compiler_stderr = None
    compiler_exit_code = None

    interpreter_stdout = None
    interpreter_stderr = None
    interpreter_exit_code = None

    state = None  # type: State
    test_info = None  # type: TestInfo

    groot_price = None  # type: TestInfo

    success = None

    skipped = None

__all__ = ['TestReport', 'TestInfo']
