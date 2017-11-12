import QtQuick 2.7
import QtQuick.Controls 1.4

import "../controls" as Controls

Rectangle {
    id: component

    property alias searchPattern: textInput.text
    visible: false

    Row {
        leftPadding: Core.scaledSize(5)
        spacing: Core.scaledSize(10)
        anchors.fill: parent

        Text {
            text: qsTr("Find:")
            color: "white"

            font.pixelSize: component.height * 0.5
            anchors.verticalCenter: parent.verticalCenter
        }

        TextField {
            id: textInput

            height: parent.height * 0.8
            width: Core.scaledSize(300)

            anchors.verticalCenter: parent.verticalCenter
        }
    }

    IconButton {
        id: clearConsoleButton

        iconSource: rootDir + "assets/images/crossIcon.svg"
        width: height
        height: parent.height * 0.8

        anchors.verticalCenter: parent.verticalCenter
        anchors.right: parent.right
        anchors.rightMargin: Core.scaledSize(5)

        onClicked: component.hide()
    }

    function show() {
        component.visible = true
        textInput.forceActiveFocus()
    }

    function hide() {
        component.visible = false
        component.searchPattern = ""
    }
}
