import QtQuick 2.7
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4

import StyleSettings 1.0
import ExpSyntaxHighlighter 1.0
import ExpAnalyzer 1.0
import CodeAnalyzer 1.0
import DiffCodeAnalyzer 1.0

import "../controls"
import "../view"

Item {
    id: component

    signal toggleBreakpointRequest(int line)
    signal linesRemoved(var lines)
    signal linesAdded(var lines)

    property var breakpoints: []
    property alias completer: completer
    property alias textComponent: textEdit
    property alias font: textEdit.font
    property alias code: textEdit.text
    property alias lineNumbersPanelColor: lineNumbers.color
    property color lineNumberColor: "gray"
    property int currentLine: -1
    property string placeHolderText: ""
    property var diffLines: []
    property alias editorDisabled: textEdit.readOnly


    clip: true

    onCurrentLineChanged: {
        if(currentLine != -1)
            component.scrollToLine(currentLine)
    }

    Item {
        z: 1
        visible: opacity != 0
        opacity: textEdit.text == ""
        anchors.fill: parent

        Behavior on opacity {
            NumberAnimation { duration: 150 }
        }

        Label {
            color: "gray"
            textFormat: Text.RichText;
            text: component.placeHolderText
            font.pixelSize: Core.scaledSize(20)

            anchors.centerIn: parent
            onLinkActivated: Qt.openUrlExternally(link)
        }
    }

    TextArea {
        id: textEdit

        focus: true
        font.pixelSize: Core.scaledSize(17)
        font.family: "Source Code Pro Medium"
        selectByMouse: true
        frameVisible: false
        textMargin: 0
        wrapMode: TextEdit.NoWrap

        anchors.leftMargin: Core.scaledSize(7)
        anchors.left: lineNumbers.right
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom

        onLineCountChanged: {
            component.diffLines = diffCodeAnalyzer.compare(textEdit.text)
            diffCodeAnalyzer.saveTempCode(textEdit.text)
        }

        onTextChanged: {
            updateCompleterModel()
            component.diffLines = diffCodeAnalyzer.compare(textEdit.text)
            diffCodeAnalyzer.saveTempCode(textEdit.text)
        }
        onSelectedTextChanged: {
            if(textComponent.selectedText.length) {
                completer.model = completer.constantModel
                completer.currentText = ""
            }
        }

        onCursorPositionChanged: updateCompleterModel()
        style: TextAreaStyle {
            handle: Rectangle {
                implicitWidth: 14
                implicitHeight: 14
                color: "lightGray"
            }

            scrollBarBackground: Item {
                implicitWidth: 14
                implicitHeight: 14
            }

            incrementControl: Item {}
            decrementControl: Item {}
        }

        Rectangle{
            id: currentLineMark
            width: parent.width
            height: textEdit.contentHeight / textEdit.lineCount
            y: (component.currentLine - 1) * height - textEdit.flickableItem.contentY
            color: "red"
            opacity: 0.4
        }

        Rectangle{
            id: lineHighlighter

            signal show()

            width: parent.width
            height: textEdit.contentHeight / textEdit.lineCount

            color: "black"
            opacity: 0

            onShow: SequentialAnimation {
                NumberAnimation { target: lineHighlighter; property: "opacity"; from: 0; to: 0.4; duration: 300; easing.type: Easing.OutQuart }
                NumberAnimation { target: lineHighlighter; property: "opacity"; easing.type: Easing.InQuart; from: 0.4; to: 0; duration: 300 }
            }
        }
    }

    ScrollBarHighlights {
        target: textEdit
        model: component.breakpoints
        color: "red"
    }

    ScrollBarHighlights {
        target: textEdit
        model: esh.searchMatchedLines
        color: "green"
    }

    // LINE NUMBERS
    Rectangle {
        id: lineNumbers

        width: Core.scaledSize(55)
        height: parent.height

        Column {
            y: -textEdit.flickableItem.contentY

            Repeater {
                model: textEdit.lineCount
                delegate: Rectangle {
                    width: lineNumbers.width
                    height: textEdit.contentHeight / textEdit.lineCount
                    color: "transparent"

                    Text {
                        id: text

                        text: modelData + 1
                        color: component.lineNumberColor
                        anchors.right: parent.right
                        anchors.rightMargin: Core.scaledSize(10)

                        anchors.verticalCenter: parent.verticalCenter
                    }

                    // diff mark
                    Rectangle {
                        color: "green"
                        visible: (component.diffLines.indexOf(modelData + 1) != -1)
                        width: 2
                        height: parent.height

                        anchors.left: text.right
                        anchors.leftMargin: Core.scaledSize(4)
                    }

                    Rectangle {
                        id: debuggerMark

                        color: "red"
                        width: height
                        height: parent.height * 0.7
                        radius: height
                        visible: (component.breakpoints.indexOf(modelData + 1) != -1)

                        anchors.right: text.left
                        anchors.rightMargin: Core.scaledSize(4)
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: component.toggleBreakpointRequest(modelData + 1)
                    }
                }
            }
        }
    }

    FontMetrics {
        id: fmCodeInput
        font: textEdit.font
    }

    DiffCodeAnalyzer {
        id: diffCodeAnalyzer

        onRemovedLines: component.linesRemoved(lines)
        onAddedLines: component.linesAdded(lines)
    }

    ExpAnalyzer {
        id: exa
        target: textEdit
    }

    ExpSyntaxHighlighter {
        id: esh
        target: textEdit

        Component.onCompleted: {
            var rules = CodeAnalyzer.highlightRules
            for(var key in rules) {
                if(typeof rules[key]["color"] == "object")
                    esh.addHighlightMultiColorRule(rules[key]["pattern"], rules[key]["color"], esh.target.font)
                else
                    esh.addHighlightSingleColorRule(rules[key]["pattern"], rules[key]["color"], esh.target.font)
            }
        }
    }

    Completer {
        id: completer

        property real unnormilizedY: textEdit.cursorRectangle.y + textEdit.cursorRectangle.height + textEdit.y - textEdit.flickableItem.contentY

        x: component.calcTextInfoPos(width)
        y: unnormilizedY - ((unnormilizedY + completer.height > textEdit.height) ?completer.height + currentLineMark.height :0)
        z: 2
        itemHeight: Core.scaledSize(20)

        opacity: 0.8
        color: StyleSettings.completer.color
        hoverColor: StyleSettings.completer.hoverColor
        textColor: StyleSettings.completer.textColor
        scrollBarColor: StyleSettings.completer.scrollBarColor

        constantModel: CodeAnalyzer.completerModel
        target: textEdit
        onItemChoosed: expandExpression(currentItem["identifier"])
    }

    function calcTextInfoPos(infoWidth) {
        var textDocument = textEdit
        if(textDocument.cursorRectangle.x + infoWidth + fmCodeInput.advanceWidth(" ") < textDocument.width)
            return textDocument.cursorRectangle.x + textDocument.x
        else
            return textDocument.x + textDocument.width - infoWidth - textDocument.textMargin
    }

    function updateCompleterModel() {
        CodeAnalyzer.code = component.code
        var textDocument = component.textComponent
        var lastChar = textDocument.text.slice(-1)
        var currentWord = exa.currentWord()

        if(textDocument.cursorPosition)
            lastChar = textDocument.text[textDocument.cursorPosition - 1]

        completer.currentText = currentWord
        completer.currentTextChanged(completer.currentText)
    }

    /**
    Show suggestion box with filtered suggestions
    */
    function completeText() {
        updateCompleterModel()
        completer.show()
    }

    /**
    Expand expression into current expresion
    @param expression Key of builtin expression or dynamic expression
    */
    function expandExpression(expansion) {
        var textDocument = component.textComponent

        if(textDocument.selectedText == "") {
            var borders = exa.currentWordBorders()
            textDocument.remove(borders["start"], borders["end"])
        }

        else
            textDocument.remove(textDocument.selectionStart, textDocument.selectionEnd)
        textDocument.insert(textDocument.selectionStart, expansion)
    }

    function highlightLine(line) {
        lineHighlighter.y = (line - 1) * lineHighlighter.height - textEdit.flickableItem.contentY
        lineHighlighter.show()
    }

    function scrollToLine(line) {
        var contentHeight = textEdit.contentHeight
        var visibleAreaHeight = textEdit.height
        var lineHeight = contentHeight / textEdit.lineCount
        var visibleLinesCount = Math.floor(visibleAreaHeight / lineHeight)
        var firstVisibleLine = Math.ceil(textEdit.flickableItem.contentY / lineHeight)

        if(line < firstVisibleLine)
            textEdit.flickableItem.contentY = (line - 2) * lineHeight
        else if(line > firstVisibleLine + visibleLinesCount)
            textEdit.flickableItem.contentY = (line - visibleLinesCount) * lineHeight
    }

    function setSearchPattern(pattern) {
        esh.setSearchPattern(pattern)
    }

    function removesDiffMarks() {
        diffCodeAnalyzer.code = textEdit.text
        diffCodeAnalyzer.saveTempCode(textEdit.text)
        component.diffLines = []
        component.diffLinesChanged()
    }
}

