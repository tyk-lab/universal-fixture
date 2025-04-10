"""
@File    :   Test_thread.py
@Time    :   2025/04/09
@Desc    :   Test thread related
"""

import traceback
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
import serial


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
        from core.utils.exception.ex_test import TestConnectException
        from core.utils.opt_log import GlobalLogger

        try:
            self.action_fun()
            self.test_complete.emit()
        except (
            serial.serialutil.SerialException
        ) as e:  # Passing on errors during testing
            err = str(e)
            GlobalLogger.debug_print("serial exceptions：", err)
            self.error_occurred.emit(" try closs window, reopen\r\nserial err:", str(e))
        except TestConnectException as e:
            GlobalLogger.debug_print("fixture_test Connect exceptions：", e.message)
            self.error_occurred.emit("fixture_test Connect err: ", e.message)
        except Exception as e:
            traceback_msg = traceback.format_exc()
            self.error_occurred.emit(
                "please check log\r\nfixture_test err: ", traceback_msg
            )
