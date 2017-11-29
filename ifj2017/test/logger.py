# coding=utf-8

import os
import shutil
import sys
from operator import attrgetter
from typing import Optional

from ifj2017.interpreter.state import State


def disable_color():
    """
    Return True if the running system's terminal supports color,
    and False otherwise.
    """
    # windows dark magic via https://stackoverflow.com/a/39675059
    # noinspection PyBroadException
    try:
        os.system('')
    except:
        pass

    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)

    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stderr, 'isatty') and sys.stderr.isatty()
    return not supported_platform or not is_a_tty


class TestLogger(object):
    BLUE = '\033[94m'
    GREEN = '\033[32m'
    WARNING = '\033[93m'
    HEADER = '\033[95m'
    FAIL = '\033[91m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    disable_colors = disable_color()
    verbose = False
    console_width, console_height = shutil.get_terminal_size((120, 20))

    _test_case_buffer = None
    _test_case_success = None
    _test_case_skipped = None

    @classmethod
    def log(cls, *args, stream=sys.stderr, end=True, indent=0):
        def write(what):
            if cls._test_case_buffer is not None:
                cls._test_case_buffer.append(what)
            else:
                stream.write(what)

        write('\t' * indent)
        to_log = ''.join(map(str, filter(None, args)))
        if cls.disable_colors:
            for color in (
                    cls.BLUE, cls.GREEN, cls.WARNING, cls.HEADER, cls.FAIL, cls.BOLD, cls.UNDERLINE
            ):
                to_log = to_log.replace(color, '')

        write(to_log)
        write(cls.END)
        if end:
            write('\n')

    @classmethod
    def log_section(cls, section):
        cls.log(cls.BLUE, cls.UNDERLINE, section, ':')

    @classmethod
    def log_test(cls, name, info=None):
        cls._test_case_buffer = []
        cls.log(cls.BOLD, '{:3}'.format(name), info, ': ', indent=1, end=False)

    @classmethod
    def log_test_fail(cls, result):
        cls._test_case_success = False
        cls.log(cls.BOLD, cls.WARNING, ' × ', result, end=False)

    @classmethod
    def log_test_ok(cls):
        cls._test_case_success = True
        cls.log(cls.GREEN, cls.BOLD, '√', end=False)

    @classmethod
    def log_warning(cls, warning, end=True):
        cls.log(cls.FAIL, cls.BOLD, 'WARNING: ', warning, end=end)

    @classmethod
    def log_end_test_case(cls):
        cls.log()
        if cls.verbose or not cls._test_case_success and not cls._test_case_skipped:
            cls._log_buffer()
        cls._test_case_buffer = None

    @classmethod
    def log_price(cls, state: State, groot_price: Optional[int]):
        # (State) -> None
        cls.log(
            cls.BLUE,
            ' ',
            state.operand_price + state.instruction_price,
            ' ({}+{}) '.format(
                state.instruction_price,
                state.operand_price
            ),
            end=False
        )
        if groot_price != state.price:
            cls.log_warning(
                'Computed price {} does not matched price from reference interpreter {}, '
                'please contact maintainers.'.format(state.price, groot_price),
                end=False
            )

    @classmethod
    def log_results(cls, reports):
        total = len(reports)
        if not total:
            cls.log(cls.UNDERLINE, cls.BLUE, cls.WARNING, 'No tests found.')
            return 0

        success = len(tuple(filter(attrgetter('success'), reports)))
        skipped = len(tuple(filter(lambda r: r.success is None, reports)))

        cls.log(
            cls.UNDERLINE,
            cls.BOLD,
            'RESULTS:',
            cls.END,
            cls.BOLD,
            ' {:.2f}%'.format((float(success) / (total - skipped)) * 100),
            cls.END,
            ' ({}/{})\n'.format(success, total - skipped),
            cls.END,
            cls.BOLD,
            ''.join(
                (
                    ((cls.FAIL + '×', cls.GREEN + '.')[report.success]
                     if report.success is not None
                     else cls.BLUE + '_')
                ) + ('\n' if not (i % cls.console_width) else '')
                for i, report in enumerate(reports, start=1)),
            ''
        )
        return bool(total - success)

    @classmethod
    def _log_buffer(cls, stream=sys.stderr):
        for to_log in cls._test_case_buffer or ():
            stream.write(to_log)


__all__ = ['TestLogger']
