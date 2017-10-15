import QtQuick 2.7
import QtQuick.Controls 1.4

import StyleSettings 1.0
import ExpSyntaxHighlighter 1.0
import ExpAnalyzer 1.0
import CodeAnalyzer 1.0

import "code"
import "controls"

ApplicationWindow {
    visible: true
    width: 640
    height: 480
    title: qsTr("Advánc Ifj Creator")

    Rectangle {
        id: root
        color: "white"
        anchors.fill: parent
    }

    ExpAnalyzer {
        id: exa
        target: codeEditor.textComponent
    }

    ExpSyntaxHighlighter {
        id: esh
        target: codeEditor.textComponent

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

        x: calcTextInfoPos(width)
        y: codeEditor.textComponent.cursorRectangle.y + codeEditor.textComponent.cursorRectangle.height + codeEditor.textComponent.y
        width: parent.width * 0.18
        itemHeight: width / 5

        opacity: 0.8
        color: StyleSettings.completer.color
        hoverColor: StyleSettings.completer.hoverColor
        textColor: StyleSettings.completer.textColor
        scrollBarColor: StyleSettings.completer.scrollBarColor

        constantModel: CodeAnalyzer.completerModel

        target: codeEditor.textComponent

        Component.onCompleted: show()
        onItemChoosed: expandExpression(currentItem["identifier"])

        function calcTextInfoPos(infoWidth) {
            var textDocument = codeEditor.textComponent
            if(textDocument.cursorRectangle.x + infoWidth + fmCodeInput.advanceWidth(" ") < textDocument.width)
                return textDocument.cursorRectangle.x + textDocument.x
            else
                return textDocument.x + textDocument.width - infoWidth - textDocument.textMargin
        }
    }

    CodeEditor {
        id: codeEditor

        lineNumbersPanelColor: "#f2f2f2"
        anchors.fill: parent

        FontMetrics {
            id: fmCodeInput
            font: codeEditor.textComponent.font
        }

        textComponent.onTextChanged: completeText()
        textComponent.onSelectedTextChanged: {
            if(textComponent.selectedText.length) {
                completer.model = completer.constantModel
                completer.currentText = ""
            }
            else
                completeText()
        }
        textComponent.onCursorPositionChanged: completeText()
    }

    /**
    Show suggestion box with filtered suggestions
    */
    function completeText() {
        var textDocument = codeEditor.textComponent
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
        var textDocument = codeEditor.textComponent

        if(textDocument.selectedText == "") {
            var borders = exa.currentWordBorders()
            textDocument.remove(borders["start"], borders["end"])
        }

        else
            textDocument.remove(textDocument.selectionStart, textDocument.selectionEnd)
        textDocument.insert(textDocument.selectionStart, expansion)
    }
}
