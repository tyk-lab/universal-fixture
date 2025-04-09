"""
@File    :   Flash_thread.py
@Time    :   2025/04/09
@Desc    :   Burning Device Threads
"""

from PyQt6.QtCore import QThread, pyqtSignal, Qt


class FlashThread(QThread):
    flash_complete = pyqtSignal(str)
    error_occurred = pyqtSignal(str, str)

    def __init__(self, usb_flash, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usb_flash = usb_flash

    def bind_event(self, complete_event, error_event):
        self.flash_complete.connect(complete_event)
        self.error_occurred.connect(error_event)

    def stop(self):
        self.wait()

    # flash device thread
    def run(self):
        try:
            result = self.usb_flash.flash_device()
            self.flash_complete.emit(result)  # Transmit completion signal
        except Exception as e:
            self.error_occurred.emit(result, str(e))  # Send error signal
