"""
@File    :   run_test.py
@Time    :   2025/04/03
@Desc    :   test interface
"""

import webbrowser
import subprocess
import traceback

from PyQt6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTableView,
    QLineEdit,
    QLabel,
    QHBoxLayout,
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
import serial

from core.model.fixture_info import FixtureInfo
from core.utils.opt_log import GlobalLogger
from core.utils.test_result_log import TestResultLog
from core.ui.timer_dialog import TimerDialog
from core.utils.common import GlobalComm
from core.utils.custom_dialog import CustomDialog
from core.utils.test_thread import TestThread
from core.ui.loading import LoadingPanel
from core.model.test_dev import DevTest
from core.ui.table import CustomTableView
from core.model.klipperpy import KlipperService
from core.model.printer_cfg import PrinterConfig
from core.utils.parse_cfg_file import check_config_field


class TestRun(QWidget):
    start_timer_dialog_signal = pyqtSignal()

    def __init__(self, cfg_path, power_path, port_path):
        super().__init__()
        self.init_data(cfg_path, power_path, port_path)
        self.init_ui()

        self.start_timer_dialog_signal.connect(self.show_timer_dialog_test)

    # Associated with the timerDialog class.
    def show_timer_dialog_test(self):
        self.time_check_dialog.setModal(True)
        self.time_check_dialog.show()

    ##################### view init #######################
    def init_data(self, cfg_path, power_path, port_path):
        # Creating objects necessary for testing
        self.klipper = KlipperService()
        self.config = PrinterConfig()
        self.port_path = port_path
        self.fixture = FixtureInfo(
            self.port_path, GlobalComm.setting_json["fixture_serial"]
        )
        self.dev_test = DevTest(self.klipper, self.fixture)
        self.dev_test.set_update_callback(
            self.make_line_data, self.delete_and_insert_line
        )
        self.creat_timer_test()

        # Initialise some data bodies
        self.dialog = CustomDialog(self)
        self.last_result = ""
        self.cfg_path = cfg_path
        self.power_path = power_path
        self.loading_git = LoadingPanel(self)

        # Maps the corresponding test mode and gets the currently selected test mode.
        mode_list = GlobalComm.setting_json["test_mode"]
        self.action_list = {
            mode_list["fixture"]: self.fixture_test,
            mode_list["comm"]: self.comm_test,
            mode_list["sigle"]: self.sigle_test,
            mode_list["power"]: self.power_test,
        }

        #! Check if the target field exists in the configuration file
        # Used to filter the modules that must be tested during testing
        key = "adxl345"
        self.fields_to_check = {
            "adxl345": False,
        }
        self.fields_to_check[key] = check_config_field(self.cfg_path, key)

    def init_ui(self):
        self.setWindowTitle(GlobalComm.get_langdic_val("view", "test_tile"))

        # Creating a Vertical Layout
        layout = QVBoxLayout()
        button = QPushButton(GlobalComm.get_langdic_val("view", "test_btn"))
        button.clicked.connect(self.on_init_test_map)
        layout.addWidget(button)

        # Create and add tags
        h_layout = QHBoxLayout()
        label = QLabel("serial id: ")
        h_layout.addWidget(label)

        # Creating and adding text edit boxes
        self.line_edit = QLineEdit()
        h_layout.addWidget(self.line_edit)

        layout.addLayout(h_layout)

        # Create a data table where the test information is stored.
        table_view = CustomTableView()
        layout.addWidget(table_view)

        # Setting up the data model
        self.table_model = QStandardItemModel(
            0, 4
        )  # Initial number of rows is 0, number of columns is 4
        self.reset_table()

        # Setting the model to table view
        table_view.setModel(self.table_model)
        table_view.setSelectionMode(
            QTableView.SelectionMode.SingleSelection
        )  # radio mode
        table_view.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectItems
        )  # Selecting Cells

        # Setting the last column to auto-fill
        header = table_view.horizontalHeader()
        header.setStretchLastSection(True)

        # Application Layout
        self.setLayout(layout)

    ##################### Function function #######################
    def update_product_cfg(self, is_combined_file, file_path):
        """Update the klipper configuration file for the corresponding product.

        Args:
            is_combined_file (bool): Whether or not to use [include] to bring in test files
            file_path (string): Corresponding configuration file

        Returns:
            bool: Success/Failure
        """
        self.config.set_cfg_mode(is_combined_file)

        # Determine if the device exists, pop-up warning if it doesn't exist
        result = self.config.get_serial_paths()
        if result is False or result == []:
            self.klipper_connect_task(
                GlobalComm.get_langdic_val("error_tip", "err_comm_no_device")
            )
            self.dialog.show_warning(
                GlobalComm.get_langdic_val("error_tip", "err_comm_no_device")
            )
            return False

        # Updating profile information
        if self.last_result != result:
            GlobalLogger.debug_print("update cfg file")
            self.line_edit.setText(", ".join(result))
            config_text = self.config.generate_config(result, file_path)
            if is_combined_file:
                self.config.cp_cfg_printer_dir(file_path)
            self.config.write_config_to_file(config_text)

        # restart klipper
        self.klipper.reset_printer()
        self.last_result = result
        return True

    def reset_table(self):
        self.table_model.clear()
        self.table_model.setHorizontalHeaderLabels(
            [
                GlobalComm.get_langdic_val("view", "test_table_col1"),
                GlobalComm.get_langdic_val("view", "test_table_col2"),
                GlobalComm.get_langdic_val("view", "test_table_col3"),
                GlobalComm.get_langdic_val("view", "test_table_col4"),
            ]
        )

    def make_line_data(self, row_data, background, head_insert=True):
        items = []
        for value in row_data:
            item = QStandardItem(str(value))
            # Setting non-editable
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            item.setBackground(background)
            items.append(item)

        if head_insert:
            self.table_model.insertRow(0, items)
            return
        self.table_model.appendRow(items)

    def delete_and_insert_line(self, row, new_items, background):
        # Check if the line number is in range
        if 0 <= row < self.table_model.rowCount():
            # Deletes the specified line
            self.table_model.removeRow(row)
            # Insert new data in the same place
            items = []
            for value in new_items:
                item = QStandardItem(str(value))
                # Setting non-editable
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                item.setBackground(background)
                items.append(item)
            self.table_model.insertRow(row, items)
        else:
            GlobalLogger.debug_print("Line number out of range")

    def klipper_connect_task(self, err=""):
        """The results of the communication tests show that

        Args:
            err (str, optional): Feedback error messages. Defaults to "".

        Returns:
            _type_: _description_
        """
        web_state = self.klipper.get_connect_info()
        state = web_state["state"]
        info_type = GlobalComm.get_langdic_val("view", "test_dev_type")
        GlobalLogger.log("connect test result")

        # Unusually Unconnected
        if err != "" or state != "ready":
            result = subprocess.run(
                ["lsusb"], capture_output=True, text=True, check=True
            )
            result = result.stdout.replace("\n", "\r\n")

            GlobalLogger.log(result)

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
        GlobalLogger.log(serial_id)
        GlobalLogger.log("connect Successful")
        GlobalLogger.debug_print("connect Successful", serial_id)
        log = web_state["state_message"] + "    " + "\r\n"
        raw_data = [
            GlobalComm.get_langdic_val("view", "test_result_ok"),
            info_type,
            serial_id,
            log,
        ]
        self.make_line_data(raw_data, GlobalComm.ok_color)
        return True

    def open_web_control(self):
        url = GlobalComm.setting_json["klipper_web"]
        webbrowser.open(url, new=2)

    def show(self):
        """Jump processing according to the current test pattern

        Returns:
            _type_: _description_
        """
        test_mode = GlobalComm.setting_json["cur_test_mode"]
        if test_mode == "power" or test_mode == "sigle":
            self.action_list[test_mode]()
        else:
            return super().show()

    ##################### event(The function name of the event with on_) #######################

    def on_init_test_map(self):
        self.time_check_dialog = TimerDialog()
        self.time_check_dialog.set_save_fun(self.save_test_result)

        test_mode = GlobalComm.setting_json["cur_test_mode"]
        self.action_list[test_mode]()

    def creat_timer_test(self, timer_fun=None):
        self.count = 0
        self.init_time = 12
        self.conn_poll_timer = QTimer()
        # Binding polled functions
        self.conn_poll_timer.timeout.connect(lambda: self.timer_run_task(timer_fun))

    def timer_run_task(self, fun):
        """Poll the klipper regularly to see if it is connected,
            and perform the relevant functions if it is connected.

        Args:
            fun (_type_): If fun exists, then the fun function is executed, otherwise the test thread is executed.
        """
        self.count += 1
        is_connect = self.klipper.is_connect()
        if not is_connect and self.count <= self.init_time:  # 1s loop
            self.conn_poll_timer.start(1000)
            return
        elif fun != None:
            self.count = 0
            fun()
            return
        else:  # Connect it, put it on the test thread and execute it.
            self.count = 0
            self.analysis_test_thread.start()
        self.conn_poll_timer.stop()

    def creat_test_thread(self, fun):
        self.analysis_test_thread = TestThread(fun)
        self.analysis_test_thread.bind_event(self.on_test_complete, self.on_test_err)

    def on_test_complete(self):
        self.loading_git.stop_gif()

    #! Arbitrary exceptions in the test are signalled and sent here to the
    def on_test_err(self, result, err):
        self.loading_git.stop_gif()
        GlobalLogger.log(err)
        self.dialog.show_warning(result + err)

    ##################### Related Tests #######################
    def fixture_test(self):
        self.reset_table()
        GlobalLogger.divider_head_log("fixture_test")

        if self.update_product_cfg(True, self.cfg_path):
            self.loading_git.init_loading_QFrame()
            self.loading_git.run_git()
            self.conn_poll_timer.start()  # Check if klipper is connected, callback test threads
            self.creat_test_thread(self.exec_fixture_test)

    def exec_fixture_test(self):
        self.fixture.init_fixture()
        self.dev_test.init_model()

        if self.fields_to_check["adxl345"] is True:
            self.dev_test.test_adxl345(
                self.time_check_dialog, self.start_timer_dialog_signal
            )

        # self.dev_test.test_rgbw()
        # self.dev_test.test_fan()
        self.dev_test.test_btn()
        self.dev_test.test_comm_th()
        self.dev_test.test_heat()
        # self.dev_test.test_motor()
        self.save_test_result()

    def save_test_result(self):
        log = TestResultLog()
        key = self.line_edit.text().split("/")[-1]

        rows_info = []
        for row in range(self.table_model.rowCount()):
            # Extracting data from each column
            col0 = self.table_model.item(row, 0).text()
            col1 = self.table_model.item(row, 1).text()
            col2 = self.table_model.item(row, 2).text()
            col3 = self.table_model.item(row, 3).text()

            rows_info.append([col0, col1, col2, col3])
            log.add_log_entry(key, col0, col1, col2, col3)

        GlobalLogger.log("\r\n ========= fixtrue test result  ========= \r\n")
        GlobalLogger.log(key)
        rows_info_str = "\r\n".join(" ".join(row) for row in rows_info)
        GlobalLogger.log(rows_info_str)
        log.save_logs()

    def comm_test(self):
        if self.update_product_cfg(False, self.cfg_path):

            GlobalLogger.divider_head_log("connect test")

            self.loading_git.init_loading_QFrame()
            self.loading_git.run_git()
            self.conn_poll_timer.start()
            self.creat_test_thread(self.klipper_connect_task)

    def sigle_test(self):
        if self.update_product_cfg(True, self.cfg_path):
            GlobalLogger.divider_head_log("sigle test")
            self.open_web_control()

    def power_test(self):
        if self.update_product_cfg(True, self.power_path):
            GlobalLogger.divider_head_log("power test")
            self.creat_timer_test(self.power_test_result)
            self.conn_poll_timer.start()
            self.open_web_control()

    def power_test_result(self):
        self.klipper.power_run()
