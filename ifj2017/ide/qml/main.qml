import QtQuick 2.7
import QtQuick.Controls 1.4
import QtQuick.Dialogs 1.0
import QtQuick.Layouts 1.0
import QtQuick.Controls.Styles 1.4
import QtQuick.Dialogs 1.2

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
    width: Core.scaledSize(1200)
    height: Core.scaledSize(800)
    title: fileIO.source + ((fileIO.source) ?" - " :"") + qsTr("Advánc IFJcode17 IDE ") + packageVersion

    menuBar: MenuBar {
        Menu {
            title: qsTr("File")
            MenuItem {
                text: qsTr("Open...\t\tCtrl+O")
                onTriggered: openFile()
            }

            MenuItem {
                text: qsTr("Save...\t\tCtrl+S")
                onTriggered: saveFile()
            }

            MenuItem {
                text: qsTr("Save as..\t\tCtrl+Shift+S")
                onTriggered: saveFileAs()
            }
        }

        style: MenuBarStyle {
            background: Rectangle { color: "lightGray" }
            itemDelegate: Rectangle {
                implicitWidth: lab.contentWidth * 2
                implicitHeight: lab.contentHeight * 1.2
                color: styleData.selected || styleData.open ? "#494949" : "transparent"

                Text {
                    id: lab
                    color: (styleData.selected  || styleData.open) ? "white" : "black"
                    text: styleData.text
                    font.pixelSize: Core.scaledSize(13)

                    anchors.centerIn: parent
                }
            }

            menuStyle: MenuStyle {
                itemDelegate {
                    background: Rectangle {
                        color: (styleData.selected) ? "lightGray" : "#ececec"
                    }

                    label: Text {
                        color: (styleData.selected) ? "black" : "black"
                        text: styleData.text
                        font.pixelSize: Core.scaledSize(11)
                    }
                }
            }
        }
    }

    onClosing: {
        if(codeEditor.diffLines.length) {
            close.accepted = false
            saveBeforeExitDialog.visible = true
        }
    }

    MessageDialog {
        id: saveBeforeExitDialog

        title: qsTr("Save changes")
        text: ("Changes are not saved. Do you want to save them?")
        standardButtons: StandardButton.Yes | StandardButton.No | StandardButton.Abort

        onYes: {
            root.fileActionType = "saveBeforeQuit"
            saveFile()
            root.fileActionType = "saveBeforeQuit"
        }

        onNo: {
            stopProgram()
            Qt.quit()
        }
        onRejected: visible = false
    }

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

    FontLoader {
        source: rootDir + "assets/fonts/SourceCodePro-Medium.otf"
    }

    FileDialog {
        id: fileDialog

        folder: shortcuts.documents
        selectMultiple: false
        selectExisting: (root.fileActionType != "save" && root.fileActionType != "saveAs")
        nameFilters: [ "IFJ files (*.IFJcode17)", "All files (*)" ]

        onAccepted: {
            fileIO.source = fileDialog.fileUrl
            if(root.fileActionType == "open") {
                if(root.state != "stopped")
                    stopProgram()
                codeEditor.code = fileIO.read()
                codeEditor.removesDiffMarks()
            }
            else if(root.fileActionType == "save" || root.fileActionType == "saveAs" || root.fileActionType == "saveBeforeQuit") {
                fileIO.write(codeEditor.code)
                codeEditor.removesDiffMarks()
            }

            if(root.fileActionType == "saveBeforeQuit") {
                stopProgram()
                Qt.quit()
            }
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
        sequence: "Ctrl+F"
        onActivated: searchPanel.show()
    }

    Shortcut {
        sequence: "Esc"
        enabled: searchPanel.visible && (searchPanel.focus || !codeEditor.completer.visible)
        onActivated: searchPanel.hide()
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
        orientation: Qt.Horizontal

        anchors.top: root.top
        anchors.bottom: root.bottom
        anchors.left: mainToolbar.right
        anchors.right: root.right

        handleDelegate: Rectangle {
            width: Core.scaledSize(2)
            color: "lightGray"
        }

        SplitView {
            id: editorSplitView

            orientation: Qt.Vertical
            Layout.fillWidth: true
            Layout.minimumWidth: Core.scaledSize(100)

            handleDelegate: Rectangle {
                height: Core.scaledSize(2)
                color: "#e5e5e5"
            }

            CodeEditor {
                id: codeEditor

                width: Core.scaledSize(500)
                height: parent.height
                Layout.fillHeight: true
                Layout.minimumHeight: Core.scaledSize(100)

                editorDisabled: root.state != "stopped"
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
            - open file (%1+O)<br>
            - save file (%1+S)<br>
            - save file as (%1+Shift+S)<br>
        <br><b>Run program</b><br>
            - run program (F5)<br>
            - debug run to next breakpoint (F5)<br>
            - debug run to next line (F6)<br>
        <br><b>Code</b><br>
            - show completer (%1+Space) (Cmd+J on OS X)<br>
            - find (%1 + F)<br>
            - hide find panel (Esc)
    </td><td>
        <b>Version</b> %2<br>
        <b>License</b> GPL v3<br>
        <br><b>Repository</b><br>
             - <a href="http://bit.ly/IFJ-toolkit">thejoeejoee@VUT-FIT-IFJ-toolkit</a><br>
        <br><b>Authors</b><br>
            - <a href="http://goo.gl/7eKD7G">Son Hai Nguyen</a>, xnguye16, <a href="http://goo.gl/j5KDWY">@SonyPony</a><br>
            - <a href="http://goo.gl/thmHgr">Josef Kolář</a>, xkolar71, <a href="http://goo.gl/9b9pC9">@thejoeejoee</a><br><br>
    </td></tr>
</table>'.arg((ossystem != "Darwin") ?"Ctrl" :"Cmd").arg(packageVersion)
                lineNumbersPanelColor: "#f2f2f2"
                breakpoints: ifjDebugger.breakpoints
                currentLine: ifjDebugger.currentLine

                completer.width: Core.scaledSize(200)
                completer.visibleItemCount: Core.scaledSize(6)

                onToggleBreakpointRequest: ifjDebugger.toggleBreakpoint(line)
                onLinesAdded: ifjDebugger.handleAddedLines(lines)
                onLinesRemoved: ifjDebugger.handleRemovedLines(lines)
            }

            Controls.SearchPanel {
                id: searchPanel

                height: Core.scaledSize(25)
                Layout.maximumHeight: Core.scaledSize(25)
                color: "#2f2f2f"

                onSearchPatternChanged: codeEditor.setSearchPattern(searchPattern)
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

        View.DebugStateView {
            id: debugStateView

            callStackModel: ifjDebugger.callStackModel

            contentWidth: Core.scaledSize(500)
            height: parent.height

            onLineClicked: {
                codeEditor.scrollToLine(line)
                codeEditor.highlightLine(line)
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

        else {
            fileIO.write(codeEditor.code)
            codeEditor.removesDiffMarks()
            if(root.fileActionType == "saveBeforeQuit") {
                stopProgram()
                Qt.quit()
            }
        }
    }

    function openFile() {
        root.fileActionType = "open"
        fileDialog.visible = true
    }
 }
