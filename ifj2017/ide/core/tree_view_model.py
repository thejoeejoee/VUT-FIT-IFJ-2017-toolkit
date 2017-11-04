# coding=utf-8
from typing import Dict

from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt


class TreeViewModel(QStandardItemModel):
    def __init__(self, parent = None):
        super().__init__(parent)

    def roleNames(self) -> Dict:
        return {
            Qt.DisplayRole: "name_col".encode(),
            Qt.UserRole: "value_col".encode(),
            Qt.UserRole + 1: "type_col".encode()
        }

    def add_item(self, branch_name, name, value, value_type) -> None:
        existing_item = self.findItems(name, Qt.MatchExactly | Qt.MatchRecursive)
        if existing_item:
            item = existing_item[0]
        else:
            item = QStandardItem(name)
        item.setData(value, Qt.UserRole)
        item.setData(value_type, Qt.UserRole + 1)

        if not existing_item:
            branch = self._get_branch(branch_name)
            branch.appendRow(item)

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
