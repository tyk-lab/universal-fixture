"""
@File    :   dev_info.py
@Time    :   2025/04/03
@Desc    :   Obtain product and gage information to determine compliance with requirements
"""

import time
from core.model.json_protocol import FrameType
from core.utils.thermistor import CustomThermistor


class DevInfo:
    def __init__(self, klipper, dicts):
        self.klipper = klipper
        self.dev_dicts = dicts

        self.prev_val = 0, 0, 0
        self.thermistor = CustomThermistor()

    def get_dev_info(self):
        for key in self.dev_dicts.keys():
            list = self.klipper.list_names(key)
            self.dev_dicts[key] = list

        return self.dev_dicts

    ############################ btn Equipment Related ############################
    # Controls the relevant port of the btn module, outputs val
    def otp_btn_state(self, fixture, val):
        fixture.send_command(FrameType.Opt, "btnSV", val)

    # Manipulate the product board to get the corresponding status
    def get_btn_state(self, key):
        result_dict = {}
        if self.dev_dicts[key] != []:
            sensor_dict = self.klipper.get_info(key)
            for key, value in sensor_dict.items():
                result_dict[key] = value["state"] == "RELEASED"
        return result_dict

    # Check that the function is eligible
    def check_btn_state(self, key, state):
        from core.utils.exception.ex_test import TestFailureException

        dev_check_dict = self.get_btn_state(key)

        # Findings
        has_exception = not all(value is state for value in dev_check_dict.values())
        log_dict = {}

        # Throw an exception if something goes wrong
        if has_exception:
            for key, value in dev_check_dict.items():
                log_dict[key] = (
                    "fixture set: "
                    + str(state)
                    + " dev val： "
                    + str(dev_check_dict[key])
                )
                if value is not state:
                    dev_check_dict[key] = False
                else:
                    dev_check_dict[key] = True
            raise TestFailureException(dev_check_dict, log_dict)

    ############################## th Equipment Related ############################

    def req_th_state(self, fixture, is_fields_key):
        """Get the value of th temperature in the fixture

        Args.
            fixture (_type_): fixture handle
            is_fields_key (bool): Check if it's a start_heat_th-end_heat_th field

        Returns:
            _type_: Returns a sequence of temperature sensors, e.g. {th0: "31.32", th0: "32.12"}
        """
        fields_frame_info, comm_frame_info = fixture.extract_fields_between_keys("thSQ")
        frame_info = comm_frame_info
        if is_fields_key:
            frame_info = fields_frame_info
        result = fixture.send_command_and_format_result(
            FrameType.Request, "thSQ", frame_info
        )
        if result != None:
            for key, value in result.items():
                result[key] = self.thermistor.get_temp(float(value))
        return result

    def get_th_state(self, klipper_key, is_fields_key):
        """Get the value of temperature sensing

        Args:
            klipper_key (_type_): name of the temperature sensing in the klipper
            is_fields_key (bool): confirm special temperature sensing value information (e.g., problems with extruder and bed types)

        Returns.
            _type_: Returns a sequence of temperature sensors, e.g. {th0: "31.32", th0: "32.12"}
        """
        result_dict = {}
        if self.dev_dicts[klipper_key] != []:
            sensor_dict = self.klipper.get_info(klipper_key)
            if not is_fields_key:
                for key, value in sensor_dict.items():
                    result_dict[key] = value["temperature"]
            else:
                for key, value in sensor_dict.items():
                    if "temperature" in value:
                        result_dict[klipper_key] = value["temperature"]
        return result_dict

    def check_th_state(self, key, fixture_dict):
        from core.utils.exception.ex_test import TestFailureException
        from core.utils.common import GlobalComm

        dev_check_dict = self.get_th_state(key, False)
        tolerance = float(GlobalComm.setting_json["temp_check_tolerance"])

        log_dict = {}
        has_exception = False
        # Equipment Comparison Fixture Values
        for key, value in dev_check_dict.items():
            fixture_val = float(fixture_dict[key])
            log_dict[key] = (
                "tolerance: "
                + str(tolerance)
                + "\r\nfixture th: "
                + str(fixture_val)
                + " dev th: "
                + str(dev_check_dict[key])
            )

            if value < fixture_val + tolerance and value > fixture_val - tolerance:
                dev_check_dict[key] = True
            else:
                dev_check_dict[key] = False
                has_exception = True
        if has_exception:
            raise TestFailureException(dev_check_dict, log_dict)

    ############################## heat Equipment Related ############################

    def run_heat(self, value):
        self.klipper.run_test_gcode("_TEST_HEATS RUN=" + value)

    def control_heating_cooling(self, fixture, is_temp_up):
        first_fixture_dict = self.req_th_state(fixture, True)
        time.sleep(1)
        self.run_heat("1" if is_temp_up else "0")
        time.sleep(5)
        second_fixture_dict = self.req_th_state(fixture, True)
        return first_fixture_dict, second_fixture_dict

    def check_ex_th_state(self, first_dict, second_dict, is_temp_up):
        from core.utils.exception.ex_test import TestFailureException
        from core.utils.common import GlobalComm

        # It's at least 10 degrees off.
        tolerance = float(GlobalComm.setting_json["temp_check_tolerance"]) + 20

        log_dict = {}
        dev_check_dict = {}
        has_exception = False
        for key, value in first_dict.items():
            first_val = float(first_dict[key])
            second_val = float(second_dict[key])

            # If it does not match the expected heating or cooling effect, there is an abnormality
            has_exception = not (
                second_val > first_val + tolerance
                if is_temp_up
                else first_val > second_val + tolerance
            )

            # There is an abnormality, and the result of the device detection is False
            dev_check_dict[key] = not has_exception
            # print("\r\ncheck_ex_th_state", key, is_temp_up, log_dict[key])
            sub_val = (
                second_val - first_val
            )  #! A positive value (2>1) when heated and a negative value (2<1) when cooled.
            log_dict[key] = (
                "heat dir: " + str(is_temp_up),  # Cooling is False, heating bit True
                "result: " + str(dev_check_dict[key]),
                "tolerance: " + str(tolerance),
                "th 2 sub 1 val: " + "{:.2f}".format(sub_val),
                "first th: " + str(first_val),
                "second th: " + str(second_val),
            )
        if has_exception:
            raise TestFailureException(dev_check_dict, log_dict)

    ############################## fan Equipment Related ############################

    def get_fan_state(self):
        key = "fan_generic "
        result_dict = {}
        if self.dev_dicts[key] != []:
            sensor_dict = self.klipper.get_info(key)
            for key, value in sensor_dict.items():
                result_dict[key] = value["rpm"]
        return result_dict

    def run_fan(self, value):
        self.klipper.run_test_gcode("_TEST_FANS FAN_SPEED=" + value)

    def check_fan_state(self, set_val, fixture_dict):
        from core.utils.exception.ex_test import TestFailureException

        # todo, 需要校正
        expected_rpm = {
            "0": 0,
            "0.2": 2400,
            "0.8": 8000,
        }
        tolerance = 500  # todo

        has_exception = False
        result_dict = self.get_fan_state()
        # print(result_dict)
        log_dict = {}
        # 判定结果
        for key, value in result_dict.items():
            cur_valid_val = value if value != None else fixture_dict[key]
            cur_valid_val = round(cur_valid_val, 3)

            # print(cur_valid_val)
            log_dict[key] = "  cur rpm:  " + str(cur_valid_val)
            if (
                cur_valid_val < expected_rpm[set_val] + tolerance
                and cur_valid_val > expected_rpm[set_val] - tolerance
            ):
                result_dict[key] = True
            else:
                result_dict[key] = False
                has_exception = True

        if has_exception:
            raise TestFailureException(result_dict, log_dict)

    ############################## rgbw Equipment Related ############################

    def run_rgbw(self, key):
        color_dict = {
            "red": "0.0",
            "blue": "0.0",
            "green": "0.0",
            "white": "0.0",
        }
        if key in color_dict:
            color_dict[key] = "1.0"

        self.klipper.run_test_gcode(
            f"TEST_RGBWS RED={color_dict['red']} GREEN={color_dict['green']} BLUE={color_dict['blue']} WHITE={color_dict['white']}"
        )

        return color_dict

    def get_rgbw_state(self):
        key = "neopixel "
        result_dict = {}
        if self.dev_dicts[key] != []:
            sensor_dict = self.klipper.get_info(key)
            for key, value in sensor_dict.items():
                result_dict[key] = value
        return result_dict

    def check_rgbw_state(self, set_color_dict, fixture_dict):
        from core.utils.exception.ex_test import TestFailureException

        result_dict = self.get_rgbw_state()
        log_dict = {}
        tolerance = 0.2

        # print("check_rgbw_state")
        has_exception = False

        # 定义检测的颜色顺序
        color_order = ["red", "green", "blue", "white"]

        # 判定结果
        for key in result_dict.keys():
            rgb_values = fixture_dict[key].split(", ")
            # 组合对应治具数据为元组，方便颜色匹对
            fixture_key_zip = zip(color_order, rgb_values)
            log_dict[key] = (
                "fixture color: "
                + str(fixture_dict[key])
                + "  cur "
                + str(set_color_dict)
            )

            result_dict[key] = True
            for color, fixture_val in fixture_key_zip:
                # print(key, "  ", color)
                if not float(fixture_val) >= float(set_color_dict[color]) - tolerance:
                    result_dict[key] = False
                    has_exception = True
                    break

            # print("\r\n")

        if has_exception:
            raise TestFailureException(result_dict, log_dict)

    ############################## adxl345 Equipment Related ############################

    def check_adxl345_state(self, inaccuracies=1000):
        from core.utils.exception.ex_test import TestFailureException

        if self.klipper.is_connect(False):
            cur_val = self.klipper.accelerometer_run()

            cur = list(map(float, cur_val.split(", ")))
            cur = [round(num, 3) for num in cur]

            prev = list(self.prev_val)

            differences = [abs(cur[j] - prev[j]) for j in range(3)]
            differences = [round(num, 3) for num in differences]

            self.prev_val = cur
            test_result = all(diff > inaccuracies for diff in differences)
            # 结果，标准偏差， 差异值, 当前的标准值
            return (test_result, inaccuracies, differences, cur)

        raise TestFailureException()

    # todo, 测试adxl345使用
    # def check_adxl345_state(self, inaccuracies=30):
    #     print("check_adxl345_state")
    #     import random

    #     # 结果，差异值, 当前的标准值,
    #     return (True, 200, [3, 3, 3], [3, random.random(), random.random()])

    ############################## motor Equipment Related ############################

    def run_motor(self, dir):
        self.klipper.run_test_gcode("_TEST_MOTOR_A_LOOP DIR=" + dir)

    # 脉冲值格式 {"a": 3000, "b": 3000, ...}
    def check_motor_distance(self, fixture_dict):
        from core.utils.exception.ex_test import TestFailureException

        # todo, 设一圈的脉冲数为 200*16*40=128000
        tolerance = 300
        stander_pulses = 128000
        log_dict = {}
        result_dict = {}
        a_loop_pulses_up = stander_pulses + tolerance
        a_loop_pulses_down = stander_pulses + tolerance

        tip = "stander: " + str(stander_pulses) + " tolerance: " + str(tolerance)
        # 判定结果
        for key, pulses in fixture_dict.items():
            log_dict[key] = "  cur pulses:  " + str(pulses) + tip
            if pulses <= a_loop_pulses_up and pulses >= a_loop_pulses_down:
                result_dict[key] = True
            else:
                result_dict[key] = False
                has_exception = True

        if has_exception:
            raise TestFailureException(result_dict, log_dict)

    def run_heats(self, enalbe):
        self.klipper.run_test_gcode("_TEST_HEATS RUN=" + enalbe)

    def check_heats_state(self, init_temp_dict, next_temp_dict):
        from core.utils.exception.ex_test import TestFailureException

        log_dict = {}
        result_dict = {}

        # 判定结果
        for key, value in init_temp_dict.items():
            log_dict[key] = (
                "  init temp:  " + str(value) + "next temp: " + str(next_temp_dict[key])
            )
            if value > next_temp_dict[key]:
                result_dict[key] = True
            else:
                result_dict[key] = False
                has_exception = True

        if has_exception:
            raise TestFailureException(result_dict, log_dict)
