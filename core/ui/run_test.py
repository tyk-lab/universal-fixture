from PyQt6.QtWidgets import (
    QApplication,
    QPushButton,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QTableView,
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt6.QtCore import Qt

from core.model.test_dev import DevTest
from core.ui.table import CustomTableView
from core.model.klipperpy import KlipperService
from core.utils.common import GlobalComm
from core.model.printer_cfg import PrinterConfig
import threading
import subprocess
import os


class TestRun(QWidget):
    def __init__(self, cfg_path):
        super().__init__()

        self.klipper = KlipperService()
        self.config = PrinterConfig()
        self.dev_test = DevTest(self.klipper)
        self.dev_test.set_update_callback(
            self.make_line_data, self.delete_and_insert_line
        )

        self.last_result = ""
        self.cfg_path = cfg_path
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(GlobalComm.get_langdic_val("view", "test_tile"))

        # 创建垂直布局
        layout = QVBoxLayout()
        button = QPushButton(GlobalComm.get_langdic_val("view", "test_btn"))
        button.clicked.connect(self.on_init_test_data)
        layout.addWidget(button)

        # 创建数据表格
        table_view = CustomTableView()
        layout.addWidget(table_view)

        # 设置数据模型
        self.model = QStandardItemModel(0, 4)  # 初始行数为0，列数为4
        self.model.setHorizontalHeaderLabels(
            [
                GlobalComm.get_langdic_val("view", "test_table_col1"),
                GlobalComm.get_langdic_val("view", "test_table_col2"),
                GlobalComm.get_langdic_val("view", "test_table_col3"),
                GlobalComm.get_langdic_val("view", "test_table_col4"),
            ]
        )

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

    def update_cfg(self, is_fixture):
        self.config.set_cfg_mode(is_fixture)

        self.result = self.config.get_serial_paths()
        if self.result is False:
            self.klipper_connect_result(
                GlobalComm.get_langdic_val("error_tip", "err_comm_no_device")
            )
            return False

        # 避免重复写文件
        if self.last_result != self.result:
            print("update cfg file")
            config_text = self.config.generate_config(self.result, self.cfg_path)
            if is_fixture:
                self.config.cp_cfg_printer_dir(self.cfg_path)

            self.config.write_config_to_file(config_text)

        # todo, 等完整连接
        # self.klipper.reset_printer()
        self.last_result = self.result
        return True

    ##################### Function function #######################
    def fixture_test(self):
        # todo, 第一次进入，需要确认是否有完整的连接，避免上次的残留信息影响
        if self.update_cfg(True):
            self.dev_test.init_model()
            self.dev_test.test_btn()

    # todo, 优化发送reset klipper还是firmware reset, 提高检查效率
    def comm_test(self):
        if self.update_cfg(False):
            self.comm_start_timer(12, self.klipper_connect_result)

    def klipper_connect_result(self, err=""):
        web_state = self.klipper.get_connect_info()
        state = web_state["state"]
        info_type = GlobalComm.get_langdic_val("view", "test_dev_type")

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
            self.make_line_data(raw_data, color=GlobalComm.err_color)
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
        self.make_line_data(raw_data, color=GlobalComm.ok_color)
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

    def comm_start_timer(self, init_time, fun):
        count = 0

        def run_task():
            nonlocal count
            count += 1
            is_connect = self.klipper.is_connect()
            if not is_connect and count <= init_time:
                threading.Timer(1, run_task).start()
                return
            else:
                fun()

        # first run
        run_task()

    ##################### event #######################
    def on_init_test_data(self):
        test_mode = GlobalComm.setting_json["cur_test_mode"]
        mode_list = GlobalComm.setting_json["test_mode"]

        # 跟setting标识一致
        action_list = {
            mode_list["fixture"]: self.fixture_test,
            mode_list["comm"]: self.comm_test,
        }
        action_list[test_mode]()
