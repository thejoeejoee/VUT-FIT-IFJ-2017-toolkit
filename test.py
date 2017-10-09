#!/usr/bin/env python3
# coding=utf-8
import os
from argparse import ArgumentParser
from collections import namedtuple
from glob import iglob
from os import path
from subprocess import Popen, PIPE
from sys import stderr
from tempfile import mktemp

__DIR__ = path.abspath(path.dirname(__file__))

TestInfo = namedtuple('TestInfo', "name code stdin stdout compiler_exit_code interpreter_exit_code")


class Logger(object):
    BLUE = '\033[94m'
    GREEN = '\033[32m'  # green
    WARNING = '\033[93m'
    HEADER = '\033[95m'
    FAIL = '\033[91m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @classmethod
    def log(cls, *args, stream=stderr, end=True, indent=0):
        stream.write('\t' * indent)
        stream.write(''.join(map(str, filter(None, args))))
        stream.write(cls.END)
        if end:
            stream.write('\n')

    @classmethod
    def log_section(cls, section):
        Logger.log(Logger.BLUE, "SECTION ", Logger.UNDERLINE, section)

    @classmethod
    def log_test(cls, name):
        Logger.log(Logger.BOLD, 'TEST ', name, indent=1)

    @classmethod
    def log_test_step(cls, step):
        Logger.log(Logger.BLUE, step, '...', indent=2)

    @classmethod
    def log_test_fail(cls, result):
        cls.log(Logger.BOLD, Logger.WARNING, '× ', result, indent=3)

    @classmethod
    def log_test_ok(cls):
        cls.log(Logger.GREEN, Logger.BOLD, '✓ OK', indent=3)


class TestRunner(object):
    def __init__(self, args):
        super(TestRunner, self).__init__()
        assert path.isdir(args.tests_dir), "Given tests dir is valid filesystem folder."
        assert path.isfile(args.compiler) and os.access(args.compiler, os.X_OK), \
            "Given compiler ({}) is file and is executable.".format(args.compiler)
        assert path.isfile(args.interpreter) and os.access(args.interpreter, os.X_OK), \
            "Given interpreter ({}) is file and is executable.".format(args.interpreter)

        self._tests_dir = args.tests_dir
        self._compiler_binary = args.compiler
        self._interpreter_binary = args.interpreter

    def run(self):
        for test_section in self.test_sections:
            Logger.log_section(path.basename(test_section))
            for test_info in self.find_tests(test_section):
                self._run_test(test_info)

    def _run_test(self, test_info):
        Logger.log_test(test_info.name)
        Logger.log_test_step('Compiling')
        compiler_out, compiler_err, compiler_exit_code = self._compile(test_info.code)

        if test_info.compiler_exit_code is not None:
            if compiler_exit_code != test_info.compiler_exit_code:
                Logger.log_test_fail("COMPILER EXIT CODE FAIL, expected={}, returned={}".format(
                    test_info.compiler_exit_code, compiler_exit_code
                ))
                return

        Logger.log_test_ok()

        Logger.log_test_step('Interpreting')
        run_out, run_err, run_exit_code = self._interpret(compiler_out, test_info)
        Logger.log_test_ok()
        Logger.log_test_step('Checking outputs')

        if test_info.interpreter_exit_code is not None:
            if run_exit_code != test_info.interpreter_exit_code:
                Logger.log_test_fail("INTERPRETER EXIT CODE FAIL, expected={}, returned={}".format(
                    test_info.interpreter_exit_code, run_exit_code
                ))
                return
        if test_info.stdout is not None:
            if run_out != test_info.stdout:
                Logger.log_test_fail("STDOUT")
                return
        Logger.log_test_ok()

    def _compile(self, code):
        process = Popen([self._compiler_binary], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        out, err = process.communicate(code)
        return out, err, process.returncode

    def _interpret(self, code, test_info):
        code_temp = mktemp()
        with open(code_temp, 'wb') as f:
            f.write(code)

        process = Popen([self._interpreter_binary, code_temp], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        out, err = process.communicate(input=test_info.stdin, timeout=2)
        return out, err, process.returncode

    @classmethod
    def find_tests(cls, directory):
        for code_file in sorted(iglob(path.join(directory, "*.code"))):
            name, _ = path.splitext(path.basename(code_file))

            try:

                info = TestInfo(
                    name,
                    cls._read_file(code_file),
                    cls._read_file(path.join(directory, '.'.join((name, 'stdin'))), allow_fail=True),
                    cls._read_file(path.join(directory, '.'.join((name, 'stdout'))), allow_fail=True),
                    int(cls._read_file(path.join(directory, '.'.join((name, 'cexitcode'))), allow_fail=True) or 0),
                    int(cls._read_file(path.join(directory, '.'.join((name, 'iexitcode'))), allow_fail=True) or 0),
                )
            except ValueError:
                # TODO: log error
                continue
            yield info

    @property
    def test_sections(self):
        return (
            path.join(self._tests_dir, dir_)
            for dir_
            in os.listdir(self._tests_dir)
            if path.isdir(path.join(self._tests_dir, dir_))
        )

    @staticmethod
    def _read_file(file, allow_fail=False):
        assert allow_fail or (path.isfile(file) and os.access(file, os.R_OK))
        try:
            with open(file, 'rb') as f:
                return f.read()
        except IOError:
            if not allow_fail:
                raise
            return None


def main(args):
    runner = TestRunner(args)
    runner.run()


if __name__ == '__main__':
    parser = ArgumentParser(description='Automatically run test cases for IFJ17 compiler.')
    parser.add_argument("compiler", help="path to IFJ17 compiler binary")
    parser.add_argument("interpreter", help="path to IFJ17 interpreter binary",
                        type=str, default=path.join(__DIR__, 'ic17int'))
    parser.add_argument("-d", "--tests-dir", help="path to folder with tests to run",
                        type=str, default=path.join(__DIR__, 'tests'))
    parsed = parser.parse_args()

    main(parsed)
