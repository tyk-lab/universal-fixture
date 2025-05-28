"""
@File    :   dev_info.py
@Time    :   2025/04/03
@Desc    :   Obtain product and gage information to determine compliance with requirements
"""

from sqlite3 import Time
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
        fixture.send_and_read_result(FrameType.Opt, "btnSV", val)

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
        from core.utils.opt_log import GlobalLogger

        dev_check_dict = self.get_btn_state(key)

        # Findings
        has_exception = not all(value is state for value in dev_check_dict.values())
        log_dict = {}

        # ok if the device value and the effect of the control are the same
        for key, value in dev_check_dict.items():
            log_dict[key] = "fixture set: " + str(state) + " | dev val： " + str(value)
            if value is not state:
                dev_check_dict[key] = False
            else:
                dev_check_dict[key] = True

        GlobalLogger.log("btn log data:", log_dict)
        if has_exception:
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
        from core.utils.opt_log import GlobalLogger

        dev_dict = self.get_th_info(key, False)
        tolerance = float(GlobalComm.setting_json["temp_check_tolerance"])

        one_feedback = GlobalComm.setting_json["one_th_test_feedback"].lower() == "true"

        normal_temp_range = self._get_normal_temp_range()
        lower_bound = min(normal_temp_range)
        upper_bound = max(normal_temp_range)

        log_dict = {}
        dev_check_dict = {}
        has_exception = False
        check_cnt = 0
        fixture_val = float(next(iter(fixture_dict.values())))
        # Ok if the temperature sensing value is about the same as the fixture value and is in the room temperature range.
        for key, value in dev_dict.items():
            if not one_feedback:
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

        GlobalLogger.log("th log data:", log_dict)
        if has_exception:
            raise TestFailureException(dev_check_dict, log_dict)

    ############################## vol Equipment Related ############################

    def format_vol_info(self, result_dict):
        for key, value in result_dict.items():
            if isinstance(value, str):
                # 根据实际业务可以拓展判断条件，此处简单判断是否以 '0x' 开头且包含逗号
                if value.strip().startswith("0x") and "," in value:
                    s = value
                    parts = [p.strip() for p in s.split(",")]
                    if not parts:
                        return s
                    # 保留第一部分
                    new_parts = [parts[0]]
                    # 处理后续部分
                    for p in parts[1:]:
                        new_parts.append(str(float(p) / 10000))
                    return {key: ", ".join(new_parts)}

    def req_vol_info(self, fixture, is_fields_key):
        from core.utils.exception.ex_test import TestReplyException

        # todo, 获取电压，电流，功耗信息，待验证
        fields_frame_info, comm_frame_info = fixture.extract_fields_between_keys(
            "volSQ"
        )
        frame_info = comm_frame_info
        if is_fields_key:
            frame_info = fields_frame_info
        result_dict = fixture.send_command_and_format_result(
            FrameType.Request, "volSQ", frame_info, 1
        )

        if result_dict == None:
            raise TestReplyException(
                self.req_vol_info.__name__ + ": fixture reply null"
            )

        result_dict = self.format_vol_info(result_dict)
        print("req_vol_info: ", result_dict)
        return result_dict

    def check_vol(self, except_vol_dict, fixtur_dict):
        from core.utils.exception.ex_test import TestFailureException
        from core.utils.opt_log import GlobalLogger

        log_dict = {}
        dev_check_dict = {}
        has_exception = False
        print("check vol", fixtur_dict)

        for key, value in fixtur_dict.items():
            parts = [s.strip() for s in value.split(",")]
            cur_vol = float(parts[1])
            log_dict[key] = "cur: " + value

            if except_vol_dict[key] - 1.3 <= cur_vol <= except_vol_dict[key]:
                dev_check_dict[key] = True
            else:
                dev_check_dict[key] = False
                has_exception = True

        GlobalLogger.log("vol log data:", log_dict)
        if has_exception:
            raise TestFailureException(dev_check_dict, log_dict)

        return log_dict

    ############################## other Equipment Related ############################

    def reset_klipper_state(self):
        self.run_heat("0")
        self.run_fan("0")

    def _wait_dev_signal_reply(self, fixture, dev_type, sample_time, dev_dict):
        """Waiting for a reply to a Poll type message

        Args:
            fixture (_type_): checker handle
            dev_type (_type_): Detection type
            sample_time (_type_): second, mcu unit is millisecond
            dev_dict (_type_): device dictionary

        Returns:
            _type_: Gauge Polling Signal Results
        """
        from core.utils.common import GlobalComm

        fan_ppr = 2
        mcu_sample_time = sample_time * 1000
        frame = {
            dev_type: [{"port": "0", "name": dev_type, "value": str(mcu_sample_time)}],
        }
        result_dict = fixture.send_command_and_format_result(
            FrameType.Poll, dev_type, frame, sample_time
        )

        if result_dict != None and "ok" in str(result_dict):
            result_dict = fixture.send_command_and_format_result(
                FrameType.Request, dev_type
            )
            fan_type = GlobalComm.setting_json["fan_type"]

            # For second-line fans, the air velocity is calculated by means of a jig.
            for key, value in dev_dict.items():
                if value == None:
                    if fan_type != "HighSpeed":
                        freq = int(result_dict[key]) / sample_time
                    else:
                        freq = (
                            int(result_dict[key]) * 2 / sample_time
                        )  # High speed, over 10,000 rpm
                    # References fan.py in klipper: line 99 and pulse_counter.py, pulse_counter.c
                    result_dict[key] = freq * 30.0 / fan_ppr

            return result_dict
        return None

    ############################## heat Equipment Related ############################

    def run_heat(self, value):
        self.klipper.run_test_gcode("_TEST_HEATS RUN=" + value)

    def control_heating_cooling(self, fixture, is_temp_up):
        first_fixture_dict = self.req_th_info(fixture, True)
        time.sleep(1)
        self.run_heat("1" if is_temp_up else "0")
        time.sleep(6)  # Wait for the heater to stabilise
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
            first_th = float(first_dict[key])
            second_th = float(second_dict[key])

            # 1. If it does not match the expected heating or cooling effect, there is an abnormality
            if is_temp_up and second_th > first_th + tolerance:
                check_cnt += 1
            elif is_temp_up == False and first_th > second_th + tolerance:
                check_cnt += 1

            print("check cnt1 ", check_cnt)

            # 2. Judging whether voltage is output when heating
            info_parts = vol_dict[key].split(",")[1]
            cur_vol = float(info_parts.strip())
            if is_temp_up and 20 <= cur_vol <= 24:
                check_cnt += 1
            elif is_temp_up == False and 0 <= cur_vol <= 1:
                check_cnt += 1

            print("check cnt2 ", check_cnt)
            if check_cnt < 2:
                has_exception = True

            # Heating or cooling, voltage changes as required and temperature sensing value will change then it is ok
            dev_check_dict[key] = not has_exception
            sub_val = (
                second_th - first_th
            )  #! A positive value (2>1) when heated and a negative value (2<1) when cooled.
            log_dict[key] = (
                "heat dir: " + str(is_temp_up),  # Cooling is False, heating bit True
                "result: " + str(dev_check_dict[key]),
                "tolerance: " + str(tolerance),
                "th 2 sub 1 val: " + "{:.2f}".format(sub_val),
                "first th: " + "{:.2f}".format(first_th),
                "second th: " + "{:.2f}".format(second_th),
                "check cnt: " + str(check_cnt),
                "vol info: " + str(vol_dict[key]),
            )
            GlobalLogger.log("heat log data:", log_dict)
            check_cnt = 0
        if has_exception:
            raise TestFailureException(dev_check_dict, log_dict)

    ############################## fan Equipment Related ############################

    def req_fan_info(self, fixture, sample_time):
        return self._wait_dev_signal_reply(
            fixture, "fanSQ", sample_time, self.get_fan_state()
        )

    # !If it is not a three-wire fan, value["rpm"] returns None
    def get_fan_state(self):
        key = "fan_generic "
        result_dict = {}
        if self.dev_dicts[key] != []:
            sensor_dict = self.klipper.get_info(key)
            print(sensor_dict)
            for key, value in sensor_dict.items():
                result_dict[key] = value["rpm"]
        return result_dict

    def run_fan(self, value, wait_time=0):
        self.klipper.run_test_gcode("_TEST_FANS FAN_SPEED=" + value)

    def check_fan_state(self, set_val, fixture_dict):
        from core.utils.exception.ex_test import TestFailureException
        from core.utils.common import GlobalComm
        from core.utils.opt_log import GlobalLogger

        expected_rpm = GlobalComm.setting_json["expected_fan_rpm"]
        tolerance = float(GlobalComm.setting_json["fan_check_tolerance"])
        has_exception = False

        log_dict = {}
        result_dict = {}
        dev_dict = self.get_fan_state()

        cur_valid_val = 0
        for key, value in dev_dict.items():
            # Dealing with the co-existence of second and third line fans
            if value != None:
                cur_valid_val = value
            elif fixture_dict != None:
                cur_valid_val = fixture_dict[key]
            else:
                #!Something went wrong, couldn't read the value of the fixture (fixture/device, always read one)
                cur_valid_val = -1
                has_exception = True
                raise TestFailureException(result_dict, log_dict)

            cur_valid_val = round(cur_valid_val, 3)
            log_dict[key] = (
                "expect rpm: " + expected_rpm[set_val],
                " cur rpm: " + str(cur_valid_val),
                " fixture state: " + str(cur_valid_val >= 0),
            )
            if (
                cur_valid_val < float(expected_rpm[set_val]) + tolerance
                and cur_valid_val > float(expected_rpm[set_val]) - tolerance
            ):
                result_dict[key] = True
            else:
                result_dict[key] = False
                has_exception = True
        GlobalLogger.log("fan log data:", log_dict)
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
            result_dict = {
                k: ", ".join([item.strip() for item in v.split(",")[1:]])
                for k, v in result_dict.items()
            }
            rgb_raw_max = 255
            for key, value in result_dict.items():
                result_dict[key] = [
                    round(float(val.strip()) / rgb_raw_max, 2)
                    for val in value.split(",")
                ]
            return result_dict
        raise TestReplyException(self.req_rgb_raw_val.__name__ + ": fixture reply null")

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
        from core.utils.opt_log import GlobalLogger

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
                check_color_index = 0
                fixture_color_dict = dict(zip(color_order, rgb_value_list))

                log_dict[key] = (
                    "set: "
                    + set_color
                    + " "
                    + str(tolerance)
                    + " | fixture color: "
                    + str(fixture_color_dict)
                )

                # Pass if greater than tolerance
                dev_check_dict[key] = True
                # 1. Determine if only one colour value meets the criteria
                for value in fixture_color_dict.values():
                    if value >= tolerance:
                        check_color_index += 1

                # 2. Determination of compliance with the criteria for colour values (white - non-white)
                if set_color != "white":
                    if not (
                        fixture_color_dict[set_color] >= tolerance
                        and check_color_index == 1
                    ):
                        dev_check_dict[key] = False
                        has_exception = True
                else:
                    if not check_color_index >= 3:
                        dev_check_dict[key] = False
                        has_exception = True
            else:  # Devices that do not participate in the detection, directly default ok
                dev_check_dict[key] = True
                log_dict[key] = "No testing"

        GlobalLogger.log("rgbw log data:", log_dict)
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

    def run_monitoring(self, dev_type, fixture, dir):
        frame = {
            dev_type: [{"port": "0", "name": dev_type, "value": "1"}],
        }
        fixture.send_command(FrameType.Poll, dev_type, "1", frame)
        time.sleep(0.5)
        self.run_motor(dir)
        time.sleep(2)

    def req_encoder_info(self, dev_type, fixture, run_time_s):
        return self._stop_wait_dev_encoder_reply(fixture, dev_type, run_time_s)

    def _split_result_dict(self, original_dict):
        val_dict = {}
        dir_dict = {}
        for key, value in original_dict.items():
            parts = value.split(", ")
            if len(parts) == 2:
                val_dict[key] = parts[0]
                dir_dict[key] = parts[1]
        return val_dict, dir_dict

    def _stop_wait_dev_encoder_reply(self, fixture, dev_type, sample_time):
        from core.utils.exception.ex_test import TestReplyException

        frame = {
            dev_type: [{"port": "0", "name": dev_type, "value": "0"}],
        }
        result_dict = fixture.send_command_and_format_result(
            FrameType.Poll, dev_type, frame, sample_time
        )

        if result_dict != None and "ok" in str(result_dict):
            result_dict = fixture.send_command_and_format_result(
                FrameType.Request, dev_type
            )
            return self._split_result_dict(result_dict)

        raise TestReplyException(
            self._stop_wait_dev_encoder_reply.__name__ + ": fixture reply null"
        )

    def run_motor(self, dir):
        dir = "1" if dir else "0"
        self.klipper.run_test_gcode("_TEST_MOTOR_A_LOOP DIR=" + dir)

    def check_motor_distance(self, fixture_dict):
        from core.utils.exception.ex_test import TestFailureException
        from core.utils.common import GlobalComm

        # todo, 设一圈的脉冲数为 200*16*40=128000
        stander_pulses = 216189
        # tolerance = float(GlobalComm.setting_json["motor_encoder_tolerance"])
        tolerance = 10000000
        log_dict = {}
        result_dict = {}
        has_exception = False

        a_loop_pulses_up = stander_pulses + tolerance
        a_loop_pulses_down = stander_pulses - tolerance
        tip = " stander: " + str(stander_pulses) + " tolerance: " + str(tolerance)
        for key, pulses in fixture_dict.items():
            val = float(pulses)
            log_dict[key] = "  cur pulses:  " + str(pulses) + tip
            print(a_loop_pulses_down, val, a_loop_pulses_up)
            if a_loop_pulses_down <= val <= a_loop_pulses_up:
                result_dict[key] = True
            else:
                result_dict[key] = False
                has_exception = True

        print("check ", has_exception)
        if has_exception:
            raise TestFailureException(result_dict, log_dict)

    def check_motor_dir(self, dir_dict_1, dir_dict_2):
        from core.utils.exception.ex_test import TestFailureException

        check_cnt = 0
        if len(set(dir_dict_1.values())) == 1 and len(set(dir_dict_2.values())) == 1:
            check_cnt += 1

        if dir_dict_1 == dir_dict_2:
            check_cnt += 1

        has_exception = check_cnt >= 2
        if has_exception:
            # Make produce exception information
            log_dict = {}
            result_dict = {}
            for key, dir in dir_dict_1.items():
                log_dict[key] = "directional inconsistency"
                result_dict[key] = False
            raise TestFailureException(result_dict, log_dict)

    ############################## other Equipment Related ############################

    def run_other(self, run):
        enable = "1" if run else "0"
        self.klipper.run_test_gcode("_TEST_OTHER RUN=" + enable)
