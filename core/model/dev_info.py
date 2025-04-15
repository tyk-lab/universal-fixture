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

        # ok if the device value and the effect of the control are the same
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

    def req_th_info(self, fixture, is_fields_key):
        from core.utils.exception.ex_test import TestReplyException

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
        result_dict = fixture.send_command_and_format_result(
            FrameType.Request, "thSQ", frame_info
        )
        if result_dict != None:
            for key, value in result_dict.items():
                result_dict[key] = self.thermistor.get_temp(float(value))
            return result_dict

        raise TestReplyException(self.req_th_info.__name__ + ": fixture reply null")

    def get_th_info(self, klipper_key, is_fields_key):
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

    def _get_normal_temp_range(self):
        from core.utils.common import GlobalComm

        # For example "(10-35)"
        s = GlobalComm.setting_json["normal_temp_range"]
        s_inner = s[1:-1]  # get "10-35"
        number_strs = s_inner.split(
            "-"
        )  # Split to get a list of number strings: ['10', '35']
        return [
            float(num) for num in number_strs
        ]  # Convert to floating point numbers: [10.0, 35.0]

    def check_th(self, key, fixture_dict):
        from core.utils.exception.ex_test import TestFailureException
        from core.utils.common import GlobalComm

        dev_dict = self.get_th_info(key, False)
        tolerance = float(GlobalComm.setting_json["temp_check_tolerance"])

        normal_temp_range = self._get_normal_temp_range()
        lower_bound = min(normal_temp_range)
        upper_bound = max(normal_temp_range)

        log_dict = {}
        dev_check_dict = {}
        has_exception = False
        check_cnt = 0
        # Ok if the temperature sensing value is about the same as the fixture value and is in the room temperature range.
        for key, value in dev_dict.items():
            fixture_val = float(fixture_dict[key])

            # 1. Two comparisons. Big difference.
            if fixture_val - tolerance <= value <= fixture_val + tolerance:
                check_cnt += 1

            # 2. In the normal temperature range
            if lower_bound <= value <= upper_bound:
                check_cnt += 1

            has_exception = check_cnt < 2
            if has_exception:
                dev_check_dict[key] = False

            log_dict[key] = (
                "normal_temp range: " + str(normal_temp_range),
                "fixture th: " + str(fixture_val),
                "dev th: " + str(value),
                "check cnt:" + str(check_cnt),
            )
            check_cnt = 0

        if has_exception:
            raise TestFailureException(dev_check_dict, log_dict)

    ############################## vol Equipment Related ############################

    def req_vol_info(self, fixture, is_fields_key, is_verbose):
        from core.utils.exception.ex_test import TestReplyException

        # todo, 获取电压，电流，功耗信息，待验证
        fields_frame_info, comm_frame_info = fixture.extract_fields_between_keys(
            "volSQ"
        )
        frame_info = comm_frame_info
        if is_fields_key:
            frame_info = fields_frame_info
        result_dict = fixture.send_command_and_format_result(
            FrameType.Request, "volSQ", frame_info
        )

        if result_dict == None:
            raise TestReplyException(
                self.req_vol_info.__name__ + ": fixture reply null"
            )
        elif not is_verbose:
            result_dict = {k: v.split(",")[1].strip() for k, v in result_dict.items()}

        print("req_vol_info: ", result_dict)
        return result_dict

    ############################## heat Equipment Related ############################

    def run_heat(self, value):
        self.klipper.run_test_gcode("_TEST_HEATS RUN=" + value)

    def control_heating_cooling(self, fixture, is_temp_up):
        first_fixture_dict = self.req_th_info(fixture, True)
        time.sleep(1)
        self.run_heat("1" if is_temp_up else "0")
        time.sleep(5)
        second_fixture_dict = self.req_th_info(fixture, True)
        return first_fixture_dict, second_fixture_dict

    def check_heat(self, first_dict, second_dict, vol_dict, is_temp_up):
        from core.utils.exception.ex_test import TestFailureException
        from core.utils.common import GlobalComm
        from core.utils.opt_log import GlobalLogger

        tolerance = float(GlobalComm.setting_json["heat_temp_check_tolerance"])

        log_dict = {}
        dev_check_dict = {}
        has_exception = False
        check_cnt = 0
        for key, value in first_dict.items():
            first_val = float(first_dict[key])
            second_val = float(second_dict[key])

            # 1. If it does not match the expected heating or cooling effect, there is an abnormality
            if is_temp_up and second_val > first_val + tolerance:
                check_cnt += 1
            elif is_temp_up == False and first_val > second_val + tolerance:
                check_cnt += 1

            # 2. Judging whether voltage is output when heating
            info_parts = vol_dict[key].split(",")[1]
            cur_vol = float(info_parts.strip())
            if is_temp_up and 20 <= cur_vol <= 24:
                check_cnt += 1
            elif is_temp_up == False and 0 <= cur_vol <= 1:
                check_cnt += 1

            if check_cnt < 2:
                has_exception = True

            # Heating or cooling, voltage changes as required and temperature sensing value will change then it is ok
            dev_check_dict[key] = not has_exception
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
                "check cnt: " + str(check_cnt),
                "vol info: " + str(vol_dict[key]),
            )
            # Output debugging information
            GlobalLogger.debug_print(
                self.check_heat.__name__, key, is_temp_up, log_dict[key]
            )
            GlobalLogger.log(self.check_heat.__name__, key, is_temp_up, log_dict[key])
            check_cnt = 0

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
            f"_TEST_RGBWS RED={color_dict['red']} GREEN={color_dict['green']} BLUE={color_dict['blue']} WHITE={color_dict['white']}"
        )

    def req_rgb_raw_val(self, fixture):
        from core.utils.exception.ex_test import TestReplyException

        result_dict = fixture.send_command_and_format_result(
            FrameType.Request, "rgbwSQ"
        )
        if result_dict != None:
            rgb_raw_max = 255
            for key, value in result_dict.items():
                result_dict[key] = [
                    round(float(val.strip()) / rgb_raw_max, 2)
                    for val in value.split(",")
                ]
            return result_dict
        raise TestReplyException(self.req_th_info.__name__ + ": fixture reply null")

    def get_rgbw_state(self):
        key = "neopixel "
        result_dict = {}
        if self.dev_dicts[key] != []:
            sensor_dict = self.klipper.get_info(key)
            for key, value in sensor_dict.items():
                result_dict[key] = value
        return result_dict

    def check_rgbw_state(self, set_color, fixture_dict):
        from core.utils.exception.ex_test import TestFailureException

        log_dict = {}
        dev_check_dict = {}
        has_exception = False

        #! Define the data format of the sensor, consistent with the data returned by the fixture.
        color_order = ["red", "green", "blue"]
        dev_dict = self.get_rgbw_state()
        tolerance = 0.8

        for key in dev_dict.keys():
            if key in fixture_dict:
                # Format and combine the colour data to output something like: {'blue': 33, 'green': 33, 'red': 33}
                rgb_value_list = fixture_dict[key]
                fixture_color_dict = dict(zip(color_order, rgb_value_list))

                log_dict[key] = (
                    "set: " + set_color + " | fixture color: " + str(fixture_color_dict)
                )

                # Pass if greater than tolerance
                dev_check_dict[key] = True
                if set_color != "white":
                    if not (fixture_color_dict[set_color] >= tolerance):
                        dev_check_dict[key] = False
                        has_exception = True
                else:
                    for value in fixture_color_dict.values():
                        if not (value >= tolerance):
                            dev_check_dict[key] = False
                            has_exception = True
                            break
            else:  # Devices that do not participate in the detection, directly default ok
                dev_check_dict[key] = True
                log_dict[key] = "No testing"
        if has_exception:
            raise TestFailureException(dev_check_dict, log_dict)

    ############################## adxl345 Equipment Related ############################

    def check_accel_state(self):
        from core.utils.exception.ex_test import TestFailureException
        from core.utils.common import GlobalComm

        if self.klipper.is_connect(False):
            inaccuracies = float(GlobalComm.setting_json["accel_inaccuracies"])
            cur_accel_vals = self.klipper.accelerometer_run()
            prev_accel_result = list(self.prev_val)

            # Converting a string to a list of floating point numbers
            cur_accel_result = list(map(float, cur_accel_vals.split(", ")))
            cur_accel_result = [round(num, 3) for num in cur_accel_result]

            # Round the last difference to 3 decimal places.
            differences = [
                abs(cur_accel_result[j] - prev_accel_result[j]) for j in range(3)
            ]
            differences = [round(num, 3) for num in differences]

            # Determine whether the current differential meets the test requirements
            test_result = all(diff > inaccuracies for diff in differences)
            self.prev_val = cur_accel_result

            # Result: Standard deviation, Difference, Current standard value
            return (test_result, inaccuracies, differences, cur_accel_result)

        raise TestFailureException()

    # todo, Testing the use of adxl345
    # def check_adxl345_state(self, inaccuracies=30):
    #     print("check_adxl345_state")
    #     import random

    #     # Result, Difference value, Current standard value,
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
