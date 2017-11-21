import QtQuick 2.7
import QtQuick.Controls 1.4
import FormattedTextWriter 1.0

Rectangle {
    id: component

    signal textReaded(string text)
    property bool reading: false

    color: "transparent"
    clip: true

    FormattedTextWriter {
        id: formattedTextWriter
        target: readonlyText
    }

    TextArea {
        id: readonlyText

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        textMargin: 0
        anchors.leftMargin: Core.scaledSize(7)

        text: ""
        selectByMouse: true
        readOnly: true
        font.pixelSize: Core.scaledSize(16)
        frameVisible: false

        onTextChanged: {
            var lines = readonlyText.text.split("\n")
            var lastLine = lines[lines.length - 1]
            editableText.x = fm.advanceWidth(lastLine) + readonlyText.anchors.leftMargin
        }

        onFocusChanged: {
            if(focus)
                editableText.forceActiveFocus()
        }

        FontMetrics {
            id: fm
            font: readonlyText.font
        }
    }

    TextInput {
        id: editableText

        y: readonlyText.y + ((readonlyText.text)
                             ?readonlyText.contentHeight - contentHeight :0) - readonlyText.flickableItem.contentY

        width: parent.width
        readOnly: true
        font: readonlyText.font

        onAccepted: {
            if(editableText.readOnly)
                return
            component.write(editableText.text + "\n")
            component.textReaded(editableText.text)
            editableText.text = ""
            editableText.readOnly = true
            editableText.focus = false
            component.reading = false
        }
    }

    function clear() {
        formattedTextWriter.clear()
    }

    function stopRead() {
        editableText.readOnly = true
        component.reading = false
    }

    function read() {
        editableText.forceActiveFocus()
        component.reading = true
        editableText.readOnly = false;
    }

    function write(text, color) {
        color = (color == undefined) ?readonlyText.color :color
        formattedTextWriter.write(text, color)
    }
}
