from core.model.moonrakerpy import MoonrakerPrinter
from core.utils.common import GlobalComm


class KlipperService:
    def __init__(self):
        self.printer = MoonrakerPrinter(GlobalComm.setting_json["klipper_web"])

    def reset_printer(self):
        try:
            web_state = self.get_connect_info()
            if web_state["state"] == "error":
                self.printer.send_gcode("FIRMWARE_RESTART")
            else:
                self.printer.send_gcode("RESTART")
        except KeyError as e:
            return False
        except Exception as e:
            return False

    def reset_klipper(self):
        self.printer.send_gcode("RESTART")

    def power_run(self):
        self.printer.send_gcode("TEST_POWER")

    def accelerometer_run(self):
        self.printer.send_gcode("ACCELEROMETER_QUERY")
        result_list = self.printer.get_gcode(1)
        result = "".join(result_list).split(": ")[1]
        return result

    def run_test_gcode(self, cmd):
        self.printer.send_gcode(cmd)

    def get_connect_info(self):
        web_state = self.printer.query_status("webhooks")
        return web_state

    # 检查过程中，如果是报错，自动重置
    # reset如果是True，则判断中发生错误会固件重置
    def is_connect(self, reset=True):
        try:
            web_state = self.get_connect_info()
            state = web_state["state"]
            if reset and state == "error":
                self.printer.send_gcode("FIRMWARE_RESTART")
            return state == "ready"
        except KeyError as e:
            return False
        except Exception as e:
            return False

    # return: sensors dicts
    def get_info(self, key):
        sensors = self.printer.list_sensors(key)
        dicts = self.printer.query_sensors(sensors, key)
        return dicts

    # key: "gcode_button "
    def list_names(self, key):
        sensors = self.printer.list_sensors(key)
        dicts = self.printer.query_sensors(sensors, key)
        return list(dicts.keys())

    def check_config_field(self, config_path, field):
        if not isinstance(config_path, str) or not config_path:
            return False

        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                # 去除行首尾空白后判断是否等于指定字段
                if field in line:
                    return True
        return False
