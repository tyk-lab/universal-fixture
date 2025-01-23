from PyQt6.QtCore import QThread, pyqtSignal, Qt


class TestThread(QThread):
    test_complete = pyqtSignal(str)
    error_occurred = pyqtSignal(str, str)

    def __init__(self, action_list, test_mode, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action_list = action_list
        self.test_mode = test_mode

    def bind_event(self, complete_event, error_event):
        self.test_complete.connect(complete_event)
        self.error_occurred.connect(error_event)

    def stop(self):
        self.wait()

    # flash device thread
    def run(self):
        try:
            self.action_list[self.test_mode]()
            self.test_complete.emit("end")  # Transmit completion signal
        except Exception as e:
            self.error_occurred.emit("err", str(e))  # Send error signal
