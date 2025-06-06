from PyQt6.QtCore import QThread, pyqtSignal


class FirmwareUpdateThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    log = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, updater, repo_url, tag="test", extract_to="."):
        super().__init__()
        self.updater = updater
        self.repo_url = repo_url
        self.tag = tag
        self.extract_to = extract_to

    def run(self):
        self.status.emit("开始下载固件...")
        try:
            # 这里没有真实进度，只能模拟
            ok= self.updater.download_and_extract_release_zip(
                self.repo_url, self.tag, "release.zip", self.extract_to, self.log
            )
            if ok:
                self.progress.emit(100)
                self.status.emit("固件下载并解压完成")
                self.finished.emit(True)
            else:
                self.progress.emit(0)
                self.status.emit("固件下载失败")
                self.finished.emit(False)
        except Exception as e:
            self.status.emit(f"异常: {e}")
            self.log.emit(f"异常: {e}")
            self.finished.emit(False)