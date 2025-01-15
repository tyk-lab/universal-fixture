import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLineEdit, QTextEdit, QFileDialog, QLabel
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt6 主界面示例")

        # 创建菜单栏
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("模式")
        
        # 创建菜单项
        open_action = QAction("打开文件", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

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
        file_name, _ = QFileDialog.getOpenFileName(self, "打开文件", "", "所有文件 (*)")
        if file_name:
            self.file_edit.setText(file_name)
            self.message_box.append(f"已选择文件: {file_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())