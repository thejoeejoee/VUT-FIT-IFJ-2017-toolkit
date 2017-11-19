#!/usr/bin/env python3
# coding=utf-8
import sys
from argparse import ArgumentParser
from datetime import datetime
from glob import glob1
from os import unlink, getcwd
from os.path import basename, join, abspath, dirname
from tarfile import TarFile
from tempfile import mktemp

from git import Repo

__DIR__ = abspath(getcwd())

HEADER = """\
/*
 * Source file of project of IFJ17 language compiler for IFJ as FIT BUT in Brno.
 * 
 * @file {}
 * @author {} 
 * 
 * Generated: {}
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


def deploy(source_dir, to_archive):
    source_dir = abspath(join(__DIR__, source_dir))
    source_files = set(glob1(source_dir, '*.c') + glob1(source_dir, '*.h') + glob1(source_dir, 'Makefile'))
    source_files.add(join(source_dir, '../rozdeleni'))
    source_files.add(join(source_dir, '../rozsireni'))

    to_archive = '{}.tgz'.format(to_archive)
    try:
        unlink(to_archive)
    except OSError:
        pass

    repository = Repo(source_dir, search_parent_directories=True)

    with TarFile.open(name=to_archive, mode='x:gz') as target_archive:

        for file_ in source_files:
            print('Processing {}.'.format(file_), file=sys.stderr)
            authors = set(
                author.strip('\'') for author in
                repository.git.log(join(source_dir, file_), pretty="format:'%an (%aE)'", follow=True).splitlines()
            )
            if basename(file_) in {'rozsireni', 'rozdeleni'}:
                target_archive.add(file_, arcname=basename(file_))
                continue

            modified = mktemp()

            _add_header(
                join(source_dir, file_),
                modified,
                authors
            )
            target_archive.add(modified, arcname=basename(file_))


def main():
    parser = ArgumentParser(
        description='Script for deploying archive with IFJ17 compiler.',
    )

    parser.add_argument("source_dir", help="path to src of project")
    parser.add_argument("archive_name", help="name of produced")

    args = parser.parse_args()
    return deploy(args.source_dir, args.archive_name)


if __name__ == '__main__':
    main()
