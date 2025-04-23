"""
@File    :   usb_flash.py
@Time    :   2025/04/03
@Desc    :   Implementing an asynchronous usb burn-in process
"""

from core.utils.opt_log import GlobalLogger
from core.ui.loading import LoadingPanel
from core.utils.Flash_thread import FlashThread
from core.utils.common import GlobalComm
from core.model.flash import Flash


class UsbFlash:
    def __init__(self, message_box, msg_dialog, parent=None):
        super().__init__()
        self.message_box = message_box
        self.msg_dialog = msg_dialog
        self.loading_git = LoadingPanel(parent)

    def check_flash_conditions(self):
        # Check the firmware type
        if not self.flash.check_firmware_suffix():
            err_tip = GlobalComm.get_langdic_val(
                "error_tip", "err_not_support_firmware"
            )
            GlobalLogger.log(err_tip)
            self.msg_dialog.show_warning(err_tip)
            return False

        # Check if you are in boot mode
        if not self.flash.check_lsusb_for_dev_boot():
            err_tip = GlobalComm.get_langdic_val("error_tip", "err_not_in_boot")
            GlobalLogger.log(err_tip)
            self.msg_dialog.show_warning(err_tip)
            return False
        return True

    # Burn Completion Event
    def on_flash_complete(self, result):

        GlobalLogger.log("flash ok")

        self.loading_git.stop_gif()
        isOk = self.flash.check_flash_finish(result)
        self.message_box.append(result)
        self.msg_dialog.show_flash_result(isOk)

    # Burning Error Event
    def on_flash_err(self, result, err):
        GlobalLogger.log("flash error")
        self.loading_git.stop_gif()
        self.message_box.append(err)
        self.message_box.append("\r\n############################################\r\n")
        self.message_box.append(result)

    def exec(self, mcu_type, burn_method, file_path):
        """Perform usb burning

        Args:
            mcu_type (_type_): Types of mcu
            file_path (_type_): Firmware Path
        """
        self.flash = Flash(mcu_type, burn_method, file_path)
        self.loading_git.init_loading_QFrame()

        # Calling threads to perform burn-in
        if self.check_flash_conditions():
            self.loading_git.run_git()
            self.analysis_thread = FlashThread(self.flash)
            self.analysis_thread.bind_event(self.on_flash_complete, self.on_flash_err)
            self.analysis_thread.start()
