import os
import shutil

PRINTER_CFG_PATH = "~/printer_data/config/printer.cfg"
PRINTER_CFG_DIR = "~/printer_data/config/"


class PrinterConfig:
    def __init__(self):
        self.is_fixture_test = False

    def set_cfg_mode(self, is_fixtrue):
        self.is_fixture_test = is_fixtrue

    def get_serial_paths(self, directory="/dev/serial/by-path"):
        # 获取目录下的所有文件路径
        try:
            serial_paths = [os.path.join(directory, f) for f in os.listdir(directory)]
        except FileNotFoundError:
            return False
        return serial_paths

    def generate_config(self, serial_paths, cfg_path=None):
        # 生成配置文本
        config_lines = ["[include fluidd.cfg]\r\n"]

        if self.is_fixture_test:
            cfg_name = os.path.basename(cfg_path)
            config_lines.append("[include " + cfg_name + "]")

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

    def cp_cfg_printer_dir(self, cfg_path):
        destination_directory = os.path.expanduser(PRINTER_CFG_DIR)
        shutil.copy(cfg_path, destination_directory)
