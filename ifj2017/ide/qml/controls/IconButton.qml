import QtQuick 2.0
import QtGraphicalEffects 1.0

Clickable {
    id: component

    property url iconSource

    Image {
        id: icon

        source: component.iconSource
        fillMode: Image.PreserveAspectFit
        sourceSize: Qt.size(width, height)

        width: parent.width * 0.6
        height: parent.height * 0.6

        anchors.centerIn: parent
    }

    Desaturate {
        id: desaturated

        anchors.fill: icon
        source: icon
        desaturation: (component.enabled) ?0 :1
    }

    Rectangle {
        id: hoverBackground

        visible: false
        opacity: 0.4
        color: "white"
        anchors.fill: parent
    }

    MouseArea {
        hoverEnabled: true
        propagateComposedEvents: true
        anchors.fill: parent

        onEntered: hoverBackground.visible = true
        onExited: hoverBackground.visible = false
        onClicked: mouse.accepted = false
    }
}
