"""
@File    :   msg.py
@Time    :   2025/04/03
@Desc    :   global message board
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QStyle

import core.utils.common


class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("消息")  # Clear the default title
        self.setModal(True)

        # Setting up the main layout
        self.main_layout = QVBoxLayout(self)

        # Create a horizontal layout for placing icons and text
        self.h_layout = QHBoxLayout()

        self.icon_label = QLabel(self)
        self.text_label = QLabel(self)

        # Resizing the dialogue box
        # self.setFixedSize(300, 150)

        # Adding icons and text to horizontal layouts
        self.h_layout.addWidget(self.icon_label)
        self.h_layout.addWidget(self.text_label)

        # Adding a horizontal layout to the main layout
        self.main_layout.addLayout(self.h_layout)

        # Add a button to close the dialogue box
        button = QPushButton("确定", self)
        button.clicked.connect(self.accept)  # Close dialogue box
        self.main_layout.addWidget(button)

    def show_info(self, info):
        self.text_label.setStyleSheet("color: black;")
        self.text_label.setText(info)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.exec()

    def show_warning(self, info):
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        self.icon_label.setPixmap(icon.pixmap(32, 32))
        self.text_label.setText(info)
        self.text_label.setStyleSheet("color: red;")
        self.exec()

    def show_flash_result(self, result):
        if result:
            icon = self.style().standardIcon(
                QStyle.StandardPixmap.SP_MessageBoxInformation
            )
            self.icon_label.setPixmap(icon.pixmap(32, 32))
            self.text_label.setText(
                core.utils.common.GlobalComm.get_langdic_val("view", "flash_ok")
            )
            self.text_label.setStyleSheet("color: green;")
        else:
            icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
            self.icon_label.setPixmap(icon.pixmap(32, 32))
            self.text_label.setText(
                core.utils.common.GlobalComm.get_langdic_val("view", "flash_err")
            )
            self.text_label.setStyleSheet("color: red;")
        self.exec()
