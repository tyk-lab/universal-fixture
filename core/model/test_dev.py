from core.utils.common import GlobalComm
from core.model.dev_info import DevInfo
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QColor


class DevTest:
    def __init__(self, klipper):
        # 类型下的设备表
        self.dev_dicts = {
            "gcode_button ": [],
            "fan_generic ": [],
            "temperature_sensor ": [],
            "output_pin ": [],
            "manual_stepper ": [],
        }

        self.klipper = klipper
        self.dev = DevInfo(klipper, self.dev_dicts)

    def set_update_callback(self, add_row_callback, modify_row_callback):
        self.add_row_callback = add_row_callback
        self.modify_row_callback = modify_row_callback

    def init_model(self):
        self.dev_dicts = self.dev.get_dev_names()

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
            self.add_row_callback(raw_data, color)
            i += 1

    def _raise_connect_exception(self, klipper_state, fixture_state):
        raise Exception(
            GlobalComm.get_langdic_val("exception_tip", "excep_connect")
            + ": klipper state "
            + str(klipper_state)
            + "\r\n",
            "fixture state ",
            +str(fixture_state),
        )

    def _test_exception(self, e, key):
        result_dict = e.args[0]  # 从异常中获取列表
        log_dict = e.args[1]
        self.show_result(key, log_dict, result_dict)

    def test_btn(self):
        # todo,命令开始前，判断下两边的状态
        klipper_state = self.klipper.is_connect(False)
        key = "gcode_button "

        if klipper_state:
            try:
                if self.dev_dicts[key] != []:
                    # todo，控制万能板输出(每个指令必须有回复)
                    self.dev.check_btn_state(True)

                    # todo，控制万能板关闭(每个指令必须有回复)
                    self.dev.check_btn_state(False)

                    self.show_result(key)
                    return
            except Exception as e:
                self._test_exception(e, key)
        else:
            # todo,更新治具状态
            self._raise_connect_exception(klipper_state, False)

    def test_th(self):
        # todo,命令开始前，判断下两边的状态
        klipper_state = self.klipper.is_connect(False)
        key = "temperature_sensor "

        if klipper_state:
            try:
                if self.dev_dicts[key] != []:
                    # todo，获取万能板温感值
                    fixture_th = 23
                    self.dev.check_th_state(fixture_th)
                    self.show_result(key)
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
                    fixture_dict = {"fan0": 0.0, "fan1": 0.0}
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
