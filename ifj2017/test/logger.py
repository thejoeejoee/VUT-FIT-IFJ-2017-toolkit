# coding=utf-8

import sys


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
    def log(cls, *args, stream=sys.stderr, end=True, indent=0):
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
        Logger.log(Logger.BOLD, name, info, ': ', indent=1, end=False)

    @classmethod
    def log_test_fail(cls, result):
        cls.log(Logger.BOLD, Logger.WARNING, '× ', result, end=False)

    @classmethod
    def log_test_ok(cls):
        cls.log(Logger.GREEN, Logger.BOLD, '✓', end=False)

    @classmethod
    def log_warning(cls, warning):
        cls.log(Logger.FAIL, Logger.BOLD, 'WARNING: ', warning)

    @classmethod
    def log_end_test_case(cls):
        cls.log()


__all__ = ['Logger']