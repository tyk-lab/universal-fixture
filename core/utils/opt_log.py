"""
@File    :   opt_log.py
@Time    :   2025/04/03
@Desc    :   Global logging of related operations
"""

import os
from datetime import datetime


class GlobalLogger:
    # class variable
    log_file_path = None
    DEBUG_MODE = True

    @classmethod
    def initialize(cls):
        # 初Initialising the log directory
        log_dir = os.path.join(os.getcwd(), "log")
        # Get the current date in YYYY-MM-DD format.
        current_date = datetime.now().strftime("%Y-%m-%d")
        # Creating a date catalogue
        date_dir = os.path.join(log_dir, current_date)
        if not os.path.exists(date_dir):
            os.makedirs(date_dir)
        # Setting the log file path
        cls.log_file_path = os.path.join(date_dir, "test_opt.log")

    @classmethod
    def log(cls, message, *args, **kwargs):
        # Ensure that the log file path is initialised
        if cls.log_file_path is None:
            cls.initialize()

        # Message append to log file
        current_time = datetime.now().time().strftime("%H:%M:%S")
        with open(cls.log_file_path, "a", encoding="utf-8") as log_file:
            print(f"{current_time}:", message, *args, **kwargs, file=log_file)

    @classmethod
    def debug_print(*args, **kwargs):
        """
        The built-in print is called when DEBUG_MODE is True, otherwise no action is performed.
        """
        if GlobalLogger.DEBUG_MODE:
            print(*args, **kwargs)

    @classmethod
    def divider_head_log(cls, title):
        cls.log(f"\r\n########################### {title} ############################")
