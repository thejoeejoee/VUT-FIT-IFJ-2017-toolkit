import QtQuick 2.0

Rectangle {
    id: component

    property int contentWidth
    default property alias content: container.children

    signal show()
    signal hide()

    visible: (width != 0)
    width: 0

    onShow: NumberAnimation {
        target: component
        property: "width"
        to: contentWidth
        duration: 200
        easing.type: Easing.InOutQuad
    }
    onHide: NumberAnimation {
        target: component
        property: "width"
        to: 0
        duration: 200
        easing.type: Easing.InOutQuad
    }

    Item {
        id: container
        anchors.fill: parent
    }
}
