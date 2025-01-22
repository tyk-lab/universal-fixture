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

    def check_btn_state(self, state):
        result_dict = self.get_btn_state()
        result = all(value is state for value in result_dict.values())
        log_dict = {}
        # print(result_dict)
        if not result:
            # 判定结果
            for key, value in result_dict.items():
                log_dict[key] = "set " + str(state) + "  cur " + str(result_dict[key])
                if value is not state:
                    result_dict[key] = False
                else:
                    result_dict[key] = True
            raise Exception(result_dict, log_dict)
        return result

    def get_th_state(self):
        key = "temperature_sensor "
        result_dict = {}
        if self.dev_dicts[key] != []:
            sensor_dict = self.klipper.get_info(key)
            for key, value in sensor_dict.items():
                result_dict[key] = value["temperature"]
        return result_dict

    def check_th_state(self, th_val):
        result_dict = self.get_th_state()
        tolerance = 1
        print(result_dict)
        log_dict = {}
        # 判定结果
        for key, value in result_dict.items():
            log_dict[key] = (
                "fixture th: " + str(th_val) + "  cur " + str(result_dict[key])
            )
            if value < th_val + tolerance and value > th_val - tolerance:
                result_dict[key] = True
            else:
                result_dict[key] = False
        raise Exception(result_dict, log_dict)

    def run_fan(self, value):
        self.klipper.run_test_gcode("TEST_FANS FAN_SPEED=" + value)

    def run_heat(self, value):
        self.klipper.run_test_gcode("TEST_HEATS VAL=" + value)
