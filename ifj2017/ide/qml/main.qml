import QtQuick 2.7
import QtQuick.Controls 1.4

import StyleSettings 1.0

import "code"

ApplicationWindow {
    visible: true
    width: 640
    height: 480
    title: qsTr("Advánc Ifj Creator")

    Rectangle {
        id: root
        color: "white"
        anchors.fill: parent
    }

    // Main bar
    Rectangle {
        id: mainToolbar

        width: 55
        height: parent.height

        color: "#2f2f2f"

        Button{
            iconSource: rootDir + "assets/images/playIcon.svg"
            width: 50
            height: width

            x: 0
            y: 0
        }
    }

    CodeEditor {
        id: codeEditor

        lineNumbersPanelColor: "#f2f2f2"

        completer.width: 200
        completer.visibleItemCount: 6

        anchors.left: mainToolbar.right
        anchors.right: root.right
        anchors.top: root.top
        anchors.bottom: root.bottom
    }
}
