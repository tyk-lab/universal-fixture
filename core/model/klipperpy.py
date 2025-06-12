"""
@File    :   klipperpy.py
@Time    :   2025/04/03
@Desc    :   Implement klipper related operations
"""

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

    def shucdown_klipper(self):
        self.printer.send_gcode("SHUTDOWN")
        self.printer.send_gcode("FIRMWARE_RESTART")

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

    # The checking process is automatically reset if it is an error report
    # reset if True, firmware reset if an error occurs during judgement
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
        from core.utils.exception.ex_test import TestKlipperNullException

        sensors = self.printer.list_sensors(key)
        dicts = self.printer.query_sensors(sensors, key)

        if len(dicts) == 0 or dicts == None:
            raise TestKlipperNullException()
        return dicts

    # key: "gcode_button "
    def list_names(self, key):
        from core.utils.exception.ex_test import TestKlipperNullException

        sensors = self.printer.list_sensors(key)
        dicts = self.printer.query_sensors(sensors, key)
        return list(dicts.keys())
