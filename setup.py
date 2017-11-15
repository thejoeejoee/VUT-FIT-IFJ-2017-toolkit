# coding=utf-8


from distutils import core
from os.path import abspath, dirname, join

from setuptools import find_packages

__author__ = "Josef Kolář, Son Hai Nguyen"
__copyright__ = "Copyright 2017, Josef Kolář & Son Hai Nguyen"
__credits__ = ["Josef Kolář", "Son Hai Nguyen"]
__license__ = "GNU GPL Version 3"

base_path = abspath(dirname(__file__))

try:
    import pypandoc

    long_description = pypandoc.convert(join(base_path, 'README.md'), 'rst')
except(IOError, ImportError):
    long_description = open(join(base_path, 'README.md')).read()


def setup():
    core.setup(
        name='IFJcode17-toolkit',
        version='1.0',
        license='GNU GENERAL PUBLIC LICENSE Version 3',
        long_description=long_description,
        url='https://github.com/thejoeejoee/VUT-FIT-IFJ-2017-toolkit',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: X11 Applications :: Qt',

            'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',

            'Programming Language :: Python',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3 :: Only',

            'Topic :: Scientific/Engineering',
            'Topic :: Utilities'
        ],
        author='Josef Kolář, Son Hai Nguyen',
        author_email='xkolar71@stud.fit.vutbr.cz, xnguye16@stud.fit.vutbr.cz',
        keywords='ifj17 ifjcode17 language ide utils debugger editor',
        packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
        install_requires=[
            'PyOpenGL',
            'PyQt5==5.7.1',
        ],
        requires=[
            'termcolor',
            'PyOpenGL',
            'PyQt5',
        ],
        # package_dir={'': base_path},
        entry_points={
            'console_scripts': [
                'ifjcode17-ide=ifj2017.ide.main:main',
                'ifjcode17-tests=ifj2017.test.main:main',
                'ifjcode17-interpreter=ifj2017.interpreter.main:main',
            ]
        },
        data_files=[
            ('share/icons/hicolor/scalable/apps', ['data/ifjcode17-ide.svg']),
            ('share/applications', ['data/ifjcode17-ide.desktop'])
        ],
        include_package_data=True,
        zip_safe=False,
    )


if __name__ == '__main__':
    setup()
