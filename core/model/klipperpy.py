from core.model.moonrakerpy import MoonrakerPrinter
from core.utils.common import GlobalComm


class KlipperService:
    def __init__(self):
        self.printer = MoonrakerPrinter(GlobalComm.setting_json["klipper_web"])

    def reset_printer(self):
        self.printer.send_gcode("FIRMWARE_RESTART")

    def reset_klipper(self):
        self.printer.send_gcode("RESTART")

    def get_connect_info(self):
        web_state = self.printer.query_status("webhooks")
        return web_state

    def is_connect(self):
        try:
            web_state = self.get_connect_info()
            return web_state["state"] == "ready"
        except KeyError as e:
            return False
        except Exception as e:
            return False

    def get_sensor_info(self, sensor_type, key_str):
        list = []
        sensors = sensor_type
        sensors = self.printer.list_sensors(sensors)
        dict = self.printer.query_sensors(sensors)
        print(dict)
        for name, info in dict.items():
            val = info.get(key_str)
            list.append((name, val))
        return list
