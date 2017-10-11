# coding=utf-8

import sys
from operator import attrgetter


class TestLogger(object):
    BLUE = '\033[94m'
    GREEN = '\033[32m'
    WARNING = '\033[93m'
    HEADER = '\033[95m'
    FAIL = '\033[91m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    disable_colors = False

    @classmethod
    def log(cls, *args, stream=sys.stderr, end=True, indent=0):
        stream.write('\t' * indent)
        if cls.disable_colors:
            args = (
                arg
                for arg
                in args
                if arg not in (
                cls.BLUE, cls.GREEN, cls.WARNING, cls.HEADER, cls.FAIL, cls.BOLD, cls.UNDERLINE
            )
            )

        stream.write(''.join(map(str, filter(None, args))))
        stream.write(cls.END)
        if end:
            stream.write('\n')

    @classmethod
    def log_section(cls, section):
        cls.log(cls.BLUE, cls.UNDERLINE, section, ':')

    @classmethod
    def log_test(cls, name, info=None):
        cls.log(cls.BOLD, name, info, ': ', indent=1, end=False)

    @classmethod
    def log_test_fail(cls, result):
        cls.log(cls.BOLD, cls.WARNING, '× ', result, end=False)

    @classmethod
    def log_test_ok(cls):
        cls.log(cls.GREEN, cls.BOLD, '✓', end=False)

    @classmethod
    def log_warning(cls, warning):
        cls.log(cls.FAIL, cls.BOLD, 'WARNING: ', warning)

    @classmethod
    def log_end_test_case(cls):
        cls.log()

    @classmethod
    def log_price(cls, state):
        # (State) -> None
        cls.log(cls.BLUE, ' ', state.operand_price + state.instruction_price, ' ({}+{})'.format(
            state.instruction_price,
            state.operand_price
        ), end=False)

    @classmethod
    def log_results(cls, reports):
        total = len(reports)
        success = len(tuple(filter(attrgetter('success'), reports)))

        cls.log(
            cls.UNDERLINE,
            cls.BOLD,
            'RESULTS:',
            cls.END,
            ' ({}/{})\n\t'.format(success, total),
            cls.END,
            cls.BOLD,
            ''.join((cls.FAIL + '×', cls.GREEN + '✓')[report.success] for report in reports),
            ''
        )
        return bool(total - success)


__all__ = ['TestLogger']
