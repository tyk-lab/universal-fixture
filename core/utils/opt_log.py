import os
from datetime import datetime


class GlobalLogger:
    # 类变量，用于存储日志文件路径
    log_file_path = None

    @classmethod
    def initialize(cls):
        # 初始化日志目录
        log_dir = os.path.join(os.getcwd(), "log")
        # 获取当前日期，格式为 YYYY-MM-DD
        current_date = datetime.now().strftime("%Y-%m-%d")
        # 创建日期目录
        date_dir = os.path.join(log_dir, current_date)
        if not os.path.exists(date_dir):
            os.makedirs(date_dir)
        # 设置日志文件路径
        cls.log_file_path = os.path.join(date_dir, "test_opt.log")

    @classmethod
    def log(cls, message):
        # 确保日志文件路径已初始化
        if cls.log_file_path is None:
            cls.initialize()

        # 将消息追加写入日志文件
        with open(cls.log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(message + "\n")
        print(f"Logged: {message}")
