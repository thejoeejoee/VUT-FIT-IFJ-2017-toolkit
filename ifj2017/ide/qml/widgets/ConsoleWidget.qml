import QtQuick 2.0
import IOWrapper 1.0

import "../controls"

Item {
    id: component

    signal runToNextBreakPointRequest()
    signal runToNextLineRequest()

    property alias ioWrapper: consoleIOWrapper
    property alias toolbarHeight: debugToolbar.height
    property alias debugToolbarEnabled: debugToolbar.debugButtonsEnabled
    readonly property alias reading: rawConsole.reading

    IOWrapper {
        id: consoleIOWrapper
        onReadRequest: component.read()
        onWriteRequest: component.write(text)
    }

    DebugToolbar {
        id: debugToolbar

        color: "#2f2f2f"
        debugButtonsEnabled: false

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top

        onRunToNextBreakpointRequest: component.runToNextBreakPointRequest()
        onRunTonextLineRequest: component.runToNextLineRequest()
        onClearConsole: component.clear()
    }

    Console {
        id: rawConsole

        anchors.top: debugToolbar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        onTextReaded: consoleIOWrapper.handleConsoleRead(text)
    }

    function clear() {
        rawConsole.clear()
    }

    function write(text, color) {
        rawConsole.write(text, color)
    }

    function read() {
        rawConsole.read()
    }

    function stopRead() {
        rawConsole.stopRead()
    }
}
