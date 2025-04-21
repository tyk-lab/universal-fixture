"""
@File    :   test_dev.py
@Time    :   2025/04/03
@Desc    :   Define the device testing process and callback related results
"""

import json
from core.utils.common import GlobalComm
from core.model.dev_info import DevInfo
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QColor
import traceback
import time


class DevTest:
    def __init__(self, klipper, fixtrue):
        # Table of devices under type
        self.dev_dicts = {
            "gcode_button ": [],
            "fan_generic ": [],
            "temperature_sensor ": [],
            "output_pin ": [],
            "heater_bed": [],
            "extruder": [],
            "neopixel ": [],
            # "adxl345": [],  # This won't read in klipper.
            # "lis2dw12": [],  # This won't read in klipper.
        }

        self.fields_to_check = {
            "adxl345": False,
            "lis2dw": False,
        }
        # Tuple meaning: whether to initialise once, whether to find the key value
        self.fields_checked_tuple = (False, False)

        self.klipper = klipper
        self.fixture = fixtrue
        self.dev = DevInfo(klipper, self.dev_dicts)

    def set_update_callback(self, add_row_callback, modify_row_callback):
        self.add_row_callback = add_row_callback
        self.modify_row_callback = modify_row_callback

    def init_model(self):
        self.dev_dicts = self.dev.get_dev_info()

    def show_keys_result(self, key_tuple, log_dict=None, result_dict=None):
        """Show results for multiple key values like (key1, key2)

        Args:
            key_tuple (_type_): key tuple (key1, key2)
            log_dict (_type_, optional): Log messages on exceptions. Defaults to None.
            result_dict (_type_, optional): Results of the test. Defaults to None.
        """
        result = True
        if result_dict != None:
            result = all(value is True for value in result_dict.values())
        # Converting a dictionary to a formatted JSON string
        json_str = json.dumps(log_dict, indent=2, ensure_ascii=False)
        # Converts escaped characters to actual characters by decoding them
        formatted_str = json_str.encode("utf-8").decode("unicode_escape")
        self.show_sigle_result(key_tuple, result, formatted_str)

    def show_result(self, key, log_dict=None, result_dict=None):
        """Display the results of the test

        Args:
            key (_type_): Keywords for klipper, like fan, adxl345, gcode_button etc
            log_dict (_type_, optional): Not None is an exception log message. Defaults to None.
            result_dict (_type_, optional):
            If it is not None, the test result will be displayed abnormally. Defaults to None.
        """
        i = 0
        # Iterate over the corresponding devices and update the result
        result = True
        log = ""
        for item in self.dev_dicts[key]:
            if result_dict != None:
                result = result_dict[item]
            if log_dict != None:
                log = log_dict[item]

            color = GlobalComm.err_color
            if result:
                color = GlobalComm.ok_color
            raw_data = [
                result,
                key,  # type
                item,  # name
                log,  # log
            ]
            # print(raw_data)
            self.add_row_callback(raw_data, color)
            i += 1

    def show_sigle_result(self, key, result, log):
        color = GlobalComm.err_color
        if result or result == None:
            color = GlobalComm.ok_color

        raw_data = [
            result,
            key,  # type
            key,  # name
            log,  # log
        ]
        # print(raw_data)
        self.add_row_callback(raw_data, color)

    def _raise_connect_exception(self, klipper_state, fixture_state):
        from core.utils.exception.ex_test import (
            TestConnectException,
        )

        raise TestConnectException(
            GlobalComm.get_langdic_val("exception_tip", "excep_connect")
            + ": klipper state "
            + str(klipper_state)
            + "\r\n",
            "fixture state " + str(fixture_state),
        )

    def _test_keys_failture_exception(self, key_tuple, result, message):
        self.show_keys_result(key_tuple, message, result)

    def _test_keys_failture_exception(self, e, key_tuple):
        """If the test fails, go here to display an exception message

        Args:
            e (_type_): Exception parameters
            key_tuple (_type_): klipper key tuple
        """
        result_dict = e.args[0]
        log_dict = e.args[1]
        self.show_keys_result(key_tuple, log_dict, result_dict)

    def _test_failture_exception(self, e, key):
        """If the test fails, go here to display an exception message

        Args:
            e (_type_): Exception parameters
            key (_type_): klipper key
        """
        result_dict = e.args[0]
        log_dict = e.args[1]
        self.show_result(key, log_dict, result_dict)

    ############################## btn Equipment Related ############################

    def test_btn(self):
        from core.utils.opt_log import GlobalLogger
        from core.utils.exception.ex_test import (
            TestFailureException,
        )

        klipper_state = self.klipper.is_connect(False)
        fixture_state = self.fixture.is_connect(True)
        key = "gcode_button "

        if klipper_state and fixture_state:
            try:
                if self.dev_dicts[key] != []:
                    GlobalLogger.divider_head_log(key)
                    self.dev.otp_btn_state(self.fixture, "1")
                    self.dev.check_btn_state(key, True)

                    self.dev.otp_btn_state(self.fixture, "0")
                    self.dev.check_btn_state(key, False)

                    self.show_result(key)
            except TestFailureException as e:
                self._test_failture_exception(e, key)
        else:
            self._raise_connect_exception(klipper_state, fixture_state)

    ############################## th Equipment Related ############################

    def test_comm_th(self):
        from core.utils.opt_log import GlobalLogger
        from core.utils.exception.ex_test import TestReplyException
        from core.utils.exception.ex_test import (
            TestFailureException,
        )

        klipper_state = self.klipper.is_connect(False)
        fixture_state = self.fixture.is_connect(True)

        key = "temperature_sensor "
        if klipper_state and fixture_state:
            try:
                if self.dev_dicts[key] != []:
                    GlobalLogger.divider_head_log(key)
                    fixture_dict = self.dev.req_th_info(self.fixture, False)
                    self.dev.check_th(key, fixture_dict)
                    self.show_result(key)
            except TestFailureException as e:
                self._test_failture_exception(e, key)
            except TestReplyException as e:
                for item in self.dev_dicts[key]:
                    self.show_sigle_result(item, False, e.message)
        else:
            self._raise_connect_exception(klipper_state, fixture_state)

    ############################## heat Equipment Related ############################

    def test_heat(self):
        from core.utils.opt_log import GlobalLogger
        from core.utils.exception.ex_test import TestReplyException
        from core.utils.exception.ex_test import (
            TestFailureException,
        )

        klipper_state = self.klipper.is_connect(False)
        fixture_state = self.fixture.is_connect(True)

        key = "extruder"
        other_key = "heater_bed"
        vol_fixture_dict = {}
        if klipper_state and fixture_state:
            try:
                if self.dev_dicts[key] != [] or self.dev_dicts[other_key]:
                    GlobalLogger.divider_head_log("extruder or heater_bed heat")

                    ##################### init part #######################
                    vol_init_dict = self.dev.req_vol_info(self.fixture, True, True)
                    init_th_dict = self.dev.req_th_info(self.fixture, True)

                    ##################### heat part #######################
                    first_dict, second_dict = self.dev.control_heating_cooling(
                        self.fixture, True
                    )
                    vol_heat_dict = self.dev.req_vol_info(self.fixture, True, True)
                    self.dev.check_heat(first_dict, second_dict, vol_heat_dict, True)

                    ##################### cooling part #######################
                    first_dict, second_dict = self.dev.control_heating_cooling(
                        self.fixture, False
                    )
                    vol_cooling_dict = self.dev.req_vol_info(self.fixture, True, True)
                    self.dev.check_heat(
                        first_dict, second_dict, vol_cooling_dict, False
                    )

                    ##################### show result #######################
                    vol_fixture_dict["vol"] = (
                        "init vol: " + str(vol_init_dict),
                        "init th: " + str(init_th_dict),
                        "cooling vol" + str(vol_cooling_dict),
                        "heat vol" + str(vol_heat_dict),
                    )
                    self.show_keys_result((key, other_key), vol_fixture_dict)
            except TestFailureException as e:
                self.dev.reset_klipper_state()
                self._test_keys_failture_exception(e, (key, other_key))
            except TestReplyException as e:
                self.dev.reset_klipper_state()
                self._test_keys_failture_exception((key, other_key), False, e.message)
        else:
            self._raise_connect_exception(klipper_state, fixture_state)

    ############################## rgbw Equipment Related ############################

    def test_rgbw(self):
        from core.utils.opt_log import GlobalLogger
        from core.utils.exception.ex_test import (
            TestFailureException,
        )

        klipper_state = self.klipper.is_connect(False)
        fixture_state = self.fixture.is_connect(True)

        key = "neopixel "
        if klipper_state and fixture_state:
            try:
                # !External small screens like lv are not controlled by the lamp beads and are not handled
                """The fixture returns similar data
                fixture_dict = {
                        #                r    g    b
                        "my_neopixel": "0.9, 0.0, 0.1",
                        "fysetc_mini12864": "0.9, 0.0, 0.1",
                    }
                """
                if self.dev_dicts[key] != []:
                    GlobalLogger.divider_head_log(key)

                    # Test Red
                    set_color = "red"
                    self.dev.run_rgbw(set_color)
                    fixture_dict = self.dev.req_rgb_raw_val(self.fixture)
                    self.dev.check_rgbw_state(set_color, fixture_dict)

                    # Test Blue
                    set_color = "blue"
                    self.dev.run_rgbw(set_color)
                    fixture_dict = self.dev.req_rgb_raw_val(self.fixture)
                    self.dev.check_rgbw_state(set_color, fixture_dict)

                    # Test Green
                    set_color = "green"
                    self.dev.run_rgbw(set_color)
                    fixture_dict = self.dev.req_rgb_raw_val(self.fixture)
                    self.dev.check_rgbw_state(set_color, fixture_dict)

                    # Test White
                    set_color = "white"
                    self.dev.run_rgbw(set_color)
                    fixture_dict = self.dev.req_rgb_raw_val(self.fixture)
                    self.dev.check_rgbw_state(set_color, fixture_dict)

                    self.show_result(key)
                    return
            except TestFailureException as e:
                self._test_failture_exception(e, key)
        else:
            self._raise_connect_exception(klipper_state, fixture_state)

    ############################## fan Equipment Related ############################

    def test_fan(self):
        from core.utils.opt_log import GlobalLogger
        from core.utils.exception.ex_test import (
            TestFailureException,
        )

        klipper_state = self.klipper.is_connect(False)
        fixture_state = self.fixture.is_connect(True)

        key = "fan_generic "
        sample_time = 1  # second
        wait_klipper_time = 4.3
        if klipper_state and fixture_state:
            try:
                if self.dev_dicts[key] != []:
                    GlobalLogger.divider_head_log(key)
                    set_val = "0.8"
                    self.dev.run_fan(set_val, wait_klipper_time)
                    fixture_dict = self.dev.req_fan_info(self.fixture, sample_time)
                    self.dev.check_fan_state(set_val, fixture_dict)

                    set_val = "0.3"
                    self.dev.run_fan(set_val, wait_klipper_time)
                    fixture_dict = self.dev.req_fan_info(self.fixture, sample_time)
                    self.dev.check_fan_state(set_val, fixture_dict)

                    set_val = "0"
                    self.dev.run_fan(set_val, wait_klipper_time)
                    fixture_dict = self.dev.req_fan_info(self.fixture, sample_time)
                    self.dev.check_fan_state(set_val, fixture_dict)

                    self.show_result(key)
            except TestFailureException as e:
                self.dev.reset_klipper_state()
                self._test_failture_exception(e, key)
        else:
            self._raise_connect_exception(klipper_state, fixture_state)

    ############################## accel Equipment Related ############################

    def test_accel(self, cfg_path, dialog, signal):
        from core.utils.parse_cfg_file import check_config_field
        from core.utils.opt_log import GlobalLogger

        GlobalLogger.divider_head_log("accel")
        klipper_state = self.klipper.is_connect(False)

        if klipper_state:
            init_check, fields_check = self.fields_checked_tuple
            GlobalLogger.debug_print(
                self.test_accel.__name__,
                "fields_checked_tuple: ",
                self.fields_checked_tuple,
            )
            if not init_check:
                self.fields_checked_tuple = check_config_field(
                    cfg_path, self.fields_to_check
                )

            elif fields_check:
                for key, value in self.fields_to_check.items():
                    if value:
                        dialog.set_title_name(key)
                        dialog.set_check_fun(
                            self.dev.check_accel_state, self.show_sigle_result
                        )
                        signal.emit()
        else:
            self._raise_connect_exception(klipper_state, False)

    ############################## motor Equipment Related ############################

    def test_motor(self):
        from core.utils.opt_log import GlobalLogger
        from core.utils.exception.ex_test import (
            TestFailureException,
            TestReplyException,
        )

        klipper_state = self.klipper.is_connect(False)
        fixture_state = self.fixture.is_connect(True)

        key = "extruder"
        motor_run_time = 4
        if klipper_state and fixture_state:
            try:
                if self.dev_dicts[key] != []:
                    GlobalLogger.divider_head_log(key)
                    if self.dev_dicts[key][0] == "":
                        self.dev_dicts[key][0] = key

                    #  Positive motor rotation
                    self.dev.run_monitoring(key, self.fixture, True)
                    val_dict_1, dir_dict_1 = self.dev.req_encoder_info(
                        key, self.fixture, motor_run_time
                    )
                    self.dev.check_motor_distance(val_dict_1)

                    # motor reversal
                    self.dev.run_monitoring(key, self.fixture, False)
                    val_dict_2, dir_dict_2 = self.dev.req_encoder_info(
                        key, self.fixture, motor_run_time
                    )
                    self.dev.check_motor_distance(val_dict_2)

                    # Inspection Direction
                    self.check_motor_dir(dir_dict_1, dir_dict_2)
                    self.show_result(key)
            except TestFailureException as e:
                self._test_failture_exception(e, key)
            except TestReplyException as e:
                for item in self.dev_dicts[key]:
                    self.show_sigle_result(item, False, e.message)
        else:
            self._raise_connect_exception(klipper_state, fixture_state)
