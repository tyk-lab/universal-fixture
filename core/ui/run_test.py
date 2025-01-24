import webbrowser
from PyQt6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTableView,
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QTimer

from core.ui.timer_dialog import TimerDialog
from core.utils.common import GlobalComm
from core.utils.msg import CustomDialog
from core.utils.Test_thread import TestThread
from core.ui.loading import LoadingPanel
from core.model.test_dev import DevTest
from core.ui.table import CustomTableView
from core.model.klipperpy import KlipperService
from core.model.printer_cfg import PrinterConfig
import subprocess


class TestRun(QWidget):
    def __init__(self, cfg_path, power_path):
        super().__init__()
        self.init_data(cfg_path, power_path)
        self.init_ui()

    def init_data(self, cfg_path, power_path):
        # 创建测试必须的对象
        self.klipper = KlipperService()
        self.config = PrinterConfig()
        self.dev_test = DevTest(self.klipper)
        self.dev_test.set_update_callback(
            self.make_line_data, self.delete_and_insert_line
        )
        self.creat_timer_test()

        # 初始化一些数据体
        self.dialog = CustomDialog(self)
        self.last_result = ""
        self.cfg_path = cfg_path
        self.power_path = power_path
        self.loading_git = LoadingPanel(self)

        # 测试模式映射， 跟setting标识一致
        mode_list = GlobalComm.setting_json["test_mode"]
        self.action_list = {
            mode_list["fixture"]: self.fixture_test,
            mode_list["comm"]: self.comm_test,
            mode_list["sigle"]: self.sigle_test,
            mode_list["power"]: self.power_test,
        }

    def init_ui(self):
        self.setWindowTitle(GlobalComm.get_langdic_val("view", "test_tile"))

        # 创建垂直布局
        layout = QVBoxLayout()
        button = QPushButton(GlobalComm.get_langdic_val("view", "test_btn"))
        button.clicked.connect(self.on_init_test_map)
        layout.addWidget(button)

        # 创建数据表格
        table_view = CustomTableView()
        layout.addWidget(table_view)

        # 设置数据模型
        self.model = QStandardItemModel(0, 4)  # 初始行数为0，列数为4
        self.reset_model_ui()

        # 将模型设置到表格视图
        table_view.setModel(self.model)
        table_view.setSelectionMode(
            QTableView.SelectionMode.SingleSelection
        )  # 单选模式
        table_view.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectItems
        )  # 选择单元格

        # 设置最后一列自动填充
        header = table_view.horizontalHeader()
        header.setStretchLastSection(True)

        # 应用布局
        self.setLayout(layout)

    def update_cfg(self, is_composite_type, file_path):
        self.config.set_cfg_mode(is_composite_type)

        # 判断设备是否存在, 不存在弹窗警告
        self.result = self.config.get_serial_paths()
        if self.result is False:
            self.klipper_connect_result(
                GlobalComm.get_langdic_val("error_tip", "err_comm_no_device")
            )
            self.dialog.show_warning(
                GlobalComm.get_langdic_val("error_tip", "err_comm_no_device")
            )
            return False

        # 避免重复写文件
        if self.last_result != self.result:
            print("update cfg file")
            config_text = self.config.generate_config(self.result, file_path)
            if is_composite_type:
                self.config.cp_cfg_printer_dir(file_path)

            self.config.write_config_to_file(config_text)

        self.klipper.reset_printer()
        self.last_result = self.result
        return True

    def reset_model_ui(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(
            [
                GlobalComm.get_langdic_val("view", "test_table_col1"),
                GlobalComm.get_langdic_val("view", "test_table_col2"),
                GlobalComm.get_langdic_val("view", "test_table_col3"),
                GlobalComm.get_langdic_val("view", "test_table_col4"),
            ]
        )

    def on_test_complete(self):
        self.loading_git.stop_gif()
        self.timer.stop()

    # 测试中是否断连的报错，若报错则弹窗警告，并提示一些信息
    def on_test_err(self, result, err):
        self.loading_git.stop_gif()
        self.timer.stop()
        self.dialog.show_warning(result + err)

    def creat_timer_test(self, timer_fun=None):
        self.count = 0
        self.init_time = 12
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.timer_run_task(timer_fun))

    def creat_test_thread(self, fun):
        self.analysis_thread = TestThread(fun)
        self.analysis_thread.bind_event(self.on_test_complete, self.on_test_err)

    ##################### Function function #######################
    def fixture_test(self):
        self.reset_model_ui()

        if self.update_cfg(True, self.cfg_path):
            self.loading_git.init_loading_QFrame()
            self.loading_git.run_git()
            self.timer.start()
            self.creat_test_thread(self.fixture_test_result)

    def fixture_test_result(self):
        self.dev_test.init_model()
        self.dev_test.test_adxl345(self.time_dialog)
        # self.dev_test.test_rgbw()
        # self.dev_test.test_fan()
        # self.dev_test.test_btn()
        # self.dev_test.test_th()

    def comm_test(self):
        if self.update_cfg(False, self.cfg_path):
            self.loading_git.init_loading_QFrame()
            self.loading_git.run_git()
            self.timer.start()
            self.creat_test_thread(self.klipper_connect_result)

    def open_web_control(self):
        url = GlobalComm.setting_json["klipper_web"]
        webbrowser.open(url, new=2)

    def sigle_test(self):
        if self.update_cfg(True, self.cfg_path):
            self.open_web_control()

    def power_test(self):
        if self.update_cfg(True, self.power_path):
            self.creat_timer_test(self.power_test_result)
            self.timer.start()
            self.open_web_control()

    def power_test_result(self):
        self.klipper.power_run()

    def klipper_connect_result(self, err=""):
        web_state = self.klipper.get_connect_info()
        state = web_state["state"]
        info_type = GlobalComm.get_langdic_val("view", "test_dev_type")

        # 异常未连接
        if err != "" or state != "ready":
            result = subprocess.run(
                ["lsusb"], capture_output=True, text=True, check=True
            )
            result = result.stdout.replace("\n", "\r\n")

            if state != "ready":
                err = web_state["state_message"]

            raw_data = [
                GlobalComm.get_langdic_val("view", "test_result_err"),
                info_type,
                str(result),
                err + "\r\n",
            ]
            self.make_line_data(raw_data, GlobalComm.err_color)
            return False

        serial_id = "\n".join(self.last_result)
        print(serial_id)
        log = web_state["state_message"] + "    " + "\r\n"
        raw_data = [
            GlobalComm.get_langdic_val("view", "test_result_ok"),
            info_type,
            serial_id,
            log,
        ]
        self.make_line_data(raw_data, GlobalComm.ok_color)
        return True

    def make_line_data(self, row_data, background, head_insert=True):
        items = []
        for value in row_data:
            item = QStandardItem(str(value))
            # 设置不可编辑
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            item.setBackground(background)
            items.append(item)

        if head_insert:
            self.model.insertRow(0, items)
            return
        self.model.appendRow(items)

    def delete_and_insert_line(self, row, new_items, background):
        # 检查行号是否在范围内
        if 0 <= row < self.model.rowCount():
            # 删除指定行
            self.model.removeRow(row)
            # 在同一位置插入新数据
            items = []
            for value in new_items:
                item = QStandardItem(str(value))
                # 设置不可编辑
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                item.setBackground(background)
                items.append(item)
            self.model.insertRow(row, items)
        else:
            print("行号超出范围")

    ##################### event #######################
    def on_init_test_map(self):
        self.time_dialog = TimerDialog()

        test_mode = GlobalComm.setting_json["cur_test_mode"]
        self.action_list[test_mode]()

    def show(self):
        test_mode = GlobalComm.setting_json["cur_test_mode"]
        if test_mode == "power" or test_mode == "sigle":
            self.action_list[test_mode]()
        else:
            return super().show()

    def timer_run_task(self, fun):
        self.count += 1
        is_connect = self.klipper.is_connect()
        if not is_connect and self.count <= self.init_time:
            self.timer.start(1000)
            return
        elif fun != None:  # 连接上就执行
            fun()
        else:  # 连接上， 放置到线程上执行
            self.analysis_thread.start()
        self.timer.stop()
