import QtQuick 2.7
import QtQuick.Controls 1.4
import QtQuick.Dialogs 1.0
import QtQuick.Layouts 1.0

import TreeViewModel 1.0
import Debugger 1.0
import StyleSettings 1.0
import IOWrapper 1.0
import FileIO 1.0

import "code"
import "controls" as Controls
import "containers"
import "view" as View
import "widgets" as Widgets

ApplicationWindow {
    visible: true
    width: 1000
    height: 800
    title: fileIO.source + ((fileIO.source) ?" - " :"") + qsTr("Advánc Ifj Creator")

    Rectangle {
        id: root

        property string fileActionType: ""

        state: "stopped"
        color: "white"
        anchors.fill: parent
    }

    Debugger {
        id: ifjDebugger

        model: debugStateView.model
        ioWrapper: consoleWidget.ioWrapper

        onProgramEnded: if(root.state != "stopped") stopProgram()
        onProgramEndedWithError: {
            consoleWidget.write(msg, "#7a0000")
            stopProgram()
        }
    }

    FileDialog {
        id: fileDialog

        folder: shortcuts.documents
        selectMultiple: false
        selectExisting: (root.fileActionType != "save" && root.fileActionType != "saveAs")
        nameFilters: [ "IFJ files (*.IFJcode17)", "All files (*)" ]

        onAccepted: {
            fileIO.source = fileDialog.fileUrl
            if(root.fileActionType == "open")
                codeEditor.code = fileIO.read()
            else if(root.fileActionType == "save" || root.fileActionType == "saveAs")
                fileIO.write(codeEditor.code)
            root.fileActionType = ""
        }
    }

    FileIO {
        id: fileIO
    }

    Shortcut {
        sequence: "Ctrl+O"
        onActivated: openFile()
    }

    Shortcut {
        sequence: "Ctrl+S"
        onActivated: saveFile()
    }

    Shortcut {
        sequence: "Ctrl+Shift+S"
        onActivated: saveFileAs()
    }

    Shortcut {
        sequence: "F5"
        onActivated: {
            if(root.state == "stopped")
                runProgram()
            else if(root.state == "runningDebug" && consoleWidget.debugToolbarEnabled)
                ifjDebugger.runToNextBreakpoint()
        }
    }

    Shortcut {
        sequence: "F6"
        onActivated: {
            if(root.state == "runningDebug"  && consoleWidget.debugToolbarEnabled)
                ifjDebugger.runToNextLine()
        }
    }

    // Main bar
    Rectangle {
        id: mainToolbar

        width: Core.scaledSize(55)
        height: parent.height

        color: "#2f2f2f"

        Column {
            spacing: 0
            width: parent.width
            height: playButton.height * 3 + 2 * spacing

            anchors.bottom: parent.bottom
            anchors.bottomMargin: spacing
            anchors.horizontalCenter: parent.horizontalCenter

            Controls.IconButton {
                id: playButton

                iconSource: rootDir + "assets/images/playIcon.svg"
                width: parent.width
                height: width * 0.7

                onClicked: runProgram()
            }

            Controls.IconButton {
                id: playDebugButton

                iconSource: rootDir + "assets/images/playBugIcon.svg"
                width: parent.width
                height: playButton.height

                onClicked: debugProgram()
            }

            Controls.IconButton {
                id: stopButton

                enabled: false
                iconSource: rootDir + "assets/images/stopIcon.svg"
                width: parent.width
                height: playButton.height

                onClicked: stopProgram()
            }
        }
    }

    SplitView {
        orientation: Qt.Vertical

        anchors.top: root.top
        anchors.bottom: root.bottom
        anchors.left: mainToolbar.right
        anchors.right: root.right

        handleDelegate: Rectangle {
            height: Core.scaledSize(2)
            color: "lightGray"
        }

        SplitView {
            id: editorSplitView

            orientation: Qt.Horizontal
            Layout.fillHeight: true
            Layout.minimumHeight: Core.scaledSize(100)

            handleDelegate: Rectangle {
                width: Core.scaledSize(2)
                color: "lightGray"
            }

            CodeEditor {
                id: codeEditor

                width: Core.scaledSize(500)
                height: parent.height
                Layout.fillWidth: true
                Layout.minimumWidth: Core.scaledSize(100)

                placeHolderText: '
<style>a{ color: #e6b400; }
table {
    width: 100%;
}
td {
    width: 50%;
    padding: 1em;
}
</style>
<table>
    <tr><td>
        <b>File</b><br>
            - open file (Ctrl+O)<br>
            - save file (Ctrl+S)<br>
            - save file as (Ctrl+Shift+S)<br>
        <br><b>Run program</b><br>
            - run program (F5)<br>
            - debug run to next breakpoint (F5)<br>
            - debug run to next line (F6)<br>
        <br><b>Code</b><br>
            - show completer (Ctrl + Space)
    </td><td>
        <b>License</b> LGPL<br>
        <br><b>Repository</b><br>
             - <a href="http://bit.ly/IFJ-toolkit">thejoeejoee@VUT-FIT-IFJ-toolkit</a><br>
        <br><b>Authors</b><br>
            - <a href="http://goo.gl/7eKD7G">Son Hai Nguyen</a>, xnguye16, <a href="http://goo.gl/j5KDWY">@SonyPony</a><br>
            - <a href="http://goo.gl/thmHgr">Josef Kolář</a>, xkolar71, <a href="http://goo.gl/9b9pC9">@thejoeejoee</a><br><br>
    </td></tr>
</table>'
                lineNumbersPanelColor: "#f2f2f2"
                breakpoints: ifjDebugger.breakpoints
                currentLine: ifjDebugger.currentLine

                completer.width: Core.scaledSize(200)
                completer.visibleItemCount: Core.scaledSize(6)

                onToggleBreakpointRequest: ifjDebugger.toggleBreakpoint(line)
                onLinesAdded: ifjDebugger.handleAddedLines(lines)
                onLinesRemoved: ifjDebugger.handleRemovedLines(lines)
            }

            View.DebugStateView {
                id: debugStateView

                contentWidth: Core.scaledSize(500)
                height: parent.height
            }
        }

        Widgets.ConsoleWidget {
            id: consoleWidget

            toolbarHeight: Core.scaledSize(25)
            height: Core.scaledSize(300)
            Layout.minimumHeight: Core.scaledSize(50)

            onRunToNextLineRequest: ifjDebugger.runToNextLine()
            onRunToNextBreakPointRequest: ifjDebugger.runToNextBreakpoint()
            onReadingChanged: {
                if(root.state == "runningDebug" && reading)
                    consoleWidget.debugToolbarEnabled = false
                else if(root.state == "runningDebug" && !reading)
                    consoleWidget.debugToolbarEnabled = true
            }
        }
    }

    function runProgram() {
        root.state = "running"
        stopButton.enabled = true;
        playButton.enabled = false;
        playDebugButton.enabled = false;
        consoleWidget.debugToolbarEnabled = false
        consoleWidget.clear()
        consoleWidget.write("Program started...\n", "#002d77")
        ifjDebugger.run(codeEditor.code)
    }

    function debugProgram() {
        root.state = "runningDebug"
        stopButton.enabled = true;
        playButton.enabled = false;
        playDebugButton.enabled = false;
        consoleWidget.debugToolbarEnabled = true
        consoleWidget.clear()
        debugStateView.show()
        consoleWidget.write("Debug started...\n", "#002d77")
        ifjDebugger.debug(codeEditor.code)
    }

    function stopProgram() {
        root.state = "stopped"
        stopButton.enabled = false;
        playButton.enabled = true;
        playDebugButton.enabled = true;
        consoleWidget.debugToolbarEnabled = false
        debugStateView.hide()
        consoleWidget.stopRead()
        ifjDebugger.stop()
        consoleWidget.write("\nProgram ended.", "#002d77")
    }

    function saveFileAs() {
        root.fileActionType = "saveAs"
        fileDialog.visible = true
    }

    function saveFile() {
        if(fileIO.source == "") {
            root.fileActionType = "save"
            fileDialog.visible = true
        }

        else
            fileIO.write(codeEditor.code)
    }

    function openFile() {
        root.fileActionType = "open"
        fileDialog.visible = true
    }
 }
