"""
@File    :   loading.py
@Time    :   2025/04/03
@Desc    :   Loading animation
"""

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QFrame,
)

from PyQt6.QtGui import QMovie
from PyQt6.QtCore import Qt

from core.utils.common import GlobalComm


class LoadingPanel:
    def __init__(self, parent=None) -> None:
        self.parent = parent

    def init_loading_QFrame(self):
        # Create a full screen overlay
        self.overlay = QFrame(self.parent)
        self.overlay.setStyleSheet("background-color: rgba(255, 255, 255, 0.5);")
        self.overlay.setGeometry(self.parent.rect())  # Set overlay size
        self.overlay.setVisible(False)

        self.loading_label = QLabel(self.parent)
        self.loading_label.setVisible(False)  # Initially hidden
        self.loading_movie = QMovie(
            GlobalComm.setting_json["loading_gif"]
        )  # Update with the correct path
        self.loading_label.setMovie(self.loading_movie)

        # Add loading animation to overlay
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center display
        self.overlay_layout = QVBoxLayout(self.overlay)
        self.overlay_layout.addWidget(self.loading_label)

    def run_git(self):
        self.loading_label.setVisible(True)
        self.overlay.setVisible(True)
        self.loading_movie.start()

    def stop_gif(self):
        self.loading_movie.stop()
        self.loading_label.setVisible(False)
        self.overlay.setVisible(False)
