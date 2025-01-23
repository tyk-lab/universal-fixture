import sys
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, QObject


# 自定义信号类
class Controller(QObject):
    close_signal = pyqtSignal()


# 自定义弹窗类
class ControlledDialog(QDialog):
    def __init__(self, controller):
        super().__init__()

        self.setWindowTitle("受控弹窗")
        self.layout = QVBoxLayout()
        self.label = QLabel("等待关闭信号...")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        # 连接信号到槽
        controller.close_signal.connect(self.close_window)

    def close_window(self):
        self.label.setText("收到关闭信号，窗口即将关闭...")
        self.accept()  # 关闭窗口


def main():
    app = QApplication(sys.argv)

    # 创建信号控制器
    controller = Controller()

    # 创建并显示弹窗
    dialog = ControlledDialog(controller)
    dialog.show()

    # 模拟一段时间后发射关闭信号
    def emit_signal():
        controller.close_signal.emit()

    # 创建一个按钮来手动触发信号（用于演示）
    button = QPushButton("关闭弹窗")
    button.clicked.connect(emit_signal)
    button.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
