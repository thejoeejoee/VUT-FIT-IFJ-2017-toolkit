import QtQuick 2.7
import QtQuick.Controls 1.4
import TreeViewModel 1.0
import Debugger 1.0
import StyleSettings 1.0
import IOWrapper 1.0

import "code"
import "controls" as Controls
import "containers"

ApplicationWindow {
    visible: true
    width: 1000
    height: 800
    title: qsTr("Advánc Ifj Creator")

    Rectangle {
        id: root
        color: "white"
        anchors.fill: parent
    }

    // INFO test
    Debugger {
        id: ifjDebugger
        model: debugStateModel
        ioWrapper: consoleIOWrapper

        onCurrentLineChanged: {
            console.log(line)
        }

        onProgramEnded: {
            stopProgram()
        }
    }

    IOWrapper {
        id: consoleIOWrapper
        onReadRequest: {
            consoleWidget.read()
        }

        onWriteRequest: consoleWidget.write(text)
    }

    // Main bar
    Rectangle {
        id: mainToolbar

        width: 55
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

                onClicked: {
                    runProgram()
//                    consoleWidget.write("dfsdfsdf")
//                    consoleWidget.read()
//                    if(com.visible)
//                        com.hide()
//                    else
//                        com.show()
                }
            }

            Controls.IconButton {
                id: playDebugButton

                iconSource: rootDir + "assets/images/playBugIcon.svg"
                width: parent.width
                height: playButton.height

                onClicked: {
                    debugProgram()
                }
            }

            Controls.IconButton {
                id: stopButton

                enabled: false
                iconSource: rootDir + "assets/images/stopIcon.svg"
                width: parent.width
                height: playButton.height

                onClicked: {
                    stopProgram()
//                    codeEditor.removesDiffMarks()

//                    if(com.visible)
//                        com.hide()
//                    else
//                        com.show()
                }
            }
        }
    }

    CodeEditor {
        id: codeEditor

        lineNumbersPanelColor: "#f2f2f2"
        breakpoints: ifjDebugger.breakpoints
        currentLine: ifjDebugger.currentLine

        completer.width: 200
        completer.visibleItemCount: 6

        anchors.left: mainToolbar.right
        anchors.right: com.left
        anchors.top: root.top
        anchors.bottom: consoleWidget.top

        onToggleBreakpointRequest: {
            ifjDebugger.toggleBreakpoint(line)
        }

        onLinesAdded: ifjDebugger.handleAddedLines(lines)
        onLinesRemoved: ifjDebugger.handleRemovedLines(lines)
    }

    Controls.DebugToolbar {
        id: debugToolbar

        color: "#2f2f2f"
        height: 25

        anchors.left: consoleWidget.left
        anchors.right: consoleWidget.right
        anchors.bottom: consoleWidget.top

        onRunToNextBreakpointRequest: ifjDebugger.runToNextBreakpoint()
        onRunTonextLineRequest: ifjDebugger.runToNextLine()
    }

    Controls.Console {
        id: consoleWidget

        height: 300

        anchors.left: mainToolbar.right
        anchors.right: com.left
        anchors.bottom: root.bottom

        onTextReaded: {
            consoleIOWrapper.handleConsoleRead(text)
        }
    }

    TreeViewModel {
            id: debugStateModel
        }

    SlideWidget {
        id: com

        width: 500
        height: parent.height
        color: "red"

        TreeView {
            width: 500
            height: 500
            model: debugStateModel
            itemDelegate: Rectangle {
               color: "white"
               height: 20

               Text {
                   anchors.verticalCenter: parent.verticalCenter
                   text: styleData.value === undefined ? "" : styleData.value // The branches don't have a description_role so styleData.value will be undefined
               }
           }

            TableViewColumn {
                role: "name_col"
                title: "Name"
            }
            TableViewColumn {
                role: "value_col"
                title: "Value"
            }
            TableViewColumn {
                role: "type_col"
                title: "Type"
            }
        }
    }

//    states: [
//        State {
//            name: "stopped"
//            PropertyChanges { target: stopButton; enabled: false }
//            PropertyChanges { target: playButton; enabled: true }
//            PropertyChanges { target: playDebugButton; enabled: true }
//            StateChangeScript { script: {
//                    com.hide()
//                    ifjDebugger.stop()
//                }
//            }
//        }
//    ]

    function runProgram() {
        stopButton.enabled = true;
        playButton.enabled = false;
        playDebugButton.enabled = false;
        consoleWidget.clear()
        consoleWidget.write("Program started...\n")
        ifjDebugger.run(codeEditor.code)
    }

    function debugProgram() {
        stopButton.enabled = true;
        playButton.enabled = false;
        playDebugButton.enabled = false;
        consoleWidget.clear()
        com.show()
        consoleWidget.write("Debug started...\n")
        ifjDebugger.debug(codeEditor.code)
    }

    function stopProgram() {
        stopButton.enabled = false;
        playButton.enabled = true;
        playDebugButton.enabled = true;
        com.hide()
        ifjDebugger.stop()
        // TODO exit codes
        consoleWidget.write("\nProgram ended")
    }
 }
