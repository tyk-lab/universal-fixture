import os
import sys
import locale

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

from core.model.usb_flash import UsbFlash
from core.utils.msg import CustomDialog
from core.utils.common import GlobalComm
from core.utils.parse import parse_cfg_flash_info


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.loading_cfg()
        self.load_current_languag()

        self.setWindowTitle(GlobalComm.get_langdic_val("view", "main_title"))
        self.resize(800, 800)

        self.menu_init()
        self.central_init()

    ##################### view init #######################
    def menu_init(self):
        menu_bar = self.menuBar()

        # 文件菜单页 #
        file_menu = menu_bar.addMenu(GlobalComm.get_langdic_val("view", "file_menu"))

        # 退出应用子页
        action = QAction(GlobalComm.get_langdic_val("view", "file_menu_exit"), self)
        action.triggered.connect(MainWindow.on_exit_app)
        file_menu.addAction(action)

        # 设置页 #
        set_menu = menu_bar.addMenu(GlobalComm.get_langdic_val("view", "set_menu"))

        # 语言转换子页
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

        # 模式菜单子页
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

        # 连接信号到槽函数
        self.action_fixture.triggered.connect(self.on_action_toggled)
        self.action_fixture.setChecked(True)
        self.action_comm.triggered.connect(self.on_action_toggled)
        self.action_sigle.triggered.connect(self.on_action_toggled)

        # 将菜单项添加到模式菜单
        mode_menu.addAction(self.action_fixture)
        mode_menu.addAction(self.action_comm)
        mode_menu.addAction(self.action_sigle)

        # 关于页 #
        about_action = QAction(GlobalComm.get_langdic_val("view", "about"), self)
        about_action.triggered.connect(self.on_show_about)
        menu_bar.addAction(about_action)

    def central_init(self):
        # 创建主部件和布局
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)

        # 第一行：选择文件按钮和不可编辑的文本框
        file_layout = QHBoxLayout()
        open_button = QPushButton(GlobalComm.get_langdic_val("view", "btn_open"))
        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)
        file_layout.addWidget(open_button)
        file_layout.addWidget(self.file_edit)

        open_button.clicked.connect(self.on_open_file)

        # 第二行：烧录按钮和测试按钮
        action_layout = QHBoxLayout()
        burn_button = QPushButton(GlobalComm.get_langdic_val("view", "btn_burn"))
        test_button = QPushButton(GlobalComm.get_langdic_val("view", "btn_test"))
        action_layout.addWidget(burn_button)
        action_layout.addWidget(test_button)

        burn_button.clicked.connect(self.on_upload_firmware)

        # 第三行及以下：消息框
        self.message_box = QTextEdit()
        self.message_box.setReadOnly(True)

        # 将布局添加到主布局中
        main_layout.addLayout(file_layout)
        main_layout.addLayout(action_layout)
        main_layout.addWidget(self.message_box)

        # 设置主部件
        self.setCentralWidget(main_widget)

        # 初始化其他要素
        self.dialog = CustomDialog(main_widget)
        self.usb_flash = UsbFlash(self.message_box, self.dialog, main_widget)

    ##################### Function function #######################
    def update_language_ui(self):
        os.execl(sys.executable, sys.executable, *sys.argv)

    def loading_cfg(self):
        result = GlobalComm.load_json_cfg()
        if not result:
            MainWindow.on_exit_app()

    def load_current_languag(self):
        if GlobalComm.setting_json["language"] == "":
            lang, _ = locale.getdefaultlocale()
            if lang and lang.startswith("zh"):
                self.language = "zh"
            elif lang and lang.startswith("en"):
                self.language = "en"
            else:
                self.language = "en"  # 若是其他语言默认中文

            GlobalComm.set_cur_language(self.language)
        else:
            self.language = GlobalComm.setting_json["language"]

    def get_flash_info(self, file_name):
        # 获取文件所在目录
        directory = os.path.dirname(file_name)

        # 查找目录下的cfg文件
        cfg_files = [f for f in os.listdir(directory) if f.endswith(".cfg")]

        if cfg_files:
            self.cfg_file_path = os.path.join(directory, cfg_files[0])
            self.message_box.append(
                GlobalComm.get_langdic_val("view", "select_cfg_file")
                + f"{self.cfg_file_path}"
            )

            board, self.mcu, file_suffix = parse_cfg_flash_info(self.cfg_file_path)
            self.message_box.append(
                f"Board: {board}\t"
                + f"MCU: {self.mcu}\t"
                + f" File Suffix: {file_suffix}\r"
            )

            if GlobalComm.test_enable:
                print(f"Board: {board}\r")
                print(f"MCU: {self.mcu}\r")
                print(f"File Suffix: {file_suffix}\r")
        else:
            self.message_box.append(
                GlobalComm.get_langdic_val("error_tip", "err_cfg_file_not_found")
            )
            self.dialog.show_warning(
                GlobalComm.get_langdic_val("error_tip", "err_cfg_file_not_found")
            )

    ##################### event #######################
    def on_open_file(self):
        default_directory = "firmware"
        self.message_box.clear()

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            GlobalComm.get_langdic_val("view", "open_file"),
            default_directory,
            GlobalComm.setting_json["support_firmware"],
        )

        if file_name:
            self.file_edit.setText(file_name)
            self.message_box.append(
                GlobalComm.get_langdic_val("view", "select_file") + f"{file_name}"
            )
            self.get_flash_info(file_name)

    def on_upload_firmware(self):
        if self.file_edit.text() and self.mcu:
            self.usb_flash.exec(self.mcu, self.file_edit.text())
        else:
            self.dialog.show_warning(
                GlobalComm.get_langdic_val("error_tip", "err_not_select_file")
            )

    def on_action_toggled(self, checked):
        # 获取触发信号的 QAction
        action = self.sender()
        if checked:
            # 取消其他 QAction 的选中状态
            if action is not self.action_fixture:
                self.action_fixture.setChecked(False)
            if action is not self.action_comm:
                self.action_comm.setChecked(False)
            if action is not self.action_sigle:
                self.action_sigle.setChecked(False)

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
