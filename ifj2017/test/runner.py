# coding=utf-8
import difflib
import os
import os.path as path
import platform
import shutil
from datetime import datetime
from io import StringIO
from os.path import basename, abspath, isfile, dirname
from subprocess import PIPE, Popen, TimeoutExpired
from tempfile import mktemp

import ifj2017
from .base import TestInfo
from .base import TestReport
from .loader import TestLoader
from .logger import TestLogger
from .. import __PROJECT_ROOT__
from ..benchmark.uploader import BenchmarkUploader
from ..interpreter.interpreter import Interpreter

TEST_LOG_HEADER = """\
# {}
# SECTION: {}
# TEST: {}
# INFO: {}
# REQUIRED EXTENSIONS: {}
# ACTIVATED EXTENSIONS: {}
# STATE: {}
# 
# COMPILER STDERR:
# {}
# INTERPRETER STDERR:
# {}
# {}
# INTERPRETER STDIN: 
# {}
#
# EXPECTED COMPILER EXIT CODE: {}
# CURRENT COMPILER EXIT CODE: {}
# EXPECTED INTERPRETER EXIT CODE: {}
# CURRENT INTERPRETER EXIT CODE: {}
# PRICE: {}
# GROOT: {}
# 
"""

_STDOUT_TWICE = """\
EXPECTED INTERPRETER STDOUT:

{}

# CURRENT INTERPRETER STDOUT:

{}
"""
_STDOUT_DIFF = """\
STDOUT DIFF:
# {}
"""


class TestRunner(object):
    INTERPRETERS = {
        'Linux': path.join(__PROJECT_ROOT__, 'ifj2017/bin/linux/ic17int'),
        'Darwin': path.join(__PROJECT_ROOT__, 'ifj2017/bin/linux/ic17int'),
        'Windows': path.join(__PROJECT_ROOT__, 'ifj2017/bin/windows/ic17int.exe'),
    }
    EXTENSION_FILE_NAME = 'rozsireni'

    def __init__(self, args):
        super(TestRunner, self).__init__()
        assert path.isfile(args.compiler) and os.access(args.compiler, os.X_OK), \
            "Given compiler ({}) is file and is executable.".format(args.compiler)
        assert args.no_interpreter or (path.isfile(args.interpreter) and os.access(args.interpreter, os.X_OK)), \
            "Given interpreter ({}) is file and is executable.".format(args.interpreter)
        assert isinstance(args.command_timeout, float) and args.command_timeout > 0, \
            'Command timeout is positive int'

        self._compiler_binary = args.compiler
        self._interpreter_binary = args.interpreter
        self._command_timeout = args.command_timeout
        self._log_dir = args.log_dir
        self._no_interpreter = args.no_interpreter
        self._loader = TestLoader(
            args.tests_dir,
            args.command_timeout,
            args.tests
        )
        self._extensions_auto_loaded_from = False
        self._extensions = self._try_load_extensions(args.extensions_file, args.compiler)
        if args.no_colors:
            TestLogger.disable_colors = args.no_colors
        TestLogger.verbose = args.verbose
        self._no_stdout_diff = args.no_stdout_diff
        self._reports = []

        if not self._log_dir:
            self._log_dir = os.path.join(dirname(abspath(self._compiler_binary)), 'log')

        token_file = args.token_file or os.path.join(self._log_dir, '.TOKEN')
        self._uploader = BenchmarkUploader(
            args.benchmark_url_target,
            token_file
        )

        if path.exists(self._log_dir):
            for root, dirs, files in os.walk(self._log_dir):
                for f in files:
                    file_path = os.path.join(root, f)
                    if file_path != token_file:
                        os.unlink(file_path)
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
        else:
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

        self._run_tests()
        result = TestLogger.log_results(self._reports)
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
        if self._uploader.version != ifj2017.version:
            TestLogger.log_warning(
                'Outdated package version, actual version on PyPI is {}.'.format(self._uploader.version)
            )
        return result

    def _run_tests(self):
        for test_section_dir in self._loader.load_section_dirs():
            self._actual_section = path.basename(test_section_dir)

            TestLogger.log_section(self._actual_section)
            os.mkdir(path.join(self._log_dir, self._actual_section))
            for test_info in self._loader.load_tests(test_section_dir):
                self._run_test(test_info)

    def _run_test(self, test_info):
        report = TestReport()
        report.test_info = test_info
        report.skipped = None
        TestLogger.log_test(
            test_info.name,
            ' ({})'.format(
                test_info.info.strip().rstrip('.').lower()
            ) if test_info.info else None
        )
        if test_info.extensions - self._extensions:
            TestLogger.log(TestLogger.GREEN, ' skipping, required extension(s) {} is not activated.'.format(
                ', '.join(test_info.extensions - self._extensions)
            ), end=False)
            report.success = None
            report.skipped = True
            self._save_report(test_info, report)
            return

        try:
            report.compiler_stdout, report.compiler_stderr, report.compiler_exit_code = self._compile(test_info)
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
        if report.compiler_exit_code != 0 or self._no_interpreter:
            # compiler stops this test case
            report.success = True
            self._save_report(test_info, report)
            return

        try:
            self._interpret(report, test_info)
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
            report.success = True
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
        else:
            TestLogger.log_price(state=state, groot_price=report.groot_price)
            self._uploader.collect_report(report)
        report.success = True
        self._save_report(test_info, report)

    def _compile(self, test_info):
        # type: (TestInfo) -> tuple
        process = Popen([self._compiler_binary], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        try:
            out, err = process.communicate(bytes(test_info.code, encoding='utf-8'), timeout=test_info.timeout)
        except (TimeoutError, TimeoutExpired):
            process.kill()
            raise
        return out.decode('raw_unicode_escape'), err.decode('raw_unicode_escape'), process.returncode

    def _interpret(self, report: TestReport, test_info: TestInfo) -> None:
        code_temp = mktemp()
        # add GROOT at the end to compute price
        with open(code_temp, 'wb') as f:
            f.write(bytes('\n'.join((report.compiler_stdout, 'GROOT')), encoding='utf-8'))

        process = Popen([self._interpreter_binary, '-v', code_temp], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        try:
            out, err = process.communicate(
                input=bytes(test_info.stdin, encoding='utf-8'),
                timeout=test_info.timeout
            )
        except (TimeoutError, TimeoutExpired):
            process.kill()
            raise
        finally:
            os.remove(code_temp)
        out, err, exit_code = out.decode('raw_unicode_escape'), err.decode('raw_unicode_escape'), process.returncode

        try:
            groot = err.splitlines()[-1]
            report.groot_price = int(groot[groot.find('(') + 1:groot.find(')')])
        except (IndexError, ValueError):
            pass

        # err has non-escaped characters
        report.interpreter_stdout, report.interpreter_stderr, report.interpreter_exit_code = out, err, exit_code

    def _interpret_price(self, code, test_info):
        interpreter = Interpreter(code=code, state_kwargs=dict(
            stdin=StringIO(test_info.stdin),
        ))
        state = interpreter.run()
        return state

    def _save_report(self, test_info, report):
        # type: (TestInfo, TestReport) -> None
        replace = lambda s: (s or '').replace('\n', '\n# ')
        with open(
                path.join(
                    self._log_dir,
                    self._actual_section,
                    '.'.join((test_info.name, 'IFJcode17'))
                ),
                'wb'
        ) as f:
            write = lambda v: f.write(bytes(v, encoding="utf-8"))
            write(TEST_LOG_HEADER.format(
                datetime.now(),
                basename(test_info.section_dir),
                test_info.name,
                test_info.info,
                ', '.join(test_info.extensions),
                ', '.join(self._extensions),
                'SUCCESS' if report.success else 'FAIL',

                replace(report.compiler_stderr),
                replace(report.interpreter_stderr),
                self._stdout_log(test_info.stdout, report.interpreter_stdout),
                replace(test_info.stdin),

                test_info.compiler_exit_code,
                report.compiler_exit_code,
                test_info.interpreter_exit_code,
                report.interpreter_exit_code,
                '{} ({}+{})'.format(
                    report.state.price,
                    report.state.instruction_price,
                    report.state.operand_price
                ) if report.state else '---',
                report.groot_price if report.groot_price is not None else '---'
            ))
            write(
                '\n'.join(
                    '# {: 3}: {}'.format(i, line) for i, line in enumerate(test_info.code.splitlines(), start=1)
                )
            )
            write('\n' * 2 + '#' * 40 + '\n' * 2)
            lines = (report.compiler_stdout or '').splitlines()
            count = len(lines)
            write('\n'.join(
                '{:80}# {:5}/{}'.format(line, i, count)
                for i, line
                in enumerate(lines, start=1)
                if line
            ) or '# ---')
            write('\n' * 2)
        self._reports.append(report)
        TestLogger._test_case_success = report.success
        TestLogger._test_case_skipped = report.skipped
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

    def _welcome_message(self):
        TestLogger.log(
            TestLogger.BLUE,
            TestLogger.BOLD,
            "Welcome to automatic test runner for IFJ17 compiler {} "
            "(https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-tests).".format(ifj2017.__version__)
        )
        if self._extensions:
            TestLogger.log(
                TestLogger.GREEN,
                TestLogger.BOLD,
                "Activated extensions: {}{}.".format(
                    ', '.join(sorted(self._extensions)),
                    ' from {}'.format(self._extensions_auto_loaded_from)
                    if self._extensions_auto_loaded_from else ''
                ),
            )
        if self._no_interpreter:
            TestLogger.log(
                TestLogger.WARNING,
                TestLogger.UNDERLINE,
                TestLogger.BOLD,
                "WARNING: Running without interpreter - without STDOUT check."
            )

    def _try_load_extensions(self, extensions_file, compiler_path):
        if not extensions_file:
            alt_paths = tuple(path_ for path_ in (
                abspath(path.join(path.dirname(compiler_path), self.EXTENSION_FILE_NAME)),
                abspath(path.join(path.dirname(compiler_path), '..', self.EXTENSION_FILE_NAME)),
                abspath(path.join(path.dirname(compiler_path), '../..', self.EXTENSION_FILE_NAME)),
            ) if isfile(path_) and os.access(path_, os.R_OK))
            if not alt_paths:
                return set()

            extensions_file = alt_paths[0]
            self._extensions_auto_loaded_from = extensions_file

        if not path.isfile(extensions_file):
            TestLogger.log_warning(
                "File '{}' is not file or is not readable, assuming none of extensions.".format(extensions_file)
            )
            return set()
        extensions = TestLoader.load_file(extensions_file, allow_fail=False)
        return set(extensions.strip().split())

    def _stdout_log(self, stdout, interpreter_stdout):
        # type: (str, str) -> str
        if self._no_stdout_diff or not stdout or not interpreter_stdout:
            return _STDOUT_TWICE.format(
                ''.join('# {}\n'.format(line) for line in (stdout or '').splitlines()),
                ''.join('# {}\n'.format(line) for line in (interpreter_stdout or '').splitlines()),
            )

        diff = tuple(difflib.unified_diff(
            stdout.splitlines(True),
            interpreter_stdout.splitlines(True),
            fromfile='expected',
            tofile='actual',
        ))

        return _STDOUT_DIFF.format(''.join((
            '# '.join('{}'.format(line) for line in diff[:3]),
            ''.join('\n# {}'.format(line) for line in diff[3:]),
        )))


__all__ = ['TestRunner']
