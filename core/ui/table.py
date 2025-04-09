"""
@File    :   table.py
@Time    :   2025/04/03
@Desc    :   Extend QTableView to double click on a cell to pop up a dialogue box
"""

from PyQt6.QtWidgets import QTableView

import core.utils.common


class CustomTableView(QTableView):
    def mouseDoubleClickEvent(self, event):
        # Getting the index of a double-click
        index = self.indexAt(event.pos())
        if index.isValid():
            # Getting the contents of a double-clicked cell
            cell_content = index.data()
            dialog = core.utils.common.CustomDialog()
            dialog.show_info(cell_content)

        else:
            super().mouseDoubleClickEvent(event)
