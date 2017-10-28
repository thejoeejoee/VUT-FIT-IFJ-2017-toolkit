import QtQuick 2.7
import QtQuick.Controls 1.4

Rectangle {
    id: component

    signal textReaded(string text)
    property color lineMarksColor: "gray"

    color: "transparent"
    border.color: "red"
    border.width: 1
    clip: true

    ScrollView {
        anchors.left: lineMarks.right
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom

        verticalScrollBarPolicy: Qt.ScrollBarAlwaysOn

        Flickable {
            id: flick

            clip: true
            interactive: false

            contentWidth: readonlyText.contentWidth
            contentHeight: readonlyText.contentHeight + editableText.contentHeight
            width: parent.width - lineMarks.width
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

            Item {
                width: flick.width

                TextEdit {
                    id: readonlyText

                    height: editableText
                    width: parent.width

                    leftPadding: 7
                    selectByMouse: true
                    readOnly: true
                    font.pixelSize: 16
                    onFocusChanged: {   // pass focus to editable line
                        if(focus) {
                            focus = false
                            editableText.focus = true
                        }
                    }

                    onCursorRectangleChanged: {
                        flick.moveContentAccordingToCursor(cursorRectangle)
                    }
                }

                Rectangle {
                    color: "lightGray"
                    anchors.fill: editableText
                }

                TextInput {
                    id: editableText

                    y: readonlyText.y + readonlyText.contentHeight
                    width: parent.width

                    focus: true
                    leftPadding: 7
                    font: readonlyText.font

                    onFocusChanged: {
                        if(focus) {
                            flick.contentY = flick.contentHeight - flick.height

                        }
                    }

                    onAccepted: {
                        readonlyText.append(editableText.text)
                        component.textReaded(editableText.text)
                        editableText.text = ""
                        editableText.readOnly = true
                    }

//                    onCursorRectangleChanged: {
//                        flick.moveContentAccordingToCursor(cursorRectangle)
//                    }
                }
            }
        }
    }

    // LINE MARKS
    Item {
        id: lineMarks

        width: 10
        height: parent.height

        Column {
            y: -flick.contentY
            Repeater {
                model: readonlyText.lineCount
                delegate: Rectangle {
                    width: lineMarks.width
                    height: flick.contentHeight / (readonlyText.lineCount + 1)
                    color: "transparent"

                    Text {
                        text: "  >"
                        font: readonlyText.font
                        color: "red"/*component.lineNumberColor*/
                        anchors.centerIn: parent
                    }
                }
            }
        }
    }

    function read() {
        editableText.readOnly = false;
    }
}
