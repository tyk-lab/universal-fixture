import os
from datetime import datetime


class GlobalLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GlobalLogger, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # 初始化日志目录
        self.log_dir = os.path.join(os.getcwd(), "log")
        # 获取当前日期，格式为 YYYY-MM-DD
        current_date = datetime.now().strftime("%Y-%m-%d")
        # 创建日期目录
        self.date_dir = os.path.join(self.log_dir, current_date)
        if not os.path.exists(self.date_dir):
            os.makedirs(self.date_dir)
        # 设置日志文件路径
        self.log_file_path = os.path.join(self.date_dir, "test_opt.log")

    def log(self, message):
        # 将消息追加写入日志文件
        with open(self.log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(message + "\n")
        print(f"Logged: {message}")


# 示例使用
logger = GlobalLogger()
logger.log("This is a test log message.")
logger.log("Another log entry.")
