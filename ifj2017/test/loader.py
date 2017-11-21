# coding=utf-8
import json
import os
import os.path as path
from glob import iglob
from operator import attrgetter

from .base import TestInfo
from .logger import TestLogger


class TestLoader(object):
    def __init__(self, tests_dir, default_timeout):
        assert path.isdir(tests_dir), "Given tests dir is valid filesystem folder."

        self._tests_dir = tests_dir
        self._default_timeout = default_timeout

    def load_section_dirs(self):
        return sorted(
            path.join(self._tests_dir, dir_)
            for dir_
            in os.listdir(self._tests_dir)
            if path.isdir(path.join(self._tests_dir, dir_))
        )

    def load_tests(self, section_dir):
        assert path.isdir(section_dir)

        compact_tests = self._load_compact_tests(section_dir)
        already_loaded = set(map(attrgetter('name'), compact_tests))
        file_tests = self._load_file_tests(section_dir, already_loaded)
        tests = tuple(file_tests) + tuple(compact_tests)
        test_names = tuple(map(attrgetter('name'), tests))
        conflicting = set(test for test in test_names if test_names.count(test) > 1)
        if conflicting:
            TestLogger.log_warning('Conflicting test case names: {}.'.format(', '.join(sorted(conflicting))))
            return ()

        return sorted(
            tests,
            key=lambda test: (len(test.name), test.name)
        )

    def _load_compact_tests(self, section_dir):
        data = self.load_file(
            path.join(section_dir, 'tests.json'),
            allow_fail=True
        )
        if not data:
            return ()
        try:
            data = json.loads(data)
        except (json.JSONDecodeError, TypeError) as e:
            TestLogger.log_warning(
                "File {} is not valid json to load ({}).".format(path.join(section_dir, 'tests.json'), e)
            )
            return ()
        cases = []
        extensions = tuple(data.get('extensions', ()))
        try:
            for i, test_case in enumerate(data.get('tests', ())):
                name = test_case.get('name')
                code = test_case.get('code')

                if name and code:
                    TestLogger.log_warning(
                        "Redefined test {} in file {}.".format(name, path.join(section_dir, 'tests.json'))
                    )

                if not name:
                    name = '{:03}'.format(i + 1)
                
                if not code:
                    code = self._load_test_file(section_dir, name, 'code')
                
                cases.append(
                    TestInfo(
                        name,
                        code,
                        test_case.get('stdin') or self._load_test_file(section_dir, name, 'stdin'),
                        test_case.get('stdout') or self._load_test_file(section_dir, name, 'stdout'),
                        int(
                            test_case.get('compiler_exit_code') or
                            self._load_test_file(section_dir, name, 'cexitcode') or 0
                        ),
                        int(
                            test_case.get('interpreter_exit_code') or
                            self._load_test_file(section_dir, name, 'iexitcode') or 0
                        ),
                        test_case.get('info') or
                        self._load_test_file(section_dir, name, 'info') or
                        self._get_code_info(code),
                        section_dir,
                        set(tuple(test_case.get('extensions', ())) + extensions),
                        test_case.get('timeout') or self._default_timeout
                    )
                )
        except TypeError as e:
            TestLogger.log_warning("Cannot load test cases: {}.".format(e))
            return ()
        return cases

    def _load_file_tests(self, section_dir, already_loaded):
        for code_file in sorted(iglob(path.join(section_dir, "*.code"))):
            name, _ = path.splitext(path.basename(code_file))
            if name in already_loaded:
                continue
            try:
                code = self.load_file(code_file)
                info = TestInfo(
                    name,
                    code,
                    self._load_test_file(section_dir, name, 'stdin'),
                    self._load_test_file(section_dir, name, 'stdout'),
                    int(self._load_test_file(section_dir, name, 'cexitcode') or 0),
                    int(self._load_test_file(section_dir, name, 'iexitcode') or 0),
                    self._load_test_file(section_dir, name, 'info') or self._get_code_info(code) or '',
                    section_dir,
                    set(),
                    self._default_timeout
                )
            except ValueError as e:
                TestLogger.log_warning("Unable to load file {}: {}".format(code_file, e))
                continue
            yield info

    @classmethod
    def _get_code_info(cls, code):
        return (
            code[:code.index('\n')].lstrip('\'').strip()
            if '\n' in code and code.strip().startswith('\'')
            else ''
        )

    def _load_test_file(self, section_dir, test_name, type_):
        return ((
            self.load_file(
                path.join(
                    section_dir,
                    '.'.join((test_name, type_))
                ),
                allow_fail=True
            ) or '').replace('\r\n', '\n').replace('\r', '\n') # normalize newlines to \n
        ) or ''

    @staticmethod
    def load_file(file, allow_fail=False):
        assert allow_fail or (path.isfile(file) and os.access(file, os.R_OK))
        try:
            with open(file, 'rb') as f:
                return f.read().decode('utf-8')
        except IOError:
            if not allow_fail:
                raise
            return None


__all__ = ['TestLoader']
