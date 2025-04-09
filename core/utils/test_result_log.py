"""
@File    :   log.py
@Time    :   2025/04/03
@Desc    :   Record information about the results of the test
"""

import os
import json
from datetime import datetime


class TestResultLog:
    def __init__(self):
        # Initialising the log directory
        self.log_dir = os.path.join(os.getcwd(), "log")
        # Initialising the datastore
        self.data = {}
        self.test_result = True

    def add_log_entry(self, key, col1, col2, col3, col4):
        if col1 == "False":
            self.test_result = False

        # If the key is not in the data dictionary, it is initialised to an empty list
        if str(key) not in self.data:
            self.data[str(key)] = []

        # Add a row of data to the list corresponding to the key
        self.data[str(key)].append(
            {"result": col1, "type": col2, "name": col3, "bak": col4}
        )

    def save_logs(self):
        # Get the current date in YYYY-MM-DD format.
        current_date = datetime.now().strftime("%Y-%m-%d")
        date_dir = os.path.join(self.log_dir, current_date)

        # If the date catalogue does not exist, create
        if not os.path.exists(date_dir):
            os.makedirs(date_dir)

        # Iterate over each key and write the data to a JSON file named key_col1
        for key, entries in self.data.items():
            if entries:  # 确保列表不为空
                file_name = f"{self.test_result}_{key}.json"
                file_path = os.path.join(date_dir, file_name)
                with open(file_path, "w", encoding="utf-8") as json_file:
                    json.dump(entries, json_file, ensure_ascii=False, indent=4)

                print(f"Logs for ID {key} saved to {file_path}")

        self.test_result = True
        self.data.clear()
