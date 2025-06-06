import subprocess
from PyQt6.QtCore import Qt, QThread, pyqtSignal


def run_git_command(cmd):
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    output = result.stdout.strip()
    error = result.stderr.strip()
    # 合并输出和错误信息
    full_output = output + ("\n" + error if error else "")
    return full_output


class GitSyncThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool)
    log = pyqtSignal(str)  # 新增信号用于输出文本

    def restore_dirty_version(self):
        self.status.emit("分析仓库是否异常...")

        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if status_result.stdout.strip():
            self.status.emit("检测到本地有未提交的更改，正在还原...")
            restore_result = subprocess.run(
                ["git", "restore", "."],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if restore_result.returncode != 0:
                error_msg = f"还原失败: {restore_result.stderr.strip()}"
                self.status.emit(error_msg)
                self.log.emit(error_msg)
                self.finished.emit(False)
                return True

            self.log.emit("还原库成功，同步仓库中")

        return False

    def run(self):
        if not self.restore_dirty_version():
            self.status.emit("正在同步远程分支...")
            process = subprocess.Popen(
                ["git", "pull", "--progress"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            total_lines = 0
            lines = []
            for line in process.stdout:
                lines.append(line)
                self.log.emit(line.strip())
                total_lines += 1
                self.progress.emit(min(99, total_lines * 10))
            process.wait()
            if process.returncode == 0:
                self.status.emit("同步完成")
                self.progress.emit(100)
                commit_info = subprocess.check_output(
                    ["git", "log", "-1", "--pretty=format:%h %s [%an]"], text=True
                ).strip()
                self.log.emit(f"最新提交: {commit_info}")
                self.finished.emit(True)
            else:
                self.status.emit("同步失败")
                self.finished.emit(False)
