import QtQuick 2.0
import QtQuick.Controls 1.4
import TreeViewModel 1.0

import "../containers"

SlideWidget {
    id: component

    property alias model: debugStateModel
    property alias view: treeView

    Item {
        width: component.width
        height: parent.height

        TreeViewModel {
            id: debugStateModel

            Component.onCompleted: console.log(debugStateModel, "bar")
        }

        TreeView {
            id: treeView

            anchors.fill: parent
            model: debugStateModel
            alternatingRowColors: false

            itemDelegate: Item {
               height: Core.scaledSize(22)

               Text {
                   anchors.verticalCenter: parent.verticalCenter
                   text: styleData.value === undefined ? "" : styleData.value
               }
           }

            Component.onCompleted: console.log("view", treeView.model)

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
    }
}
