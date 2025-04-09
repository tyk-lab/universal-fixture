"""
@File    :   Test_thread.py
@Time    :   2025/04/09
@Desc    :   Test thread related
"""

from PyQt6.QtCore import QThread, pyqtSignal, QTimer


class TestThread(QThread):
    error_occurred = pyqtSignal(str, str)
    test_complete = pyqtSignal()

    def __init__(self, action_fun, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action_fun = action_fun
        self.count = 0

    def bind_event(self, complete_event, error_event):
        self.test_complete.connect(complete_event)
        self.error_occurred.connect(error_event)

    def stop(self):
        self.wait()

    # flash device thread
    def run(self):
        try:
            self.action_fun()
            self.test_complete.emit()
        except Exception as e:
            print("Exception")
            self.error_occurred.emit("err: ", str(e))  # Send error signal
