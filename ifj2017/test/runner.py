# coding=utf-8
import os
import os.path as path
import platform
import shutil
import sys
from subprocess import PIPE, Popen
from tempfile import mktemp

from ifj2017.interpreter.interpreter import Interpreter
from .base import TestInfo
from .base import TestReport
from .loader import TestLoader
from .logger import Logger
from .. import __PROJECT_ROOT__

TEST_LOG_HEADER = """\
# TEST: {}
# INFO: {}
# INTERPRETER STDIN: 
# {}
# 
# COMPILER STDERR:
# {}
# INTERPRETER STDERR:
# {}
#
# EXPECTED INTERPRETER STDOUT:
# {}
# CURRENT INTERPRETER STDOUT:
# {}
#
# EXPECTED COMPILER EXIT CODE: {}
# CURRENT COMPILER EXIT CODE: {}
# EXPECTED INTERPRETER EXIT CODE: {}
# CURRENT INTERPRETER EXIT CODE: {}
# 
"""


class TestRunner(object):
    INTERPRETERS = {
        'Linux': path.join(__PROJECT_ROOT__, 'bin/linux/ic17int'),
        'Windows': path.join(__PROJECT_ROOT__, 'bin/windows/ic17int.exe'),
    }

    def __init__(self, args):
        super(TestRunner, self).__init__()
        assert path.isfile(args.compiler) and os.access(args.compiler, os.X_OK), \
            "Given compiler ({}) is file and is executable.".format(args.compiler)
        assert path.isfile(args.interpreter) and os.access(args.interpreter, os.X_OK), \
            "Given interpreter ({}) is file and is executable.".format(args.interpreter)
        assert isinstance(args.command_timeout, int) and args.command_timeout > 0, \
            'Command timeout is positive int'

        self._compiler_binary = args.compiler
        self._interpreter_binary = args.interpreter
        self._command_timeout = args.command_timeout
        self._log_dir = args.log_dir
        self._loader = TestLoader(args.tests_dir)

        if path.exists(self._log_dir):
            shutil.rmtree(self._log_dir)
        os.mkdir(self._log_dir)

        self._actual_section = None

    def run(self):
        for test_section_dir in self._loader.load_section_dirs():
            self._actual_section = path.basename(test_section_dir)

            Logger.log_section(self._actual_section)
            os.mkdir(path.join(self._log_dir, self._actual_section))
            for test_info in self._loader.load_tests(test_section_dir):
                self._run_test(test_info)
        return 0  # TODO: resolve exit code

    def _run_test(self, test_info):
        report = TestReport()
        Logger.log_test(
            test_info.name,
            ' ({})'.format(
                test_info.info
            ) if test_info.info else None
        )
        report.compiler_stdout, report.compiler_stderr, report.compiler_exit_code = self._compile(test_info.code)

        if test_info.compiler_exit_code is not None:
            if report.compiler_exit_code != test_info.compiler_exit_code:
                Logger.log_test_fail("COMPILER EXIT CODE expected={}, returned={}".format(
                    test_info.compiler_exit_code, report.compiler_exit_code
                ))
                self._save_report(test_info, report)
                return

        Logger.log_test_ok()
        if report.compiler_exit_code != 0:
            # compiler stops this test case
            self._save_report(test_info, report)
            return

        report.interpreter_stdout, report.interpreter_stderr, report.interpreter_exit_code = self._interpret(
            report.compiler_stdout, test_info
        )

        if test_info.interpreter_exit_code is not None:
            if report.interpreter_exit_code != test_info.interpreter_exit_code:
                Logger.log_test_fail("INTERPRETER EXIT CODE expected={}, returned={}".format(
                    test_info.interpreter_exit_code, report.interpreter_exit_code
                ))
                self._save_report(test_info, report)
                return

        if report.interpreter_exit_code != 0:
            # interpreter stops this test case
            self._save_report(test_info, report)
            return

        Logger.log_test_ok()

        if test_info.stdout is not None:
            if report.interpreter_stdout != test_info.stdout:
                Logger.log_test_fail("STDOUT")
                self._save_report(test_info, report)
                return
        Logger.log_test_ok()
        Interpreter(report.compiler_stdout).run()
        self._save_report(test_info, report)

    def _compile(self, code):
        process = Popen([self._compiler_binary], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        out, err = process.communicate(bytes(code, encoding='utf-8'), timeout=self._command_timeout)
        return out.decode('utf-8'), err.decode('utf-8'), process.returncode

    def _interpret(self, code, test_info):
        code_temp = mktemp()
        with open(code_temp, 'wb') as f:
            f.write(bytes(code, encoding='utf-8'))

        process = Popen([self._interpreter_binary, '-v', code_temp], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        out, err = process.communicate(input=bytes(test_info.stdin, encoding='utf-8'), timeout=self._command_timeout)
        os.remove(code_temp)
        return out.decode('utf-8'), err.decode('utf-8'), process.returncode

    def _save_report(self, test_info, report):
        # type: (TestInfo, TestReport) -> None
        replace = lambda s: (s or '').replace('\n', '\n# ')
        with open(
                path.join(
                    self._log_dir,
                    self._actual_section,
                    '.'.join((test_info.name, 'IFJcode17'))
                ),
                'w'
        ) as f:
            f.write(TEST_LOG_HEADER.format(
                test_info.name,
                test_info.info,
                replace(test_info.stdin),

                replace(report.compiler_stderr),
                replace(report.interpreter_stderr),
                replace(test_info.stdout),
                replace(report.interpreter_stdout),

                test_info.compiler_exit_code,
                report.compiler_exit_code,
                test_info.interpreter_exit_code,
                report.interpreter_exit_code,
            ))
            f.write(
                '\n'.join(
                    '# {: 3}: {}'.format(i, line) for i, line in enumerate(test_info.code.split('\n'), start=1)
                )
            )
            f.write('\n' * 2 + '# ' * 20 + '\n' * 2)
            f.write(report.compiler_stdout)
        Logger.log_end_test_case()

    @classmethod
    def check_platform(cls):
        if sys.maxsize <= 2 ** 32:
            Logger.log_warning(
                "Interpreter IFJcode17 requires 64-bit architecture, current is not 64-bit, terminating..."
            )
            return
        system = platform.system()
        if system not in cls.INTERPRETERS:
            Logger.log_warning(
                "Actual platform '{}' is not supported platform, terminating...".format(system)
            )
            return
        return True


__all__ = ['TestRunner']
