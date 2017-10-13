#!/usr/bin/env python3
# coding=utf-8
import platform
from argparse import ArgumentParser
from os import path

from ifj2017 import __PROJECT_ROOT__
from ifj2017.test.runner import TestRunner

if __name__ == '__main__':
    parser = ArgumentParser(
        description='Automatic test cases runner for IFJ17 compiler.',
        epilog="""
        Authors: Josef Kolář (xkolar71, @thejoeejoee), Son Hai Nguyen (xnguye16, @SonyPony), GNU GPL v3, 2017
        """
    )
    if not TestRunner.check_platform():
        exit(1)

    parser.add_argument("compiler", help="path to IFJ17 compiler binary")
    parser.add_argument("-i", "--interpreter", help="path to IFJ17 interpreter binary",
                        type=str, default=TestRunner.INTERPRETERS.get(platform.system()))
    parser.add_argument("-d", "--tests-dir", help="path to folder with tests to run",
                        type=str, default=path.join(__PROJECT_ROOT__, 'tests'))
    parser.add_argument("-l", "--log-dir", help="path to folder with logs",
                        type=str, default=path.join(__PROJECT_ROOT__, 'log'))
    parser.add_argument("--benchmark-url-target", help="target hostname to send benchmark results",
                        type=str, default='http://localhost:8000')
    parser.add_argument("--command-timeout", help="maximal timeout for compiler and interpreter",
                        type=float, default=.2)
    parser.add_argument("--no-colors", action='store_true', help="disable colored output (for Windows CMD etc.)",
                        default=False)

    runner = TestRunner(parser.parse_args())
    exit(runner.run())
