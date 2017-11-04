import QtQuick 2.0

Rectangle {
    id: component

    signal runToNextBreakpointRequest()
    signal runTonextLineRequest()

    Row {
        anchors.fill: parent

        Text {
            text: qsTr("Program output")
            color: "white"

            anchors.verticalCenter: parent.verticalCenter
        }

        IconButton {
            id: runToNextBreakpointButton

            iconSource: rootDir + "assets/images/debugNextBreakpointIcon.svg"
            width: height
            height: parent.height

            anchors.verticalCenter: parent.verticalCenter

            onClicked: component.runToNextBreakpointRequest()
        }

        IconButton {
            id: runToNextLineButton

            iconSource: rootDir + "assets/images/debugNextLineIcon.svg"
            width: height
            height: parent.height

            anchors.verticalCenter: parent.verticalCenter

            onClicked: component.runTonextLineRequest()
        }
    }
}
