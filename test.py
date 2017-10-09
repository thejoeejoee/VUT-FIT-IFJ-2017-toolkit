#!/usr/bin/env python3
# coding=utf-8
import json
import os
from argparse import ArgumentParser
from collections import namedtuple
from glob import iglob
from operator import attrgetter
from os import path
from subprocess import Popen, PIPE
from sys import stderr
from tempfile import mktemp

__DIR__ = path.abspath(path.dirname(__file__))

TestInfo = namedtuple('TestInfo', "name code stdin stdout compiler_exit_code interpreter_exit_code info")


class Logger(object):
    BLUE = '\033[94m'
    GREEN = '\033[32m'
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
    def log_test(cls, name, info=None):
        Logger.log(Logger.BOLD, 'TEST ', name, info, indent=1)

    @classmethod
    def log_test_step(cls, step):
        Logger.log(Logger.BLUE, step, '...', indent=2)

    @classmethod
    def log_test_fail(cls, result):
        cls.log(Logger.BOLD, Logger.WARNING, '× ', result, indent=3)

    @classmethod
    def log_test_ok(cls):
        cls.log(Logger.GREEN, Logger.BOLD, '✓ OK', indent=3)

    @classmethod
    def log_warning(cls, warning):
        cls.log(Logger.FAIL, Logger.BOLD, 'WARNING: ', warning)


class TestLoader(object):
    def __init__(self, tests_dir):
        assert path.isdir(tests_dir), "Given tests dir is valid filesystem folder."

        self._tests_dir = tests_dir

    def load_section_dirs(self):
        return (
            path.join(self._tests_dir, dir_)
            for dir_
            in os.listdir(self._tests_dir)
            if path.isdir(path.join(self._tests_dir, dir_))
        )

    def load_tests(self, section_dir):
        assert path.isdir(section_dir)
        file_tests = self._load_file_tests(section_dir)
        compact_tests = self._load_compact_tests(section_dir)

        return sorted(
            tuple(file_tests) + tuple(compact_tests),
            key=attrgetter('name')
        )

    def _load_compact_tests(self, section_dir):
        data = self._read_file(
            path.join(section_dir, 'tests.json'),
            allow_fail=True
        )
        if not data:
            return ()
        try:
            data = json.loads(data)
        except (json.JSONDecodeError, TypeError) as e:
            Logger.log_warning(
                "File {} is not valid json to load ({}).".format(path.join(section_dir, 'tests.json'), e)
            )
            return ()
        cases = []
        try:
            for i, test_case in enumerate(data.get('tests', ())):
                cases.append(
                    TestInfo(
                        test_case.get('name') or '{:03}'.format(i + 1),
                        test_case.get('code') or '',
                        test_case.get('stdin') or '',
                        test_case.get('stdout') or '',
                        int(test_case.get('compiler_exit_code') or 0),
                        int(test_case.get('interpreter_exit_code') or 0),
                        test_case.get('info') or '',
                    )
                )
        except TypeError as e:
            Logger.log_warning("Cannot load test cases: {}.".format(e))
            return ()
        return cases

    def _load_file_tests(self, section_dir):
        for code_file in sorted(iglob(path.join(section_dir, "*.code"))):
            name, _ = path.splitext(path.basename(code_file))
            try:
                code = self._read_file(code_file)
                info = TestInfo(
                    name,
                    code,
                    self._read_file(path.join(section_dir, '.'.join((name, 'stdin'))), allow_fail=True),
                    self._read_file(path.join(section_dir, '.'.join((name, 'stdout'))), allow_fail=True),
                    int(self._read_file(path.join(section_dir, '.'.join((name, 'cexitcode'))), allow_fail=True) or 0),
                    int(self._read_file(path.join(section_dir, '.'.join((name, 'iexitcode'))), allow_fail=True) or 0),
                    (
                        code[:code.index('\n')].lstrip('\'').strip()
                        if '\n' in code and code.strip().startswith('\'')
                        else ''
                    )
                )
            except ValueError as e:
                Logger.log_warning("Unable to load file {}: {}".format(code_file, e))
                continue
            yield info

    @staticmethod
    def _read_file(file, allow_fail=False):
        assert allow_fail or (path.isfile(file) and os.access(file, os.R_OK))
        try:
            with open(file, 'rb') as f:
                return f.read().decode('utf-8')
        except IOError:
            if not allow_fail:
                raise
            return None


class TestRunner(object):
    def __init__(self, args):
        super(TestRunner, self).__init__()
        assert path.isfile(args.compiler) and os.access(args.compiler, os.X_OK), \
            "Given compiler ({}) is file and is executable.".format(args.compiler)
        assert path.isfile(args.interpreter) and os.access(args.interpreter, os.X_OK), \
            "Given interpreter ({}) is file and is executable.".format(args.interpreter)

        self._compiler_binary = args.compiler
        self._interpreter_binary = args.interpreter
        self._loader = TestLoader(args.tests_dir)

    def run(self):
        for test_section_dir in self._loader.load_section_dirs():
            Logger.log_section(path.basename(test_section_dir))
            for test_info in self._loader.load_tests(test_section_dir):
                self._run_test(test_info)

    def _run_test(self, test_info):
        Logger.log_test(
            test_info.name,
            ' ({})'.format(
                test_info.info
            ) if test_info.info else None
        )
        Logger.log_test_step('Compiling')
        compiler_out, compiler_err, compiler_exit_code = self._compile(test_info.code)

        if test_info.compiler_exit_code is not None:
            if compiler_exit_code != test_info.compiler_exit_code:
                Logger.log_test_fail("COMPILER EXIT CODE FAIL, expected={}, returned={}".format(
                    test_info.compiler_exit_code, compiler_exit_code
                ))
                return

        Logger.log_test_ok()
        if compiler_exit_code != 0:
            # compiler stops this test case
            return

        Logger.log_test_step('Interpreting')
        run_out, run_err, run_exit_code = self._interpret(compiler_out, test_info)

        if test_info.interpreter_exit_code is not None:
            if run_exit_code != test_info.interpreter_exit_code:
                Logger.log_test_fail("INTERPRETER EXIT CODE FAIL, expected={}, returned={}".format(
                    test_info.interpreter_exit_code, run_exit_code
                ))
                return

        if run_exit_code != 0:
            # interpreter stops this test case
            return

        Logger.log_test_ok()

        Logger.log_test_step('Checking outputs')
        if test_info.stdout is not None:
            if run_out != test_info.stdout:
                Logger.log_test_fail("STDOUT")
                return
        Logger.log_test_ok()

    def _compile(self, code):
        process = Popen([self._compiler_binary], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        out, err = process.communicate(bytes(code, encoding='utf-8'))
        return out.decode('utf-8'), err, process.returncode

    def _interpret(self, code, test_info):
        code_temp = mktemp()
        with open(code_temp, 'wb') as f:
            f.write(bytes(code, encoding='utf-8'))

        process = Popen([self._interpreter_binary, code_temp], stdout=PIPE, stdin=PIPE, stderr=PIPE)
        out, err = process.communicate(input=test_info.stdin, timeout=2)
        return out.decode('utf-8'), err, process.returncode


def main(args):
    runner = TestRunner(args)
    runner.run()


if __name__ == '__main__':
    parser = ArgumentParser(
        description='Automatic test cases runner for IFJ17 compiler.',
        epilog="""
        Authors: Josef Kolář (xkolar71, @thejoeejoee), Son Hai Nguyen (xnguye16, @SonyPony), GNU GPL v3, 2017
        """
    )
    parser.add_argument("compiler", help="path to IFJ17 compiler binary")
    parser.add_argument("-i", "--interpreter", help="path to IFJ17 interpreter binary",
                        type=str, default=path.join(__DIR__, 'bin/ic17int'))
    parser.add_argument("-d", "--tests-dir", help="path to folder with tests to run",
                        type=str, default=path.join(__DIR__, 'tests'))

    parsed = parser.parse_args()

    main(parsed)
