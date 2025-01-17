import subprocess

from core.utils.common import GlobalComm
import sh


class Flash:

    def __init__(self, mcu_type, file_full_name):
        self.usb_devs = GlobalComm.setting_json["support_dev"]
        self.file_path = file_full_name
        self.mcu_type = mcu_type

    def check_flash_finish(self, result):
        if "Rebooting device" in result:
            return True
        elif "Resetting USB to switch back to runtime mode" in result:
            return True
        return False

    # 解析时判断
    def check_firmware_suffix(self):
        # 定义允许的文件后缀
        allowed_suffixes = GlobalComm.setting_json["support_suffixes"]
        # 获取文件后缀
        file_suffix = self.file_path.split(".")[-1]

        # 检查文件后缀是否在允许的后缀列表中
        if f".{file_suffix}" in allowed_suffixes.get(self.mcu_type, []):
            return True
        return False

    def check_lsusb_for_dev_boot(self):
        # 执行 lsusb 命令并捕获输出
        result = subprocess.run(["lsusb"], capture_output=True, text=True, check=True)
        dev = self.usb_devs[self.mcu_type]

        for line in result.stdout.splitlines():
            if dev in line:
                self.parts = line.split()
                usb_id = self.parts[5]
                return usb_id
        return None

    def flash_device(self):
        return sh.bash("tool/usb_flash.sh", self.mcu_type, self.file_path)
