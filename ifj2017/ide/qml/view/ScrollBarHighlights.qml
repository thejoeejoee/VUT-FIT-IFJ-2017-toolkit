import QtQuick 2.0
import QtQuick.Controls 1.4

Item {
    id: component

    property TextArea target
    property var model: []
    property color color: "black"

    width: 13
    parent: target
    anchors.right: target.right
    anchors.top: target.top
    anchors.bottom: target.bottom

    Repeater {
        model: component.model
        delegate: Rectangle {
            y: (target.contentHeight / (target.lineCount - 1))  * (modelData - 1) * target.flickableItem.visibleArea.heightRatio - ((modelData == target.lineCount) ?height :0)
            width: Core.scaledSize(13)
            height: Core.scaledSize(2)

            color: component.color
        }
    }
}
