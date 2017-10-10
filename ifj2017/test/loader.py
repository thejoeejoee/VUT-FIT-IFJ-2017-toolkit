# coding=utf-8
import json
import os
import os.path as path
from glob import iglob
from operator import attrgetter

from .base import TestInfo
from .logger import Logger


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
        tests = tuple(file_tests) + tuple(compact_tests)
        test_names = tuple(map(attrgetter('name'), tests))
        conflicting = set(test for test in test_names if test_names.count(test) > 1)
        if conflicting:
            Logger.log_warning('Conflicting test case names: {}.'.format(', '.join(sorted(conflicting))))
            return ()

        return sorted(
            tests,
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
                    self._read_file(path.join(section_dir, '.'.join((name, 'stdin'))), allow_fail=True) or '',
                    self._read_file(path.join(section_dir, '.'.join((name, 'stdout'))), allow_fail=True) or '',
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


__all__ = ['TestLoader']
