pragma Singleton
import QtQuick 2.0
import QtQuick.Controls.Styles 1.4

QtObject {
    id: styles

    property QtObject completer: QtObject {
        property color color: "#272b2d"
        property color hoverColor: "#e0e0e0"
        property color textColor: "#FFFFFF"
        property color scrollBarColor: "black"
        property var typeColors: ({})
        property font font: Qt.font({family: "Roboto Light"})

        Component.onCompleted: {
            typeColors[0] = "#00bff2"
            typeColors[1] = "#ffe20d"
            typeColors[2] = "white"
            typeColors[3] = "orange"
        }
    }
}
