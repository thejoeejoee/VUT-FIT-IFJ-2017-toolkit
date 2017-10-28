import QtQuick 2.0

Rectangle {
    id: component

    default property alias content: container.children

    signal show()
    signal hide()

    visible: (component.anchors.leftMargin != 0)
    anchors.left: parent.right
    anchors.leftMargin: 0

    Behavior on anchors.leftMargin {
        NumberAnimation { duration: 150; easing.type: Easing.InOutQuad }
    }

    onShow: component.anchors.leftMargin = -component.width
    onHide: component.anchors.leftMargin = 0

    Item {
        id: container
        anchors.fill: parent
    }
}
