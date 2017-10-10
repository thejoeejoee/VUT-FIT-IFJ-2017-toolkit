# coding=utf-8
from collections import namedtuple

TestInfo = namedtuple('TestInfo', "name code stdin stdout compiler_exit_code interpreter_exit_code info")


class TestReport(object):
    compiler_stdout = None
    compiler_stderr = None
    compiler_exit_code = None

    interpreter_stdout = None
    interpreter_stderr = None
    interpreter_exit_code = None


__all__ = ['TestReport', 'TestInfo']
