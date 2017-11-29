#!/usr/bin/env python3
# coding=utf-8

import sys

if 'linux' in sys.platform.lower():
    # noinspection PyUnresolvedReferences
    from OpenGL import GL  # noqa

from ifj2017.ide.main import main

if __name__ == '__main__':
    exit(main())
