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
        if not self.flash.check_firmware_suffix():
            self.msg_dialog.show_warning(
                GlobalComm.get_langdic_val("error_tip", "err_not_support_firmware")
            )
            return False

        if not self.flash.check_lsusb_for_dev_boot():
            self.msg_dialog.show_warning(
                GlobalComm.get_langdic_val("error_tip", "err_not_in_boot")
            )
            return False
        return True

    def on_flash_complete(self, result):
        self.loading_git.stop_gif()
        isOk = self.flash.check_flash_finish(result)
        self.message_box.append(result)
        self.msg_dialog.show_flash_result(isOk)

    def on_flash_err(self, result, err):
        self.loading_git.stop_gif()
        self.message_box.append(err)
        self.message_box.append("\r\n############################################\r\n")
        self.message_box.append(result)

    def exec(self, mcu_type, file_path):
        self.flash = Flash(mcu_type, file_path)
        self.loading_git.init_loading_QFrame()

        if self.check_flash_conditions():
            self.loading_git.run_git()

            self.analysis_thread = FlashThread(self.flash)
            self.analysis_thread.bind_event(self.on_flash_complete, self.on_flash_err)
            self.analysis_thread.start()
