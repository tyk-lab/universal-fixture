from core.model.moonrakerpy import MoonrakerPrinter
from core.utils.common import GlobalComm


class DevInfo:
    def __init__(self, klipper, dicts):
        self.klipper = klipper
        self.dev_dicts = dicts

    def get_dev_names(self):
        for key in self.dev_dicts.keys():
            list = self.klipper.list_names(key)
            self.dev_dicts[key] = list

        return self.dev_dicts

    def get_btn_state(self):
        key = "gcode_button "
        result_dict = {}
        if self.dev_dicts[key] != []:
            sensor_dict = self.klipper.get_info(key)
            for key, value in sensor_dict.items():
                result_dict[key] = value["state"] == "RELEASED"
        return result_dict

    def get_th_state(self):
        key = "temperature_sensor "
        result_dict = {}
        if not self.dev_dicts[key]:
            sensor_dict = self.klipper.get_info(key)
            for key, value in sensor_dict.items():
                result_dict[key] = value["temperature"]
        return result_dict

    def run_fan(self, value):
        self.klipper.run_test_gcode("TEST_FANS FAN_SPEED=" + value)

    def run_heat(self, value):
        self.klipper.run_test_gcode("TEST_HEATS VAL=" + value)
