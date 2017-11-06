# coding=utf-8
from typing import Dict, Union

from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt


class TreeViewModel(QStandardItemModel):
    def __init__(self, parent = None):
        super().__init__(parent)


    def _create_item(self, parent_model: Union[QStandardItem, QStandardItemModel], name: str, data: Dict) -> QStandardItem:
        item = QStandardItem(name)
        for user_role, row_data in data.items():
            item.setData(row_data, user_role)
        parent_model.appendRow(item)
        return item

    def _get_item(self, path, item_name):
        parents = [None]

        for i, name in path + [item_name]:
            parent_model = self if i is 0 else parents[-1]
            items = self.findItems(name, Qt.MatchExactly | Qt.MatchRecursive)
            target_item = None

            if not items:   # create new item if it does not exist
                target_item = self._create_item(parent_model, name, {Qt.UserRole: "", Qt.UserRole+1: ""})
            else:
                for item in items: # check found items with corresponding parent
                    if item.parent() == parents[-1]:
                        target_item = item
                    else:
                        target_item = self._create_item(parent_model, name, {Qt.UserRole: "", Qt.UserRole + 1: ""})

            parents.append(target_item)
        return parents[-1]


    def roleNames(self) -> Dict:
        return {
            Qt.DisplayRole: "name_col".encode(),
            Qt.UserRole: "value_col".encode(),
            Qt.UserRole + 1: "type_col".encode()
        }

    def set_item_data(self, path, name, value, value_type) -> None:
        item = self._get_item(path, name)
        item.setData(value, Qt.UserRole)
        item.setData(value_type, Qt.UserRole + 1)
