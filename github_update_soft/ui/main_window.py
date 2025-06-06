from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtCore import Qt
from updater import Updater


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("软件更新")
        self.setGeometry(100, 100, 400, 200)

        self.updater = Updater()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.check_updates_button = QPushButton("更新软件")
        self.check_updates_button.clicked.connect(self.check_for_updates)
        layout.addWidget(self.check_updates_button)

        self.firmware_update_button = QPushButton("更新配置和固件")
        self.firmware_update_button.clicked.connect(self.update_firmware)
        layout.addWidget(self.firmware_update_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_firmware(self):
        from utils.firmware_update import FirmwareUpdateThread
        from ui.updater_dialog import UpdaterDialog

        dlg = UpdaterDialog(self)
        dlg.update_status("准备下载固件...")
        dlg.progress_bar.setValue(0)

        repo_url = "https://gitee.com/tyk_123/save_fixture_firmware"  # 替换为你的仓库
        self.firmware_thread = FirmwareUpdateThread(self.updater, repo_url)
        self.firmware_thread.progress.connect(dlg.update_progress)
        self.firmware_thread.status.connect(dlg.update_status)
        self.firmware_thread.log.connect(dlg.append_log)

        def on_finished(ok):
            if ok:
                dlg.update_status("固件更新完成")
            else:
                dlg.update_status("固件更新失败")

        self.firmware_thread.finished.connect(on_finished)
        self.firmware_thread.start()
        dlg.exec()

    def check_for_updates(self):
        from ui.updater_dialog import UpdaterDialog
        from utils.git_sync import GitSyncThread

        if self.updater.is_update_available():
            dlg = UpdaterDialog(self)
            dlg.update_status("检测到新版本，正在同步...")
            dlg.progress_bar.setValue(0)
            self.sync_thread = GitSyncThread()
            self.sync_thread.progress.connect(dlg.update_progress)
            self.sync_thread.status.connect(dlg.update_status)
            self.sync_thread.log.connect(dlg.append_log)  # 连接日志信号

            def on_finished(ok):
                if ok:
                    dlg.update_status("同步完成")
                else:
                    dlg.update_status("同步失败")

            self.sync_thread.finished.connect(on_finished)
            self.sync_thread.start()
            dlg.exec()
        else:
            QMessageBox.information(
                self, "No Updates", "You are using the latest version."
            )
