# coding=utf-8
import sys

from os import path

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterSingletonType, qmlRegisterType
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import (QSize, QtFatalMsg, QtCriticalMsg, QtWarningMsg, QtInfoMsg,
                          qInstallMessageHandler, QtDebugMsg)

from ifj2017.ide.code_analyzer import CodeAnalyzer
from ifj2017.ide.code.expression import ExpSyntaxHighlighter, ExpAnalyzer
from ifj2017.ide.core.tree_view_model import TreeViewModel
from ifj2017.ide.code.diff_code_analyzer import DiffCodeAnalyzer
from ifj2017.ide.debugger_wrapper import DebuggerWrapper
from ifj2017.ide.io_wrapper import IOWrapper
from ifj2017.ide.core.file_io import FileIO

try:
    from termcolor import colored
except ImportError:
    def colored(mode, *args, **kwargs):
        return mode


def qt_message_handler(mode, context, message):
    modes = {
        QtInfoMsg: "Info",
        QtWarningMsg: "Warning",
        QtCriticalMsg: "Critical",
        QtFatalMsg: "Fatal",
        QtDebugMsg: "Debug"
    }

    modes_colors = {
        QtInfoMsg: "blue",
        QtWarningMsg: "yellow",
        QtCriticalMsg: "red",
        QtFatalMsg: "red",
        QtDebugMsg: "green"
    }

    mode = colored(modes[mode], modes_colors[mode])

    if context.file is None:
        print('{mode}: {msg}'.format(mode=mode, msg=message))
    else:
        print('{mode}: {msg}\t\t\t\tline: {line}, function: {func}, file: {file}'.format(
            mode=mode, line=context.line, func=context.function, file=context.file, msg=message))


qInstallMessageHandler(qt_message_handler)

app = QApplication(sys.argv)

base_url = QUrl("file:///{}/".format(str(path.abspath(path.dirname(__file__))).replace('\\', '/')))

qmlRegisterSingletonType(base_url.resolved(QUrl("assets/styles/UIStyles.qml")), "StyleSettings", 1, 0, "StyleSettings")
qmlRegisterSingletonType(CodeAnalyzer, "CodeAnalyzer", 1, 0, "CodeAnalyzer", CodeAnalyzer.singletonProvider)
qmlRegisterType(ExpSyntaxHighlighter, "ExpSyntaxHighlighter", 1, 0, "ExpSyntaxHighlighter")
qmlRegisterType(DiffCodeAnalyzer, "DiffCodeAnalyzer", 1, 0, "DiffCodeAnalyzer")
qmlRegisterType(ExpAnalyzer, "ExpAnalyzer", 1, 0, "ExpAnalyzer")
qmlRegisterType(TreeViewModel, "TreeViewModel", 1, 0, "TreeViewModel")
qmlRegisterType(DebuggerWrapper, "Debugger", 1, 0, "Debugger")
qmlRegisterType(IOWrapper, "IOWrapper", 1, 0, "IOWrapper")
qmlRegisterType(FileIO, "FileIO", 1, 0, "FileIO")

engine = QQmlApplicationEngine()
engine.rootContext().setContextProperty("rootDir", base_url.toString())
engine.load(QUrl("qml/main.qml"))

sys.exit(app.exec())
