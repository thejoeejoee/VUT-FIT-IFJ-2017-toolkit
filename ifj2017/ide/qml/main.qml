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
            spacing: 20
            width: parent.width * 0.5
            height: playButton.width * 3 + 2 * spacing

            anchors.bottom: parent.bottom
            anchors.bottomMargin: spacing
            anchors.horizontalCenter: parent.horizontalCenter

            Controls.IconButton {
                id: playButton

                iconSource: rootDir + "assets/images/playIcon.svg"
                width: parent.width
                height: width

                onClicked: {
                    ifjDebugger.debug(codeEditor.code)
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
                height: width

                onClicked: {
//                    consoleWidget.read()
                    ifjDebugger.runToNextBreakPoint()
                }
            }

            Controls.IconButton {
                id: stopButton

                iconSource: rootDir + "assets/images/stopIcon.svg"
                width: parent.width
                height: width

                onClicked: {
//                    codeEditor.removesDiffMarks()
                    if(com.visible)
                        com.hide()
                    else
                        com.show()
                }
            }
        }
    }

//    TreeViewModel {
//            id: theModel
//        }
//        TreeView {
//            anchors.left: mainToolbar.right
//            width: 500
//            height: 500
//            model: theModel
//            itemDelegate: Rectangle {
//               color: "white"
//               height: 20

//               Text {
//                   anchors.verticalCenter: parent.verticalCenter
//                   text: styleData.value === undefined ? "" : styleData.value // The branches don't have a description_role so styleData.value will be undefined
//               }
//           }

//            TableViewColumn {
//                role: "name_col"
//                title: "Name"
//            }
//            TableViewColumn {
//                role: "value_col"
//                title: "Value"
//            }
//            TableViewColumn {
//                role: "type_col"
//                title: "Type"
//            }
//        }

    CodeEditor {
        id: codeEditor

        lineNumbersPanelColor: "#f2f2f2"
        breakpoints: ifjDebugger.breakpoints

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

    Controls.Console {
        id: consoleWidget

        height: 300

        anchors.left: mainToolbar.right
        anchors.right: com.left
        anchors.bottom: root.bottom

//        Component.onCompleted: read()
        onTextReaded: {
            console.log(text)
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
}
