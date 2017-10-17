# coding=utf-8
import logging
import os
import os.path as path
import platform
import shutil
from io import StringIO
from subprocess import PIPE, Popen, TimeoutExpired
from tempfile import mktemp

from os.path import basename

from .base import TestInfo
from .base import TestReport
from .loader import TestLoader
from .logger import TestLogger
from .. import __PROJECT_ROOT__
from ..benchmark.uploader import BenchmarkUploader
from ..interpreter.interpreter import Interpreter

TEST_LOG_HEADER = """\
# SECTION: {}
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
        assert isinstance(args.command_timeout, float) and args.command_timeout > 0, \
            'Command timeout is positive int'

        self._compiler_binary = args.compiler
        self._interpreter_binary = args.interpreter
        self._command_timeout = args.command_timeout
        self._log_dir = args.log_dir
        self._loader = TestLoader(args.tests_dir)
        if args.no_colors:
            TestLogger.disable_colors = args.no_colors
        self._reports = []
        self._uploader = BenchmarkUploader(args.benchmark_url_target)

        if path.exists(self._log_dir):
            shutil.rmtree(self._log_dir)
        os.mkdir(self._log_dir)

        self._actual_section = None

    def run(self):
        self._welcome_message()
        self._uploader.check_connection()
        try:
            self._uploader.authenticate_user()
        except Exception as e:
            TestLogger.log_warning('Unable to authenticate user ({}), terminating...'.format(e))
            return 1

        for test_section_dir in self._loader.load_section_dirs():
            self._actual_section = path.basename(test_section_dir)

            TestLogger.log_section(self._actual_section)
            os.mkdir(path.join(self._log_dir, self._actual_section))
            for test_info in self._loader.load_tests(test_section_dir):
                self._run_test(test_info)

        if self._uploader.has_connection:
            try:
                response = self._uploader.send_reports()
                if not response.get('success'):
                    TestLogger.log_warning(
                        'Server fail with saving result ({}), terminating...'.format(response.get('message'))
                    )
            except Exception as e:
                TestLogger.log_warning('Unable to send reports ({}), terminating...'.format(e))
        else:
            TestLogger.log_warning('Results upload skipped.')

        return TestLogger.log_results(self._reports)

    def _run_test(self, test_info):
        report = TestReport()
        report.test_info = test_info
        TestLogger.log_test(
            test_info.name,
            ' ({})'.format(
                test_info.info
            ) if test_info.info else None
        )
        try:
            report.compiler_stdout, report.compiler_stderr, report.compiler_exit_code = self._compile(test_info.code)
        except (TimeoutExpired, TimeoutError) as e:
            TestLogger.log_test_fail('COMPILER TIMEOUT')
            report.success = False
            self._save_report(test_info, report)
            return
        except Exception as e:
            TestLogger.log_test_fail('FAIL TO RUN COMPILER ({})'.format(e))
            report.success = False
            self._save_report(test_info, report)
            return

        if test_info.compiler_exit_code is not None:
            if report.compiler_exit_code != test_info.compiler_exit_code:
                TestLogger.log_test_fail("COMPILER EXIT CODE expected={}, returned={}".format(
                    test_info.compiler_exit_code, report.compiler_exit_code
                ))
                report.success = False
                self._save_report(test_info, report)
                return

        TestLogger.log_test_ok()
        if report.compiler_exit_code != 0:
            # compiler stops this test case
            self._save_report(test_info, report)
            return

        try:
            report.interpreter_stdout, report.interpreter_stderr, report.interpreter_exit_code = self._interpret(
                report.compiler_stdout, test_info
            )
        except (TimeoutExpired, TimeoutError) as e:
            TestLogger.log_test_fail('INTERPRETER TIMEOUT')
            report.success = False
            self._save_report(test_info, report)
            return
        except Exception as e:
            TestLogger.log_test_fail('FAIL TO RUN INTERPRETER ({})'.format(e))
            report.success = False
            self._save_report(test_info, report)
            return

        if test_info.interpreter_exit_code is not None:
            if report.interpreter_exit_code != test_info.interpreter_exit_code:
                TestLogger.log_test_fail("INTERPRETER EXIT CODE expected={}, returned={}".format(
                    test_info.interpreter_exit_code, report.interpreter_exit_code
                ))
                report.success = False
                self._save_report(test_info, report)
                return

        if report.interpreter_exit_code != 0:
            # interpreter stops this test case
            self._save_report(test_info, report)
            return

        TestLogger.log_test_ok()

        if test_info.stdout is not None:
            if report.interpreter_stdout != test_info.stdout:
                TestLogger.log_test_fail("STDOUT")
                report.success = False
                self._save_report(test_info, report)
                return
        TestLogger.log_test_ok()

        try:
            state = self._interpret_price(report.compiler_stdout, test_info)
            report.state = state
        except Exception as e:
            TestLogger.log(TestLogger.WARNING, ' (fail: {})'.format(e))
            logging.exception(e, exc_info=True)
        else:
            TestLogger.log_price(state=state)
            self._uploader.collect_report(report)
        self._save_report(test_info, report)

    def _compile(self, code):
        process = Popen([self._compiler_binary], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        try:
            out, err = process.communicate(bytes(code, encoding='utf-8'), timeout=self._command_timeout)
        except (TimeoutError, TimeoutExpired):
            process.kill()
            raise
        return out.decode('ascii'), err.decode('ascii'), process.returncode

    def _interpret(self, code, test_info):
        code_temp = mktemp()
        with open(code_temp, 'wb') as f:
            f.write(bytes(code, encoding='utf-8'))

        process = Popen([self._interpreter_binary, '-v', code_temp], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        try:
            out, err = process.communicate(input=bytes(test_info.stdin, encoding='utf-8'),
                                           timeout=self._command_timeout)
        except (TimeoutError, TimeoutExpired):
            process.kill()
            raise
        finally:
            os.remove(code_temp)
        # err has non-escaped characters
        return out.decode('ascii'), err.decode('unicode_escape'), process.returncode

    def _interpret_price(self, code, test_info):
        interpreter = Interpreter(code=code, stdin=StringIO(test_info.stdin))
        return interpreter.run()

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
                basename(test_info.section_dir),
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
            f.write('\n' * 2 + '#' * 40 + '\n' * 2)
            f.write(report.compiler_stdout or '# ---')
        self._reports.append(report)
        TestLogger.log_end_test_case()

    @classmethod
    def check_platform(cls):
        system = platform.system()
        if system not in cls.INTERPRETERS:
            TestLogger.log_warning(
                "Actual platform '{}' is not supported platform, terminating...".format(system)
            )
            return
        return True

    @staticmethod
    def _welcome_message():
        TestLogger.log(
            TestLogger.BLUE,
            TestLogger.BOLD,
            "Welcome to automatic test runner for IFJ17 compiler "
            "(https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-tests)."
        )


__all__ = ['TestRunner']
