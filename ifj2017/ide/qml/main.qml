import QtQuick 2.7
import QtQuick.Controls 1.4

import "code"

ApplicationWindow {
    visible: true
    width: 640
    height: 480
    title: qsTr("Advánc Ifj Creator")

    Rectangle {
        color: "white"
        anchors.fill: parent
    }

    CodeEditor {
        lineNumbersPanelColor: "#f2f2f2"
        anchors.fill: parent
    }
}
