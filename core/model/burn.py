import subprocess

from core.utils.msg import CustomDialog


class Burn:

    def __init__(self, mcu_type, file_full_name):
        self.usb_devs = {"rp2040": "Raspberry Pi RP2", "": ""}
        self.file_path = file_full_name
        self.mcu_type = mcu_type

    def check_flash_finish(self, result):
        if "Rebooting device" in result:
            return True
        return False

    def check_lsusb_for_dev_boot(self):
        # 执行 lsusb 命令并捕获输出
        result = subprocess.run(["lsusb"], capture_output=True, text=True, check=True)
        dev = self.usb_devs[self.mcu_type]

        for line in result.stdout.splitlines():
            if dev in line:
                # 找到包含 'Raspberry Pi RP2' 的行后，提取 ID 号
                self.parts = line.split()
                # ID 通常在第四个位置（索引为 3）
                usb_id = self.parts[5]
                return usb_id
        return None

    def flash_device(self, usb_id):
        result = subprocess.run(
            [
                "python3",
                "flash_usb.py",
                "-t" + self.mcu_type,
                "-d" + usb_id,
                self.file_path,
                "--no-sudo",
            ],
            capture_output=True,
            text=True,
        )
        return self.check_flash_finish(result.stderr)

    def flash(self, parent=None):
        usb_id = self.check_lsusb_for_dev_boot()
        dialog = CustomDialog(parent)

        if usb_id != None:
            dialog.show_burn_result(self.flash_device(usb_id))
            return
        dialog.show_show_warning("错误：设备未进入烧录模式")
