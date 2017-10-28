# coding=utf-8
from typing import Dict

from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt


class TreeViewModel(QStandardItemModel):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.add_item("prvni", "sub", 1, "int")
        self.add_item("sub", "foo2", 1, "int")
        self.add_item("prvni", "foo", 1, "float")
        self.add_item("prvni", "foo", 1, "int")
        self.add_item("prvni2", "foo", 2, "int")
        self.add_item("prvni3", "foo", 3, "int")

    def roleNames(self) -> Dict:
        return {
            Qt.DisplayRole: "name_col".encode(),
            Qt.UserRole: "value_col".encode(),
            Qt.UserRole + 1: "type_col".encode()
        }

    def add_item(self, branch_name, name, value, value_type) -> None:
        new_item = QStandardItem(name)
        new_item.setData(value, Qt.UserRole)
        new_item.setData(value_type, Qt.UserRole + 1)

        branch = self._get_branch(branch_name)
        branch.appendRow(new_item)

    def _get_branch(self, branch_name: str) -> QStandardItem:
        branches = self.findItems(branch_name, Qt.MatchExactly | Qt.MatchRecursive)

        if len(branches):
            return branches[0]
        else:
            new_branch = QStandardItem(branch_name)
            new_branch.setData("", Qt.UserRole)
            new_branch.setData("", Qt.UserRole + 1)
            self.appendRow(new_branch)

            return new_branch
