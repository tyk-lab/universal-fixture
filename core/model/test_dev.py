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

        # 存储对应类型的设备所在的行号
        self.tabal_index = {}

        self.dev = DevInfo(klipper, self.dev_dicts)

    def set_update_callback(self, add_row_callback, modify_row_callback):
        self.add_row_callback = add_row_callback
        self.modify_row_callback = modify_row_callback

    def init_model(self):
        self.dev_dicts = self.dev.get_dev_names()

        # print(self.dev_dicts)
        i = 0
        for key, value in self.dev_dicts.items():
            index_list = []
            for name in value:
                raw_data = [
                    "",  # result
                    key,  # type
                    name,  # name
                    "",  # log
                ]
                index_list.append(i)
                i += 1
                self.add_row_callback(raw_data, QColor("white"), False)
            self.tabal_index[key] = index_list

    # todo
    def test_btn(self):
        # todo，控制万能板输出(每个指令必须有回复)
        # todo,命令开始前，判断下两边的状态
        key = "gcode_button "
        result_dict = self.dev.get_btn_state()
        match_index_list = self.tabal_index[key]

        print(result_dict)
        i = 0
        # 遍历所有设备，更新结果
        for item in self.dev_dicts[key]:
            result = result_dict[item]
            color = GlobalComm.err_color
            if result:
                color = GlobalComm.ok_color
            raw_data = [
                result,  # todo, result 可能要转为文字
                key,  # type
                item,  # name
                "",  # log
            ]
            self.modify_row_callback(match_index_list[i], raw_data, color)
            i += 1
