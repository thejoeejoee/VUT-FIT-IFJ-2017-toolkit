# coding=utf-8
from typing import Dict, Union, List

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

    def get_item(self, path: List[str], item_name: str):
        parents = [None]

        for i, name in enumerate(path + [item_name]):
            parent_model = self if i == 0 else parents[-1]
            items = self.findItems(name, Qt.MatchExactly | Qt.MatchRecursive)
            target_item = None

            if not items:   # create new item if it does not exist
                target_item = self._create_item(parent_model, name, {Qt.UserRole: "", Qt.UserRole+1: ""})
            else:
                for item in items: # check found items with corresponding parent
                    if item.parent() == parents[-1]:
                        target_item = item
                if target_item is None:
                    target_item = self._create_item(parent_model, name, {Qt.UserRole: "", Qt.UserRole + 1: ""})

            parents.append(target_item)
        return parents[-1]

    def clear_sub_tree(self, path: List[str], item_name: str) -> None:
        index = self.get_item(path, item_name).index()
        self.removeRows(0, self.rowCount(index), index)

    def remove_sub_tree(self, path: List[str], item_name: str) -> None:
        index = self.get_item(path, item_name).index()
        parent_index = index.parent()

        self.removeRows(index.row(), 1, parent_index)


    def roleNames(self) -> Dict:
        return {
            Qt.DisplayRole: "name_col".encode(),
            Qt.UserRole: "value_col".encode(),
            Qt.UserRole + 1: "type_col".encode()
        }

    def set_item_data(self, path, name, value, value_type) -> None:
        item = self.get_item(path, name)
        item.setData(value, Qt.UserRole)
        item.setData(value_type, Qt.UserRole + 1)
