import QtQuick 2.0
import QtQuick.Controls 1.4

Rectangle {
    id: component

    signal clicked(var itemData)

    property alias model: repeater.model
    property alias titleColor: title.color
    property color titleTextColor: "black"
    property string title: ""

    color: "white"

    Rectangle {
        id: title
        width: parent.width
        height: Core.scaledSize(25)


        Text {
            text: component.title
            color: component.titleTextColor

            anchors.left: parent.left
            anchors.leftMargin: Core.scaledSize(5)
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    ScrollView {
        id: scrollView

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: title.bottom
        anchors.bottom: parent.bottom

        Column {
            Repeater {
                id: repeater

                delegate: Item {

                    width: scrollView.flickableItem.width
                    height: Core.scaledSize(25)

                    Text {
                        text: modelData[0] + "\t" + modelData[1]
                        height: parent.height

                        font.pixelSize: Core.scaledSize(15)

                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.leftMargin: Core.scaledSize(5)
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Rectangle {
                        color: "black"
                        opacity: (mouseArea.containsMouse) ?0.2 :0
                        anchors.fill: parent
                        Behavior on opacity { NumberAnimation { duration: 200 }}
                    }

                    MouseArea {
                        id: mouseArea

                        hoverEnabled: true
                        anchors.fill: parent
                        onClicked: component.clicked(modelData[0])
                    }
                }
            }
        }
    }
}
