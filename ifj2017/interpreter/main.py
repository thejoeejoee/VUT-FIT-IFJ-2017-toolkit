# coding=utf-8
from argparse import ArgumentParser
from sys import stdout, stderr, stdin

from ifj2017.interpreter.interpreter import Interpreter


def main():
    parser = ArgumentParser(
        description='Interpreter for IFJcode17 three address code.',
        epilog="""
        Authors: Josef Kolář (xkolar71, @thejoeejoee), Son Hai Nguyen (xnguye16, @SonyPony), GNU GPL v3, 2017
        """
    )

    parser.add_argument("file", help="path to file of IFJcode17 to interpret")

    args = parser.parse_args()

    try:
        with open(args.file) as f:
            code = f.read()
    except Exception as e:
        print("Cannot load code from file {} due {}.".format(args.file, e), file=stderr)
        exit(1)
        return

    Interpreter(
        code,
        state_kwargs=dict(
            stdout=stdout,
            stderr=stderr,
            stdin=stdin
        )
    ).run()

    return 0


if __name__ == '__main__':
    exit(main())
