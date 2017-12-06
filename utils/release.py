#!/usr/bin/env python3
# coding=utf-8
import os
import sys
from argparse import ArgumentParser
from collections import Counter
from datetime import datetime
from glob import glob1
from operator import itemgetter
from os import unlink, getcwd
from os.path import basename, join, abspath, dirname
from tarfile import TarFile
from tempfile import mktemp

from git import Repo

__CWD_DIR__ = abspath(getcwd())
__DIR__ = dirname(abspath(__file__))
__PROJECT_DIR__ = abspath(join(dirname(abspath(__file__)), '..'))

HEADER = """\
/*
 * Source file of project of IFJ17 language compiler for IFJ as FIT BUT in Brno.
 * 
 * @file {}
 * @author {} 
 * 
 * Generated: {}
 * Academic year: 2017-2018
 * Team: xkobel02, xkolar71, xpazdi02, xnguye16
 * Project URL: https://github.com/thejoeejoee/IFJ-VUT-BIT-2017-2018
 * Encoding: UTF-8
 */
"""


def _add_header(original, target_file, authors):
    with open(original) as source, open(target_file, 'w') as target:
        target.write(
            '{}\n'
            '{}'.format(
                HEADER.format(
                    basename(original),
                    ', '.join(authors),
                    datetime.now()
                ) if basename(original) != 'Makefile' else '\n'.join('# {}'.format(line) for line in HEADER.format(
                    basename(original),
                    ', '.join(authors),
                    datetime.now()
                ).splitlines()),
                source.read()
            )
        )


def include_tests(archive: TarFile):
    def exclude(name: str):
        return name.endswith('pyc') or '__pycache__' in name

    archive.add(join(__PROJECT_DIR__, 'test.py'), 'tests/test.py')
    print('Processing tests/test.py.', file=sys.stderr)
    for d in 'benchmark interpreter test tests __init__.py'.split():
        archive.add(join(__PROJECT_DIR__, 'ifj2017/{}'.format(d)), 'tests/ifj2017/{}'.format(d), exclude=exclude)
        print('Processing {}.'.format('tests/ifj2017/{}'.format(d)), file=sys.stderr)


def deploy(source_dir, to_archive, tests=False):
    source_dir = abspath(join(__CWD_DIR__, source_dir))
    source_files = set(glob1(source_dir, '*.c') + glob1(source_dir, '*.h') + glob1(source_dir, 'Makefile'))
    source_files.add(join(source_dir, '../rozdeleni'))
    source_files.add(join(source_dir, '../rozsireni'))
    source_files.add(join(source_dir, '../doc/build/doc.pdf'))

    to_archive = '{}.tgz'.format(to_archive)
    try:
        unlink(to_archive)
    except OSError:
        pass

    repository = Repo(source_dir, search_parent_directories=True)

    with TarFile.open(name=to_archive, mode='x:gz') as target_archive:
        for file_ in source_files:
            print('Processing {}.'.format(file_), file=sys.stderr)
            counter = Counter(
                repository.git.log(
                    join(source_dir, file_),
                    pretty="format:%an (%aE)",
                    follow=True
                ).splitlines()
            )
            if basename(file_) in {'rozsireni', 'rozdeleni'}:
                target_archive.add(file_, arcname=basename(file_))
                continue
            if basename(file_) in {'doc.pdf', }:
                target_archive.add(file_, arcname='dokumentace.pdf')
                continue

            modified = mktemp()

            _add_header(
                join(source_dir, file_),
                modified,
                map(itemgetter(0), counter.most_common())
            )
            target_archive.add(modified, arcname=basename(file_))
        if tests:
            include_tests(target_archive)


def main():
    parser = ArgumentParser(
        description='Script for deploying archive with IFJ17 compiler.',
    )

    parser.add_argument(
        "--source_dir", help="path to src of project", type=str,
        default=os.path.expanduser('~/projects/IFJ-VUT-BIT-2017-2018/src')
    )
    parser.add_argument("--archive_name", help="name of produced", type=str, default='xkobel02')
    parser.add_argument("--tests", help="include tests?", action='store_true')

    args = parser.parse_args()
    return deploy(args.source_dir, args.archive_name, args.tests)


if __name__ == '__main__':
    main()
