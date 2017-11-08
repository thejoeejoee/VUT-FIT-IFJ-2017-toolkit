import QtQuick 2.0

/**
  Base component for all mouse interactive components
  */
Item {
    id: component

    /**
      Emits when clicked on component
      @param mouse Contains event data
      */
    signal clicked(var mouse)
    /**
      Emits when mouse entered area of component
      */
    signal entered()
    /**
      Emits when mouse leaved area of component
      */
    signal exited()
    /**
      Emits after mouse is pressed
      @param mouse Contains event data
      */
    signal pressed(var mouse)
    /**
      Emits after mouse is released
      @param mouse Contains event data
      */
    signal released(var mouse)

    /// If set to true hover is enabled else disable hover
    property alias hoverEnabled: mouseArea.hoverEnabled
    /// Holds whether component is hovered
    readonly property alias hovered: mouseArea.containsMouse
    /// Sets to manual signal emitting
    property bool manual: false
    /// Expose MouseArea
    readonly property alias mouseArea: mouseArea

    MouseArea {
        id: mouseArea

        anchors.fill: parent
        acceptedButtons: Qt.LeftButton | Qt.RightButton

        onPressed: {
            if(!component.manual)
                component.pressed(mouse)
        }

        onReleased: {
            if(!component.manual)
                component.released(mouse)
        }

        onClicked: {
            if(!component.manual)
                component.clicked(mouse)
        }

        onContainsMouseChanged: {
            if(component.manual)
                return
            if(mouseArea.containsMouse)
                component.entered()
            else
                component.exited()
        }
    }
}
