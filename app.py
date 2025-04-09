"""
@File    :   app.py
@Time    :   2025/04/03
@Desc    :   Define the main interface logic
"""

import os
import sys
import locale
import webbrowser

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QFileDialog,
    QLabel,
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from core.utils.opt_log import GlobalLogger
from core.ui.run_test import TestRun
from core.model.usb_flash import UsbFlash
from core.utils.custom_dialog import CustomDialog
from core.utils.common import GlobalComm
from core.utils.parse_cfg_file import parse_cfg_flash_info


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.loading_cfg()
        self.load_current_languag()

        self.setWindowTitle(GlobalComm.get_langdic_val("view", "main_title"))
        self.resize(800, 800)  # todo, 全屏或修改适配屏幕

        self.menu_init()
        self.central_init()

    ##################### view init #######################
    def menu_init(self):
        menu_bar = self.menuBar()

        ###########################
        # File menu page
        #############################
        file_menu = menu_bar.addMenu(GlobalComm.get_langdic_val("view", "file_menu"))

        # Exit the application sub-page
        action = QAction(GlobalComm.get_langdic_val("view", "file_menu_exit"), self)
        action.triggered.connect(MainWindow.on_exit_app)
        file_menu.addAction(action)

        ###########################
        # settings page
        #############################
        set_menu = menu_bar.addMenu(GlobalComm.get_langdic_val("view", "set_menu"))

        # Language Conversion Subpage
        language_menu = set_menu.addMenu(
            GlobalComm.get_langdic_val("view", "set_menu_language")
        )
        self.english_action = QAction(
            GlobalComm.get_langdic_val("view", "set_menu_language_en"),
            self,
            checkable=True,
        )
        self.english_action.setChecked(self.language == "en")
        self.english_action.triggered.connect(self.on_set_language_en)
        language_menu.addAction(self.english_action)

        self.chinese_action = QAction(
            GlobalComm.get_langdic_val("view", "set_menu_language_ch"),
            self,
            checkable=True,
        )
        self.chinese_action.setChecked(self.language == "zh")
        self.chinese_action.triggered.connect(self.on_set_language_zh)
        language_menu.addAction(self.chinese_action)

        # Mode menu sub-page
        mode_menu = set_menu.addMenu(GlobalComm.get_langdic_val("view", "menu_mode"))
        self.action_fixture = QAction(
            GlobalComm.get_langdic_val("view", "menu_mode_1"), self, checkable=True
        )
        self.action_comm = QAction(
            GlobalComm.get_langdic_val("view", "menu_mode_2"), self, checkable=True
        )
        self.action_sigle = QAction(
            GlobalComm.get_langdic_val("view", "menu_mode_3"), self, checkable=True
        )
        self.action_power = QAction(
            GlobalComm.get_langdic_val("view", "menu_mode_4"), self, checkable=True
        )

        # Connecting Signals to Slot Functions
        self.action_fixture.triggered.connect(self.on_mode_toggled)
        self.action_comm.triggered.connect(self.on_mode_toggled)
        self.action_sigle.triggered.connect(self.on_mode_toggled)
        self.action_power.triggered.connect(self.on_mode_toggled)

        mode_list = GlobalComm.setting_json["test_mode"]
        self.action_list = {
            mode_list["fixture"]: self.action_fixture,
            mode_list["comm"]: self.action_comm,
            mode_list["sigle"]: self.action_sigle,
            mode_list["power"]: self.action_power,
        }
        self.init_test_mode()

        # Adding menu items to the modal menu
        mode_menu.addAction(self.action_fixture)
        mode_menu.addAction(self.action_comm)
        mode_menu.addAction(self.action_sigle)
        mode_menu.addAction(self.action_power)

        ###########################
        #  About Page
        #############################
        about_action = QAction(GlobalComm.get_langdic_val("view", "about"), self)
        about_action.triggered.connect(self.on_show_about)
        menu_bar.addAction(about_action)

    def central_init(self):
        # Creating Master Parts and Layouts
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)

        # First line: select file button and non-editable text box
        file_layout = QHBoxLayout()
        open_button = QPushButton(GlobalComm.get_langdic_val("view", "btn_open"))
        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)
        file_layout.addWidget(open_button)
        file_layout.addWidget(self.file_edit)

        open_button.clicked.connect(self.on_open_file)

        # Second row: Burn button and Test button
        action_layout = QHBoxLayout()
        burn_button = QPushButton(GlobalComm.get_langdic_val("view", "btn_burn"))
        test_button = QPushButton(GlobalComm.get_langdic_val("view", "btn_test"))
        action_layout.addWidget(burn_button)
        action_layout.addWidget(test_button)

        burn_button.clicked.connect(self.on_upload_firmware)
        test_button.clicked.connect(self.on_test)

        # Third row and following: message box
        self.message_box = QTextEdit()
        self.message_box.setReadOnly(True)

        # Adding a layout to the main layout
        main_layout.addLayout(file_layout)
        main_layout.addLayout(action_layout)
        main_layout.addWidget(self.message_box)

        # Setting up the main part
        self.setCentralWidget(main_widget)

        ### Initialising other elements ###
        self.dialog = CustomDialog(main_widget)
        self.usb_flash = UsbFlash(self.message_box, self.dialog, main_widget)
        self.cfg_file_path = ""
        self.new_window = None

    ##################### Function function #######################
    def update_language_ui(self):
        os.execl(sys.executable, sys.executable, *sys.argv)

    def loading_cfg(self):
        result = GlobalComm.load_json_cfg()
        if not result:
            MainWindow.on_exit_app()

    def init_test_mode(self):
        cur = GlobalComm.setting_json["cur_test_mode"]
        for key, value in self.action_list.items():
            if cur == key:
                value.setChecked(True)
                GlobalComm.save_json_setting("cur_test_mode", key)
                return

        self.action_fixture.setChecked(True)
        GlobalComm.save_json_setting("cur_test_mode", "fixture")

    def load_current_languag(self):
        if GlobalComm.setting_json["language"] == "":
            lang, _ = locale.getdefaultlocale()
            if lang and lang.startswith("zh"):
                self.language = "zh"
            elif lang and lang.startswith("en"):
                self.language = "en"
            else:
                self.language = "en"  # Default Chinese for other languages

            GlobalComm.set_cur_language(self.language)
        else:
            self.language = GlobalComm.setting_json["language"]

    def load_required_files(self, target_file_name):
        """Get the necessary file information according to the path of the open file, including configuration file,
            port file, power file, etc.

        Args:
            target_file_name (_type_): Selected target file

        Raises:
            FileNotFoundCustomError: Relevant documents do not exist
        """
        from core.utils.exception.ex_file import FileNotFoundCustomError

        # Get the directory where the target file is located
        directory = os.path.dirname(target_file_name)

        self.power_cfg_path = None
        self.mcu_type = None

        try:
            # Find the cfg file in the directory
            cfg_files = [f for f in os.listdir(directory) if f.endswith(".cfg")]
            cfg_file = [f for f in cfg_files if "test" in f]
            if cfg_files == [] or cfg_file == []:
                raise FileNotFoundCustomError(directory)

            # Look for the port file in the directory
            port_file = [f for f in os.listdir(directory) if f.endswith(".json")]
            if port_file == []:
                raise FileNotFoundCustomError(directory)

            # Get Fixture Port File
            self.port_path = os.path.join(directory, port_file[0])
            print("port_path:", self.port_path)
            GlobalLogger.log("port file: " + f"{self.port_path}")
            self.message_box.append(
                GlobalComm.get_langdic_val("view", "select_cfg_file")
                + f"{self.port_path}"
            )

            # Obtaining Fixture Test Documents
            self.cfg_file_path = os.path.join(directory, cfg_file[0])
            print("cfg_file_path:", self.cfg_file_path)
            GlobalLogger.log("cfg file: " + f"{self.cfg_file_path}")
            self.message_box.append(
                GlobalComm.get_langdic_val("view", "select_cfg_file")
                + f"{self.cfg_file_path}"
            )

            # Getting the Power Test File
            self.power_cfg_path = ""
            power_test_file = GlobalComm.setting_json["power_test_file"]
            if power_test_file in cfg_files:
                self.power_cfg_path = os.path.join(directory, power_test_file)
            print("power_cfg_path:", self.power_cfg_path)

            # Extract the necessary burn-in information from the configuration file
            board, self.mcu_type, file_suffix = parse_cfg_flash_info(self.cfg_file_path)
            self.message_box.append(
                f"Board: {board}\t"
                + f"MCU: {self.mcu_type}\t"
                + f" File Suffix: {file_suffix}\r"
            )

            GlobalLogger.log(
                f"Board: {board}\t"
                + f"MCU: {self.mcu_type}\t"
                + f" File Suffix: {file_suffix}\r"
            )

            print(f"Board: {board}\r")
            print(f"MCU: {self.mcu_type}\r")
            print(f"File Suffix: {file_suffix}\r")

        except FileNotFoundCustomError as e:
            self.message_box.append(e.message)
            self.dialog.show_warning(e.message)

    ##################### event(The function name of the event with on_) #######################
    def on_open_file(self):
        default_directory = "firmware"

        target_file, _ = QFileDialog.getOpenFileName(
            self,
            GlobalComm.get_langdic_val("view", "open_file"),
            default_directory,
            GlobalComm.setting_json["support_firmware"],
        )

        GlobalLogger.log("\r\nselect file")

        if target_file:
            self.message_box.clear()

            # Selecting New Firmware closes the test screen
            if self.new_window != None:
                self.new_window.close()
            self.file_edit.setText(target_file)
            GlobalLogger.log("firmware file: " + f"{target_file}")
            self.message_box.append(
                GlobalComm.get_langdic_val("view", "select_file") + f"{target_file  }"
            )
            self.load_required_files(target_file)

    def on_upload_firmware(self):
        if self.file_edit.text() and self.mcu_type:
            self.usb_flash.exec(self.mcu_type, self.file_edit.text())
            GlobalLogger.log("\r\n flash file: " + self.file_edit.text())
        else:
            err_tip = GlobalComm.get_langdic_val("error_tip", "err_not_select_file")
            GlobalLogger.log("\r\n" + err_tip)
            self.dialog.show_warning(err_tip)

    def on_test(self):
        if self.cfg_file_path != "":
            # Restricted to open only once
            if self.new_window != None and self.new_window.isVisible():
                return

            self.new_window = TestRun(
                self.cfg_file_path, self.power_cfg_path, self.port_path
            )
            self.new_window.show()
            return

        # Prompts that no profile is selected
        GlobalLogger.log(
            "\r\n" + GlobalComm.get_langdic_val("error_tip", "err_not_select_cfg")
        )
        self.dialog.show_warning(
            GlobalComm.get_langdic_val("error_tip", "err_not_select_cfg")
        )

    def on_mode_toggled(self, checked):
        action = self.sender()
        for key, value in self.action_list.items():
            if action is value:
                value.setChecked(True)
                GlobalComm.save_json_setting("cur_test_mode", key)
                continue
            value.setChecked(False)

    def on_set_language_en(self):
        self.language = "en"
        self.chinese_action.setChecked(False)
        GlobalComm.save_json_setting(
            "language", self.language
        )  # Save the selected language
        self.update_language_ui()

    def on_set_language_zh(self):
        self.language = "zh"
        self.english_action.setChecked(False)
        GlobalComm.save_json_setting(
            "language", self.language
        )  # Save the selected language
        self.update_language_ui()

    def on_show_about(self):
        self.dialog.show_info(GlobalComm.get_langdic_val("view", "about_text"))

    @staticmethod
    def on_exit_app():
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
