"""
@File    :   flash.py
@Time    :   2025/04/03
@Desc    :   Enables burning of device firmware
"""

import subprocess

from core.utils.opt_log import GlobalLogger
from core.utils.common import GlobalComm
import sh


class Flash:

    def __init__(self, mcu_type, file_full_name):
        self.usb_devs = GlobalComm.setting_json["support_dev"]
        self.file_path = file_full_name
        self.mcu_type = mcu_type.split("f")[0]

    # Check the key fields to judge the burn-in results
    def check_flash_finish(self, result):
        if "Rebooting device" in result:
            return True
        elif "Resetting USB to switch back to runtime mode" in result:
            return True
        return False

    def check_firmware_suffix(self):
        # Define allowed file suffixes
        allowed_suffixes = GlobalComm.setting_json["support_suffixes"]
        # Get File Suffix
        file_suffix = self.file_path.split(".")[-1]
        if f".{file_suffix}" in allowed_suffixes.get(self.mcu_type, []):
            return True
        return False

    # Determine if you are in boot mode based on the result of the unique usb id of the lsusb
    def check_lsusb_for_dev_boot(self):
        result = subprocess.run(["lsusb"], capture_output=True, text=True, check=True)
        dev = self.usb_devs[self.mcu_type]

        GlobalLogger.log(result.stdout)

        for line in result.stdout.splitlines():
            if dev in line:
                self.parts = line.split()
                # The fifth column is the usb id column
                usb_id = self.parts[5]
                return usb_id
        return None

    def flash_device(self):
        return sh.bash("tool/usb_flash.sh", self.mcu_type, self.file_path)
