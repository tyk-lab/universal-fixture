import os
import re

PRINTER_CFG_PATH = "~/printer_data/config/printer.cfg"


class PrinterConfig:
    def get_serial_paths(self, directory="/dev/serial/by-path"):
        # 获取目录下的所有文件路径
        try:
            serial_paths = [os.path.join(directory, f) for f in os.listdir(directory)]
        except FileNotFoundError:
            return False
        return serial_paths

    def generate_config(self, serial_paths):
        # 生成配置文本
        config_lines = ["[include fluidd.cfg]\r\n"]

        for i, path in enumerate(serial_paths):
            if i == 0:
                config_lines.append("[mcu]")
            else:
                config_lines.append(f"[mcu a{i}]")
            config_lines.append(f"serial: {path}\r\n")

        config_lines.extend(
            [
                "[printer]",
                "kinematics: none",
                "max_velocity: 1000",
                "max_accel: 1000\r\n",
            ]
        )

        return "\n".join(config_lines)

    def write_config_to_file(self, config_text):
        # 展开用户目录路径
        expanded_path = os.path.expanduser(PRINTER_CFG_PATH)
        with open(expanded_path, "w") as file:
            file.write(config_text)
