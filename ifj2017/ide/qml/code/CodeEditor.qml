import QtQuick 2.0
import QtQuick.Controls 1.4

import "../controls" as Controls

Item {
    id: component

    property alias textComponent: textEdit
    property alias font: textEdit.font
    property alias code: textEdit.text
    property alias lineNumbersPanelColor: lineNumbers.color
    property color lineNumberColor: "gray"

    clip: true

    ScrollView {
        anchors.fill: parent
        verticalScrollBarPolicy: Qt.ScrollBarAlwaysOn

        Flickable {
            id: flick

            clip: true
            interactive: false

            contentWidth: textEdit.paintedWidth
            contentHeight: textEdit.paintedHeight
            width: parent.width - lineNumbers.width
            height: parent.height

            function moveContentAccordingToCursor(cr) {
                // vertical move
                if(flick.contentY + flick.height < cr.y + cr.height)
                    flick.contentY += cr.y + cr.height - flick.height - flick.contentY
                else if(flick.contentY > cr.y)
                    flick.contentY += cr.y - flick.contentY

                // horizontal move
                if(flick.contentX + flick.width < cr.x + cr.width)
                    flick.contentX += cr.x - flick.width - flick.contentX
                else if(flick.contentX > cr.x)
                    flick.contentX += cr.x - flick.contentX
            }

            TextEdit {
                id: textEdit

                focus: true
                font.pixelSize: 16
                selectByMouse: true

                x: lineNumbers.width
                width: flick.width
                height: flick.height

                onCursorRectangleChanged: {
                    flick.moveContentAccordingToCursor(cursorRectangle)
                }
            }
        }
    }

    // LINE NUMBERS
    Rectangle {
        id: lineNumbers

        width: 50
        height: parent.height

        Column {
            y: -flick.contentY
            Repeater {
                model: textEdit.lineCount
                delegate: Rectangle {
                    width: lineNumbers.width
                    height: flick.contentHeight / textEdit.lineCount
                    color: "transparent"

                    Text {
                        text: modelData
                        color: component.lineNumberColor
                        anchors.centerIn: parent
                    }
                }
            }
        }
    }
}

