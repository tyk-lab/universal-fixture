from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar,QTextEdit
from PyQt6.QtCore import Qt

class UpdaterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("软件更新")
        self.setFixedSize(400, 300)

        self.layout = QVBoxLayout()

        self.status_label = QLabel("检查更新中...")
        self.layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.progress_bar)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.layout.addWidget(self.log_text)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        self.layout.addWidget(self.cancel_button)

        self.setLayout(self.layout)

    def update_status(self, message):
        self.status_label.setText(message)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def append_log(self, text):
        self.log_text.append(text)