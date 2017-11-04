import QtQuick 2.0

Rectangle {
    id: component

    signal runToNextBreakpointRequest()
    signal runTonextLineRequest()

    Row {
        anchors.fill: parent
        Item { width: 5; height: parent.height }

        Text {
            text: qsTr("Program output")
            color: "white"

            anchors.verticalCenter: parent.verticalCenter
        }

        Item { width: 25; height: parent.height }

        Rectangle {
            width: 1
            height: parent.height * 0.7
            color: "gray"
            anchors.verticalCenter: parent.verticalCenter
        }

        Item { width: 5; height: parent.height }

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
