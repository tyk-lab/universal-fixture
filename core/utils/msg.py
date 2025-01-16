from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMainWindow,
    QHBoxLayout,
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QStyle


class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("消息")  # 清空默认标题
        self.setModal(True)

        # 设置主布局
        self.main_layout = QVBoxLayout(self)

        # 创建一个水平布局来放置图标和文本
        self.h_layout = QHBoxLayout()

        self.icon_label = QLabel(self)
        self.text_label = QLabel(self)

        # 调整对话框大小
        self.setFixedSize(300, 150)

        # 将图标和文本添加到水平布局中
        self.h_layout.addWidget(self.icon_label)
        self.h_layout.addWidget(self.text_label)

        # 将水平布局添加到主布局中
        self.main_layout.addLayout(self.h_layout)

        # 添加一个按钮来关闭对话框
        button = QPushButton("确定", self)
        button.clicked.connect(self.accept)  # 关闭对话框
        self.main_layout.addWidget(button)

    def show_show_warning(self, info):
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        self.icon_label.setPixmap(icon.pixmap(32, 32))
        self.text_label.setText(info)
        self.text_label.setStyleSheet("color: red;")
        self.exec()

    def show_burn_result(self, result):
        # 根据结果设置图标和文本
        if result:
            icon = self.style().standardIcon(
                QStyle.StandardPixmap.SP_MessageBoxInformation
            )
            self.icon_label.setPixmap(icon.pixmap(32, 32))
            self.text_label.setText("烧录成功")
            self.text_label.setStyleSheet("color: green;")
        else:
            icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
            self.icon_label.setPixmap(icon.pixmap(32, 32))
            self.text_label.setText("烧录失败")
            self.text_label.setStyleSheet("color: red;")
        self.exec()
