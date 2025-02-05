import os
import json
from datetime import datetime


class Log:
    def __init__(self):
        # 初始化日志目录
        self.log_dir = os.path.join(os.getcwd(), "log")
        # 初始化数据存储
        self.data = {}
        self.test_result = True

    def add_log_entry(self, key, col1, col2, col3, col4):
        if col1 == "False":
            self.test_result = False

        # 如果 key 不在数据字典中，则初始化为一个空列表
        if str(key) not in self.data:
            self.data[str(key)] = []

        # 添加一行数据到对应 key 的列表中
        self.data[str(key)].append(
            {"result": col1, "type": col2, "name": col3, "bak": col4}
        )

    def save_logs(self):
        # 获取当前日期，格式为 YYYY-MM-DD
        current_date = datetime.now().strftime("%Y-%m-%d")
        date_dir = os.path.join(self.log_dir, current_date)

        # 如果日期目录不存在，则创建
        if not os.path.exists(date_dir):
            os.makedirs(date_dir)

        # 遍历每个 key，将数据写入以 key_col1 命名的 JSON 文件
        for key, entries in self.data.items():
            if entries:  # 确保列表不为空
                file_name = f"{self.test_result}_{key}.json"
                file_path = os.path.join(date_dir, file_name)
                with open(file_path, "w", encoding="utf-8") as json_file:
                    json.dump(entries, json_file, ensure_ascii=False, indent=4)

                print(f"Logs for ID {key} saved to {file_path}")

        self.test_result = True
        self.data.clear()
