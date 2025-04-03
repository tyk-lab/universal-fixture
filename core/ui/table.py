"""
@File    :   table.py
@Time    :   2025/04/03
@Desc    :   Extend QTableView to double click on a cell to pop up a dialogue box
"""

from PyQt6.QtWidgets import QTableView

import core.utils.common


class CustomTableView(QTableView):
    def mouseDoubleClickEvent(self, event):
        # 获取双击的索引
        index = self.indexAt(event.pos())
        if index.isValid():
            # 获取双击单元格的内容
            cell_content = index.data()
            dialog = core.utils.common.CustomDialog()
            dialog.show_info(cell_content)

        else:
            super().mouseDoubleClickEvent(event)
