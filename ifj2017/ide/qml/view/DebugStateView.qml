import QtQuick 2.0
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.0
import TreeViewModel 1.0

import "../containers"

SlideWidget {
    id: component

    signal lineClicked(var line)
    property alias model: debugStateModel
    property alias callStackModel: callStackView.model
    property alias view: treeView

    Item {
        width: component.width
        height: parent.height

        TreeViewModel {
            id: debugStateModel
        }

        SplitView {
            orientation: Qt.Vertical
            anchors.fill: parent

            handleDelegate: Rectangle {
                height: Core.scaledSize(2)
                color: "#e5e5e5"
            }

            TreeView {
                id: treeView

                property int scrollbarSize: Core.scaledSize(7)

                model: debugStateModel
                frameVisible: false
                backgroundVisible: false
                alternatingRowColors: false
                Layout.fillHeight: true
                Layout.minimumHeight: Core.scaledSize(200)

                style: TreeViewStyle {
                    backgroundColor: "white"
                    handle: Rectangle {
                        color: "#424246"
                        implicitWidth: treeView.scrollbarSize
                        implicitHeight: treeView.scrollbarSize
                    }
                    scrollBarBackground: Item {
                        implicitWidth: treeView.scrollbarSize
                        implicitHeight: treeView.scrollbarSize
                    }

                    decrementControl: Rectangle {
                        implicitWidth: treeView.scrollbarSize
                        implicitHeight: treeView.scrollbarSize
                        color: "lightGray"
                    }

                    incrementControl: Rectangle {
                        implicitWidth: treeView.scrollbarSize
                        implicitHeight: treeView.scrollbarSize
                        color: "lightGray"
                    }

                    itemDelegate: Rectangle {
                        color: "white"
                        implicitHeight: Core.scaledSize(20)
                        height: implicitHeight

                        Text {
                            font.pixelSize: parent.height * 0.8
                            anchors.verticalCenter: parent.verticalCenter
                            text: styleData.value === undefined ? "" : styleData.value
                        }
                    }

                    rowDelegate: Rectangle {
                        implicitHeight: Core.scaledSize(20)
                        height: implicitHeight
                    }

                    headerDelegate: Rectangle {
                        color: "#e5e5e5"
                        implicitHeight: Core.scaledSize(20)
                        height: implicitHeight

                        Rectangle {
                            opacity: (styleData.containsMouse) ?0.2 :0
                            color: "black"
                            anchors.fill: parent
                        }

                        Rectangle {
                            color: "white"
                            height: parent.height * 0.7
                            width: 1

                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: styleData.value === undefined ? "" : styleData.value
                            font.pixelSize: parent.height * 0.75

                            anchors.left: parent.left
                            anchors.leftMargin: Core.scaledSize(7)
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    branchDelegate: Rectangle {
                        width: height
                        height: Core.scaledSize(10)
                        color: "white"

                        Image {
                            source: rootDir + "assets/images/arrowRight.svg"
                            fillMode: Image.PreserveAspectFit

                            anchors.fill: parent
                            sourceSize: Qt.size(width, height)

                            transform: Rotation {
                                origin.x: width / 2
                                origin.y: height / 2
                                axis { x: 0; y: 0; z: 1 }
                                angle: (styleData.isExpanded) ?90 :0
                            }
                        }
                    }
                }

                TableViewColumn {
                    role: "name_col"
                    title: "Name"
                    width: Core.scaledSize(250)
                }
                TableViewColumn {
                    role: "value_col"
                    title: "Value"
                }
                TableViewColumn {
                    role: "type_col"
                    title: "Type"
                }
            }

            SimpleListView {
                id: callStackView

                title: qsTr("Call stack")
                titleColor: "#2f2f2f"
                titleTextColor: "white"

                height: 200
                Layout.minimumHeight: Core.scaledSize(100)

                onClicked: component.lineClicked(itemData)
            }
        }
    }
}
