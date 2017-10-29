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
        id: textOutput

        property var streamHistory: []

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

            onContentHeightChanged: flick.scrollToEnd()

            function scrollToEnd() {
                if(flick.contentHeight > flick.height) {
                    flick.contentY = flick.contentHeight - flick.height
                }
            }

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

                    height: 0
                    width: parent.width

                    text: ""
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

                    y: readonlyText.y + ((readonlyText.text) ?readonlyText.contentHeight :0)
                    width: parent.width
                    readOnly: true

                    focus: true
                    leftPadding: 7
                    font: readonlyText.font

                    onAccepted: {
                        if(editableText.readOnly)
                            return
                        readonlyText.append(editableText.text)
                        component.textReaded(editableText.text)
                        editableText.text = ""
                        editableText.readOnly = true
                        editableText.focus = false
                    }
                }
            }
        }
    }

    // LINE MARKS
    Item {
        id: lineMarks

        width: 15
        height: parent.height

        Column {
            y: -flick.contentY
            Repeater {
                model: textOutput.streamHistory
                delegate: Rectangle {
                    width: lineMarks.width
                    height: flick.contentHeight / (readonlyText.lineCount + 1)
                    color: "transparent"

                    Text {
                        text: modelData
                        font: readonlyText.font
                        color: "red"/*component.lineNumberColor*/
                        anchors.centerIn: parent
                    }
                }
            }
        }
    }

    function read() {
        flick.scrollToEnd()
        textOutput.streamHistory.push("<")
        textOutput.streamHistoryChanged()
        editableText.readOnly = false;
    }

    function write(text) {
        textOutput.streamHistory.push(">")
        textOutput.streamHistoryChanged()
        readonlyText.append(text)
    }
}
