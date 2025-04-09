"""
@File    :   test_dev.py
@Time    :   2025/04/03
@Desc    :   Define the device testing process and callback related results
"""

from core.model.json_protocol import FrameType
from core.utils.common import GlobalComm
from core.model.dev_info import DevInfo
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QColor
import traceback


class DevTest:
    def __init__(self, klipper, fixtrue):
        # 类型下的设备表
        self.dev_dicts = {
            "gcode_button ": [],
            "fan_generic ": [],
            "temperature_sensor ": [],
            "output_pin ": [],
            "heater_bed": [],
            "extruder": [],
            "neopixel ": [],
            # "adxl345": [],  # 这个直接读读不出数据
        }

        self.klipper = klipper
        self.fixtrue = fixtrue
        self.dev = DevInfo(klipper, self.dev_dicts)

    def set_update_callback(self, add_row_callback, modify_row_callback):
        self.add_row_callback = add_row_callback
        self.modify_row_callback = modify_row_callback

    def init_model(self):
        self.dev_dicts = self.dev.get_dev_info()

    def show_result(self, key, log_dict=None, result_dict=None):
        i = 0
        # 遍历对应的设备，更新结果
        result = True
        log = ""
        for item in self.dev_dicts[key]:
            if result_dict != None:
                result = result_dict[item]
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
        if result:
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
            TestFailureException,
        )

        raise TestConnectException(
            GlobalComm.get_langdic_val("exception_tip", "excep_connect")
            + ": klipper state "
            + str(klipper_state)
            + "\r\n",
            "fixture state " + str(fixture_state),
        )

    def _test_exception(self, e, key):

        result_dict = e.args[0]  # 从异常中获取列表
        log_dict = e.args[1]
        self.show_result(key, log_dict, result_dict)

    def test_btn(self):
        from core.utils.opt_log import GlobalLogger
        from core.utils.exception.ex_test import (
            TestConnectException,
            TestFailureException,
        )

        klipper_state = self.klipper.is_connect(False)
        fixture_state = self.fixtrue.is_connect(True)
        key = "gcode_button "

        if klipper_state and fixture_state:
            try:
                if self.dev_dicts[key] != []:
                    GlobalLogger.divider_head_log("test_btn")
                    self.fixtrue.sync_dev(FrameType.Sync)
                    self.fixtrue.send_command(FrameType.Opt, "btnSV", "1")
                    self.dev.check_btn_state(True)

                    self.fixtrue.send_command(FrameType.Opt, "btnSV", "0")
                    self.dev.check_btn_state(False)

                    self.show_result(key)
            except TestFailureException as e:
                self._test_exception(e, key)
            except Exception as e:
                print("发生异常: %s\n%s", str(e), traceback.format_exc())
        else:
            # todo,更新治具状态
            self._raise_connect_exception(klipper_state, fixture_state)

    def test_comm_th(self):
        # todo,命令开始前，判断下两边的状态
        klipper_state = self.klipper.is_connect(False)
        key = "temperature_sensor "

        if klipper_state:
            try:
                if self.dev_dicts[key] != []:
                    # todo，获取万能板温感值
                    fixture_th = 23
                    self.dev.check_th_state(fixture_th, key)
                    self.show_result(key)
                    return
            except Exception as e:
                self._test_exception(e, key)
        else:
            # todo,更新治具状态
            self._raise_connect_exception(klipper_state, False)

    def test_extruder_th(self):
        klipper_state = self.klipper.is_connect(False)
        key = "extruder"
        other_key = "heater_bed"

        if klipper_state:
            try:
                if self.dev_dicts[key] != []:
                    # todo，获取万能板温感值
                    fixture_th = 23
                    self.dev.check_th_state(fixture_th, key)
                    self.show_result(key)

                if self.dev_dicts[other_key] != []:
                    self.dev.check_th_state(fixture_th, other_key)
                    self.show_result(other_key)
                return
            except Exception as e:
                self._test_exception(e, key)
        else:
            # todo,更新治具状态
            self._raise_connect_exception(klipper_state, False)

    def test_fan(self):
        klipper_state = self.klipper.is_connect(False)
        key = "fan_generic "
        if klipper_state:
            try:
                if self.dev_dicts[key] != []:
                    # 让所有风扇旋转
                    set_val = "0.8"
                    self.dev.run_fan(set_val)
                    # # todo, 获取万能板中非三线的风速
                    # # 设返回的数据格式：{'fan2': 0.0, 'fan3': 0.0}
                    fixture_dict = {"PCF": 0.0, "HEF": 0.0}
                    self.dev.check_fan_state(set_val, fixture_dict)

                    set_val = "0.2"
                    self.dev.run_fan(set_val)
                    self.dev.check_fan_state(set_val, fixture_dict)

                    set_val = "0"
                    self.dev.run_fan(set_val)
                    self.dev.check_fan_state(set_val, fixture_dict)

                    self.show_result(key)
                    return
            except Exception as e:
                self._test_exception(e, key)
        else:
            # todo,更新治具状态
            self._raise_connect_exception(klipper_state, False)

    def test_rgbw(self):
        klipper_state = self.klipper.is_connect(False)
        key = "neopixel "

        if klipper_state:
            try:
                # todo,像lv这样外接小屏不受管控灯珠，怎么处理
                if self.dev_dicts[key] != []:
                    # 测试红色
                    # 返回的数据格式 {"rgb1": "0.0, 0.0, 0.1, 0.2"}
                    set_val = "red"
                    fixture_dict = {
                        #         r    g    b    w
                        "my_neopixel": "0.9, 0.0, 0.1, 0.2",
                        "fysetc_mini12864": "0.9, 0.0, 0.1, 0.2",
                    }
                    color_dict = self.dev.run_rgbw(set_val)
                    self.dev.check_rgbw_state(color_dict, fixture_dict)

                    # 测试蓝色
                    set_val = "blue"
                    color_dict = self.dev.run_rgbw(set_val)
                    self.dev.check_rgbw_state(color_dict, fixture_dict)

                    # 测试绿色
                    set_val = "green"
                    color_dict = self.dev.run_rgbw(set_val)
                    self.dev.check_rgbw_state(color_dict, fixture_dict)

                    # 测试白色
                    set_val = "white"
                    color_dict = self.dev.run_rgbw(set_val)
                    self.dev.check_rgbw_state(color_dict, fixture_dict)

                    self.show_result(key)
                    return
            except Exception as e:
                self._test_exception(e, key)
        else:
            # todo,更新治具状态
            self._raise_connect_exception(klipper_state, False)

    def test_adxl345(self, dialog, signal):
        klipper_state = self.klipper.is_connect(False)
        key = "adxl345"

        if klipper_state and self.dev_dicts[key] != []:
            cur = GlobalComm.setting_json["cur_test_cfg_file"]
            if self.klipper.get_info(key) != {}:
                dialog.set_title_name(key)
                dialog.set_check_fun(
                    self.dev.check_adxl345_state, self.show_sigle_result
                )
                signal.emit()

    def test_motor(self):
        klipper_state = self.klipper.is_connect(False)
        key = "extruder"

        if klipper_state:
            try:
                if self.dev_dicts[key] != []:
                    # todo, 通知万能板采集脉冲
                    self.dev.run_motor(True)
                    # todo, 获取万能板采集的脉冲
                    fixture_dict = {"a": 3000, "b": 3000}
                    self.dev.check_motor_distance(fixture_dict)

                    # todo, 通知万能板采集脉冲
                    self.dev.run_motor(False)
                    # todo, 获取万能板采集的脉冲
                    self.dev.check_motor_distance(fixture_dict)

                    self.show_result(key)
                    return
            except Exception as e:
                self._test_exception(e, key)
        else:
            # todo,更新治具状态
            self._raise_connect_exception(klipper_state, False)

    def test_heats(self):
        klipper_state = self.klipper.is_connect(False)
        key = "extruder"
        other_key = "heater_bed"

        if klipper_state:
            try:
                # todo
                if self.dev_dicts[key] != []:
                    # todo, 获取万能板的初始温度值
                    self.dev.run_heats(True)
                    fixture_dict = {
                        "a": 3000,
                        "b": 3000,
                    }  # todo, 区分同事有无两个key，看反馈
                    # todo，获取万能板当前温度值
                    self.dev.check_heats_state(fixture_dict)
                    self.show_result(key)

                if self.dev_dicts[other_key] != []:
                    self.dev.run_heats(False)
                    self.dev.check_heats_state(fixture_dict)
                    self.show_result(other_key)

                return
            except Exception as e:
                self._test_exception(e, key)
        else:
            # todo,更新治具状态
            self._raise_connect_exception(klipper_state, False)
