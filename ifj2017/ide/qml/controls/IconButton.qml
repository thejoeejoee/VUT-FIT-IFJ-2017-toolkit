import QtQuick 2.0

Clickable {
    id: component

    property url iconSource
    property url iconDisabledSource

    Image {
        id: icon

        source: (component.enabled) ?component.iconSource :component.iconDisabledSource
        fillMode: Image.PreserveAspectFit
        anchors.fill: parent
        sourceSize: Qt.size(width, height)
    }
}
