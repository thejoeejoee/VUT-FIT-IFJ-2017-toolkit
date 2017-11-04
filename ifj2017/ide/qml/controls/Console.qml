import QtQuick 2.7
import QtQuick.Controls 1.4

Rectangle {
    id: component

    signal textReaded(string text)

    color: "transparent"
    clip: true

    ScrollView {
        anchors.left: parent.left
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
            width: parent.width
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

                    onTextChanged: {
                        var lines = readonlyText.text.split("\n")
                        var lastLine = lines[lines.length - 1]
                        editableText.x = fm.advanceWidth(lastLine) + readonlyText.leftPadding
                    }

                    onCursorRectangleChanged: {
                        flick.moveContentAccordingToCursor(cursorRectangle)
                    }

                    FontMetrics {
                        id: fm
                        font: readonlyText.font

                        Component.onCompleted: {

                        }
                    }
                }

                TextInput {
                    id: editableText

                    y: readonlyText.y + ((readonlyText.text)
                                         ?readonlyText.contentHeight - contentHeight :0)
                    width: parent.width
                    readOnly: true

                    focus: true
                    leftPadding: 7
                    font: readonlyText.font

                    onAccepted: {
                        if(editableText.readOnly)
                            return
                        readonlyText.text += editableText.text + "\n"
                        component.textReaded(editableText.text)
                        editableText.text = ""
                        editableText.readOnly = true
                        editableText.focus = false
                    }
                }
            }
        }
    }

    function clear() {
        readonlyText.clear()
    }

    function read() {
        var lines = readonlyText.text.split("\n")
        var lastLine = lines[lines.length - 1]

        editableText.forceActiveFocus()
        flick.scrollToEnd()
        editableText.readOnly = false;
    }

    function write(text) {
        readonlyText.text += text
    }
}
