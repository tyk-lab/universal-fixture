import os
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QFileDialog,
    QLabel,
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from core.model.burn import Burn


class MainWindow(QMainWindow):
    app_directory = os.path.dirname(os.path.abspath(__file__))

    def __init__(self):
        super().__init__()

        self.setWindowTitle("生产测试")
        self.setGeometry(100, 100, 800, 600)

        # 创建菜单栏
        menu_bar = self.menuBar()
        mode_menu = menu_bar.addMenu("模式")

        # 创建菜单项
        self.action_fixture = QAction("治具测试", self, checkable=True)
        self.action_comm = QAction("通信测试", self, checkable=True)
        self.action_sigle = QAction("单独测试", self, checkable=True)

        # 将菜单项添加到模式菜单
        mode_menu.addAction(self.action_fixture)
        mode_menu.addAction(self.action_comm)
        mode_menu.addAction(self.action_sigle)

        # 连接信号到槽函数
        self.action_fixture.triggered.connect(self.update_mode)
        self.action_fixture.setChecked(True)
        self.action_comm.triggered.connect(self.update_mode)
        self.action_sigle.triggered.connect(self.update_mode)

        # 创建主部件和布局
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)

        # 第一行：选择文件按钮和不可编辑的文本框
        file_layout = QHBoxLayout()
        self.open_button = QPushButton("选择文件")
        self.open_button.clicked.connect(self.open_file)
        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)
        file_layout.addWidget(self.open_button)
        file_layout.addWidget(self.file_edit)

        # 第二行：烧录按钮和测试按钮
        action_layout = QHBoxLayout()
        self.burn_button = QPushButton("烧录")
        self.test_button = QPushButton("测试")
        self.burn_button.clicked.connect(self.upload_firmware)
        action_layout.addWidget(self.burn_button)
        action_layout.addWidget(self.test_button)

        # 第三行及以下：消息框
        self.message_box = QTextEdit()
        self.message_box.setReadOnly(True)

        # 将布局添加到主布局中
        main_layout.addLayout(file_layout)
        main_layout.addLayout(action_layout)
        main_layout.addWidget(self.message_box)

        # 设置主部件
        self.setCentralWidget(main_widget)

    def open_file(self):
        default_directory = "firmware"  # 替换为你想要的默认目录路径

        # todo, 可能要区分后缀根据配置
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "打开文件",
            default_directory,
            "烧录固件 (*.bin *.uf2)",
        )
        if file_name:
            self.file_edit.setText(file_name)
            self.message_box.append(f"已选择文件: {file_name}")

    def upload_firmware(self):
        burn = Burn("rp2040", self.file_edit.text())
        burn.flash(self)

    def update_mode(self):
        # 确保只有一个菜单项被选中
        sender = self.sender()
        if sender == self.action_fixture:
            self.action_comm.setChecked(False)
            self.action_sigle.setChecked(False)

        elif sender == self.action_comm:
            self.action_fixture.setChecked(False)
            self.action_sigle.setChecked(False)
        elif sender == self.action_sigle:
            self.action_fixture.setChecked(False)
            self.action_comm.setChecked(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
