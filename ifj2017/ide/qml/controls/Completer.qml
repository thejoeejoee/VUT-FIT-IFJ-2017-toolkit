import QtQuick 2.7
import QtQuick.Controls 2.0
import StyleSettings 1.0

/**
  Component which offer suggestion to text inputs
  */
DropDown {
    id: component

    /// Background color of completer
    property color color
    /// List of suggestions
    property var constantModel
    /// Reference to targeted text input
    property var target
    /// Holds current word, so only matching words could be suggested
    property string currentText
    /// Background color of suggestion item when hovered
    property color hoverColor
    /// Text color of suggestions
    property color textColor

    scrollbarWidth: Core.scaledSize(3)
    model: constantModel

    onModelChanged: {
        if(!model.length)
            component.hide()
        component.resize()
    }

    onConstantModelChanged: updateModel()
    onCurrentTextChanged: updateModel()

    dropDownMenuBackground: Rectangle {
        color: component.color
        anchors.fill: parent
    }

    menuItem: Item {
        Rectangle {     // hover overlay
            opacity: 0.8
            color: (hovered) ?component.hoverColor :"transparent"

            anchors.fill: parent
        }

        Rectangle {
            id: symbol

            width: height
            height: component.itemHeight / 2.
            // TODO  real color
            color: StyleSettings.completer.typeColors[itemData["type"]]

            anchors.left: parent.left
            anchors.leftMargin: width
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            color: component.textColor
            text: itemData["identifier"]
            font: dummyText.font
            anchors.left: symbol.right
            anchors.leftMargin: symbol.anchors.leftMargin
            anchors.verticalCenter: parent.verticalCenter
        }
    }

    onTargetChanged: {
        component.target.Keys.pressed.connect(component.handleOtherKeys)
        component.target.Keys.upPressed.connect(component.moveUpWrapper)
        component.target.Keys.downPressed.connect(component.moveDownWrapper)
        component.target.Keys.returnPressed.connect(component.handleEnterKey)
        component.target.Keys.enterPressed.connect(component.handleEnterKey)
    }

    Text {
        id: dummyText
        visible: false
        font.pixelSize: itemHeight * 0.8
    }

    FontMetrics {
        id: fm
        font: dummyText.font
    }

    /**
      Update completer model according to constantModel
      */
    function updateModel()
    {
        var newModel = []

        var filter_pattern = new RegExp("^" + currentText, 'i')
        for(var key in component.constantModel) {
            var value = component.constantModel[key]

            if(value["identifier"].search(filter_pattern) !== -1)
                newModel.push(value)
        }

        component.model = newModel
    }

    function handleEnterKey(event) {
        if(!component.visible || component.model.length == 0)
            event.accepted = false;
        else
            component.chooseCurrent()
    }

    function moveUpWrapper(event) {
        if(!component.visible || component.model.length == 0)
            event.accepted = false;
        else
            component.moveUp()
    }

    function moveDownWrapper(event) {
        if(!component.visible || component.model.length == 0)
            event.accepted = false;
        else
            component.moveDown()
    }

    /**
      Manage completer actions based on key pressed. Cannot steal key event from text input, so connect it to target event
      @param event Passed key event
      */
    function handleOtherKeys(event) {
        var desiredKey = (ossystem != "Darwin") ?Qt.Key_Space :Qt.Key_J

        if(event.key == desiredKey && (event.modifiers & Qt.ControlModifier)) {
            component.show()
            event.accepted = true
        }

        if(component.visible && component.model.length && event.key == Qt.Key_Escape) {
            component.hide()
            event.accepted = true
        }
    }

    function resize() {
        var maxTextWidth = 0

        for(var key in component.model) {
            var textWidth = fm.advanceWidth(component.model[key]["identifier"])

            if(textWidth > maxTextWidth)
                maxTextWidth = textWidth
        }

        component.width = maxTextWidth + (component.itemHeight) * 2
    }
}
