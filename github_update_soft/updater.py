import os
import re
import subprocess
import requests
import zipfile
import io


class Updater:

    def __init__(self, version_file="version", remote="origin"):
        self.version_file = version_file
        self.remote = remote
        self.current_version = self.get_current_version()

    def get_current_version(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        version_file_path = parent_dir + "/" + self.version_file
        print(version_file_path)
        if os.path.exists(version_file_path):
            with open(self.version_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        return "0.0.0"

    def get_latest_version(self, branch="master", file_path="version"):
        from utils.git_sync import run_git_command

        list = ["git", "show", f"{self.remote}/{branch}:{file_path}"]
        print(list)
        return run_git_command(["git", "show", f"{self.remote}/{branch}:{file_path}"])

    def is_update_available(self):
        from utils.version import Version

        latest_version = self.get_latest_version()
        print(latest_version, "----", self.current_version)
        return Version(latest_version) > Version(self.current_version)

    def is_dirty(self):
        from test_update.utils.git_sync import run_git_command

        status = run_git_command(["git", "status", "--porcelain"])
        return bool(status.strip())

    def restore_if_dirty(self):
        if self.is_dirty():
            run_git_command(["git", "restore", "."])

    def download_and_extract_release_zip(
        self, repo_url, tag, filename, extract_to=".", log=None, progress=None
    ):
        """
        :param repo_url: Warehouse address, e.g. https://github.com/yourusername/yourrepo
        :param tag: release tag name
        :param filename: release Uploaded zip file name
        :param extract_to: Unzip the catalogue
        """
        zip_url = f"{repo_url}/releases/download/{tag}/{filename}"
        local_zip = "test.zip"
        print(f"Downloading with curl: {zip_url}")
        log.emit(zip_url)
        try:

            # 使用curl下载，增加 --progress-bar 显示进度
            process = subprocess.Popen(
                ["curl", "-L", "--progress-bar", "-o", local_zip, zip_url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            # 处理进度条，避免百分比倒退
            for line in process.stderr:
                # curl --progress-bar 输出格式为：  45% [=======>             ]
                match = re.search(r"(\d+)%", line)
                if match:
                    if progress:
                        progress.emit(int(match.group(1)))

            # 判断失败的情况
            process.wait()
            if process.returncode != 0:
                err = f"curl download failed with code {process.returncode}"
                print(err)
                if log:
                    log.emit(err)
                return False

            # 解压前先删除 firmware 文件夹
            firmware_dir = os.path.join(extract_to, "firmware")
            if os.path.isdir(firmware_dir):
                import shutil

                shutil.rmtree(firmware_dir)

            # 解压
            with zipfile.ZipFile(local_zip, "r") as zf:
                # 兼容中文路径：用cp437解码再用gbk编码
                for info in zf.infolist():
                    try:
                        name = info.filename.encode("cp437").decode("gbk")
                    except Exception:
                        name = info.filename
                    target_path = os.path.join(extract_to, name)
                    if info.is_dir():
                        os.makedirs(target_path, exist_ok=True)
                    else:
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        with open(target_path, "wb") as f:
                            f.write(zf.read(info))
            print(
                f"Decompression is complete and the file has been saved to. {extract_to}"
            )
            if os.path.exists(local_zip):
                os.remove(local_zip)
            return True
        except Exception as e:
            err = f"An exception occurs during download or decompression. {e}"
            print(err)
            log.emit(err)
            return False
