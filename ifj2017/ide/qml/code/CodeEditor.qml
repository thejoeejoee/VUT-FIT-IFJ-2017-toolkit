import QtQuick 2.7
import QtQuick.Controls 1.4

import StyleSettings 1.0
import ExpSyntaxHighlighter 1.0
import ExpAnalyzer 1.0
import CodeAnalyzer 1.0

import "../controls"

Item {
    id: component

    property alias completer: completer
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

                x: lineNumbers.width + 7
                width: flick.width
                height: flick.height

                onCursorRectangleChanged: {
                    flick.moveContentAccordingToCursor(cursorRectangle)
                }

                onTextChanged: completeText()
                onSelectedTextChanged: {
                    if(textComponent.selectedText.length) {
                        completer.model = completer.constantModel
                        completer.currentText = ""
                    }
                    else
                        completeText()
                }
                onCursorPositionChanged: completeText()
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
                        text: modelData + 1
                        color: component.lineNumberColor
                        anchors.centerIn: parent
                    }
                }
            }
        }
    }

    FontMetrics {
        id: fmCodeInput
        font: textEdit.font
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

        x: component.calcTextInfoPos(width)
        y: textEdit.cursorRectangle.y + textEdit.cursorRectangle.height + textEdit.y
        width: 150
        itemHeight: 20

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

    /**
    Show suggestion box with filtered suggestions
    */
    function completeText() {
        var textDocument = component.textComponent
        var lastChar = textDocument.text.slice(-1)
        var currentWord = exa.currentWord()

        if(textDocument.cursorPosition)
            lastChar = textDocument.text[textDocument.cursorPosition - 1]

        if(CodeAnalyzer.expressionSplitters.indexOf(lastChar) != -1)
            completer.show()

        completer.currentText = currentWord
        completer.currentTextChanged(completer.currentText)
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
}

