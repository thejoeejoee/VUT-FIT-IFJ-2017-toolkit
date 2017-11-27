# coding=utf-8
import json
import os
import os.path as path
from glob import iglob
from operator import attrgetter
from os.path import basename
from typing import Set, Tuple, Optional

from .base import TestInfo
from .logger import TestLogger


class TestLoader(object):
    def __init__(self, tests_dir, default_timeout, tests_wildcards):
        assert path.isdir(tests_dir), "Given tests dir is valid filesystem folder."

        self._tests_dir = tests_dir
        self._default_timeout = default_timeout
        self._tests_wildcards = self._parse_wildcards(tests_wildcards)  # type: Set[Tuple[str, Optional[str]]]

    def load_section_dirs(self):
        return sorted(
            path.join(self._tests_dir, dir_)
            for dir_
            in os.listdir(self._tests_dir)
            if path.isdir(path.join(self._tests_dir, dir_))
            and self._allow_wildcard(dir_)
        )

    def load_tests(self, section_dir):
        assert path.isdir(section_dir)

        json_data = self._load_json_file(section_dir)
        compact_tests = self._load_compact_tests(section_dir, json_data)
        already_loaded = set(map(attrgetter('name'), compact_tests))
        file_tests = self._load_file_tests(section_dir, already_loaded, json_data)
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

    def _load_json_file(self, section_dir):
        data = self.load_file(
            path.join(section_dir, 'tests.json'),
            allow_fail=True
        )
        if not data:
            return {}
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError) as e:
            TestLogger.log_warning(
                "File {} is not valid json to load ({}).".format(path.join(section_dir, 'tests.json'), e)
            )
            return {}

    def _load_compact_tests(self, section_dir, data):
        cases = []
        extensions = tuple(data.get('extensions', ()))
        try:
            for i, test_case in enumerate(data.get('tests', ())):
                name = test_case.get('name')
                code = test_case.get('code')

                if name and code:
                    TestLogger.log_warning(
                        "Redefined test {} in file {}, skipping.".format(name, path.join(section_dir, 'tests.json'))
                    )
                    continue

                if not name:
                    name = '{:03}'.format(i + 1)

                if not self._allow_wildcard(basename(section_dir), name):
                    continue

                if not code:
                    code = self._load_test_file(section_dir, name, 'code')

                if not code and not test_case.get('allow_empty'):
                    TestLogger.log_warning('Test {} has not defined code, skipping.'.format(name))
                    continue

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

    def _load_file_tests(self, section_dir, already_loaded, data):
        extensions = tuple(data.get('extensions', ()))
        for code_file in sorted(iglob(path.join(section_dir, "*.code"))):
            name, _ = path.splitext(path.basename(code_file))
            if name in already_loaded:
                continue
            if not self._allow_wildcard(basename(section_dir), name):
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
                    set(extensions),
                    self._default_timeout
                )
            except ValueError as e:
                TestLogger.log_warning("Unable to load file {}: {}".format(code_file, e))
                continue
            yield info

    def _allow_wildcard(self, section, name=None):
        if not self._tests_wildcards:
            return True

        if name:
            return any(
                section_wc in section and (name_wc is None or name == name_wc)
                for section_wc, name_wc
                in self._tests_wildcards
            )

        return any(
            section_wc in section
            for section_wc, name_wc
            in self._tests_wildcards
        )

    @classmethod
    def _get_code_info(cls, code):
        return (
            code[:code.index('\n')].lstrip('\'').strip()
            if '\n' in code and code.strip().startswith('\'')
            else ''
        )

    @staticmethod
    def _parse_wildcards(tests_wildcards):
        wildcards = set()
        for wildcard in filter(None, tests_wildcards):
            parts = tuple(filter(None, wildcard.split('/')))
            parts_count = len(parts)
            if parts_count == 1:
                section, name = parts[0], None
            elif parts_count == 2:
                section, name = parts
            else:
                TestLogger.log_warning('Invalid wildcard {}, skipping.'.format(wildcard))
                continue
            wildcards.add((section, name))
        return wildcards

    def _load_test_file(self, section_dir, test_name, type_):
        # splitlines is not possible due endlines at and of file
        return (
                   (
                       self.load_file(
                           path.join(
                               section_dir,
                               '.'.join((test_name, type_))
                           ),
                           allow_fail=True
                       ) or '').replace('\r\n', '\n').replace('\r', '\n')  # normalize newlines to \n
               ) or ''

    @staticmethod
    def load_file(file, allow_fail=False):
        assert allow_fail or (path.isfile(file) and os.access(file, os.R_OK))
        try:
            with open(file, 'rbU') as f:
                return f.read().decode('utf-8')
        except IOError:
            if not allow_fail:
                raise
            return None


__all__ = ['TestLoader']
