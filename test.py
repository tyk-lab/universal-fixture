import sys
from PyQt6.QtWidgets import QApplication, QFrame, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import Qt


class GifPlayer(QWidget):
    def __init__(self):
        super().__init__()

        # Create a full screen overlay
        self.overlay = QFrame(self)
        self.overlay.setStyleSheet("background-color: rgba(128, 128, 128, 0.5);")
        self.overlay.setGeometry(self.rect())  # Set overlay size
        self.overlay.setVisible(False)

        # 创建一个 QLabel 作为 GIF 显示的载体
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中对齐

        # 创建 QMovie 对象，加载 GIF 文件
        self.movie = QMovie("core/cfg/loading.gif")

        # 设置 QLabel 使用 QMovie
        self.label.setMovie(self.movie)

        # 设置布局
        self.overlay_layout = QVBoxLayout(self.overlay)
        self.overlay_layout.addWidget(self.label)
        self.setLayout(self.overlay_layout)

        # 设置窗口属性
        self.setWindowTitle("GIF 播放器")
        self.resize(400, 300)

        # 启动 GIF 动画
        self.movie.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = GifPlayer()
    player.show()
    sys.exit(app.exec())
