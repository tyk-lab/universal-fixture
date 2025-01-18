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

from core.ui.table import CustomTableView
from core.model.klipperpy import KlipperService
from core.utils.common import GlobalComm
from core.model.printer_cfg import PrinterConfig
import threading
import subprocess


class TestRun(QWidget):
    def __init__(self):
        super().__init__()

        self.klipper = KlipperService()
        self.config = PrinterConfig()
        self.last_result = ""

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
        self.model = QStandardItemModel(0, 3)  # 初始行数为0，列数为3
        self.model.setHorizontalHeaderLabels(
            [
                GlobalComm.get_langdic_val("view", "test_table_col1"),
                GlobalComm.get_langdic_val("view", "test_table_col2"),
                GlobalComm.get_langdic_val("view", "test_table_col3"),
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

    ##################### Function function #######################
    # todo
    def fixture_test(self):
        pass

    def comm_test(self):
        self.result = self.config.get_serial_paths()
        if self.result is False:
            self.klipper_connect_result(
                GlobalComm.get_langdic_val("error_tip", "err_comm_no_device")
            )
            return

        if self.last_result != self.result:
            config_text = self.config.generate_config(self.result)
            self.config.write_config_to_file(config_text)

        self.klipper.reset_printer()
        self.last_result = self.result
        self.comm_start_timer(self.klipper_connect_result)

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
                err + "\r\n" + str(result),
            ]
            self.make_line_data(raw_data, QColor("red"))
            return False

        serial_id = str(self.last_result).replace("[", "").replace("]", "")
        log = web_state["state_message"] + "    " + "\r\nid: " + serial_id
        raw_data = [
            GlobalComm.get_langdic_val("view", "test_result_ok"),
            info_type,
            log,
        ]
        self.make_line_data(raw_data, QColor("green"))
        return True

    def make_line_data(self, row_data, background):
        items = []
        for value in row_data:
            item = QStandardItem(str(value))
            # 设置不可编辑
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            item.setBackground(background)
            items.append(item)
        self.model.insertRow(0, items)

    def comm_start_timer(self, fun):
        count = 0

        def run_task():
            nonlocal count
            count += 1
            web_state = self.check()
            print(count)
            if not web_state and count <= 8:
                print("run")
                threading.Timer(1, self.check).start()
                return
            else:
                fun()

        # 启动第一次定时任务
        run_task()

    def check(self):
        try:
            web_state = self.klipper.get_connect_info()
            print(web_state)
            return web_state["state"] == "ready"
        except KeyError as e:
            return False
        except Exception as e:
            return False

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
