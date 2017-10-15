pragma Singleton
import QtQuick 2.0
import QtQuick.Controls.Styles 1.4

QtObject {
    id: styles

    property QtObject completer: QtObject {
        property color color: "black"
        property color hoverColor: "#ED1946"
        property color textColor: "#C1C0C0"
        property color scrollBarColor: "#9F9F9F"
        property var typeColors: ({})
        property font font: Qt.font({family: "Roboto Light"})

        Component.onCompleted: {
            typeColors[0] = "#EF4223"
            typeColors[1] = "#C1C0C0"
        }
    }
}
