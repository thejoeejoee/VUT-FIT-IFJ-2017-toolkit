import QtQuick 2.0
import QtQuick.Controls 1.4
import TreeViewModel 1.0

import "../containers"

SlideWidget {
    id: component

    property alias model: debugStateModel

    TreeView {
        width: component.width
        height: parent.height
        model: debugStateModel
        alternatingRowColors: false

        TreeViewModel {
            id: debugStateModel
        }

        itemDelegate: Item {
           height: Core.scaledSize(22)

           Text {
               anchors.verticalCenter: parent.verticalCenter
               text: styleData.value === undefined ? "" : styleData.value
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
}
