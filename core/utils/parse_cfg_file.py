"""
@File    :   parse.py
@Time    :   2025/04/03
@Desc    :   Information about parsing klipper configuration files
"""

import configparser
import re


def parse_cfg_flash_info(file_path):
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Open the file and read the contents
    with open(file_path, "r") as file:
        # Read all rows
        lines = file.readlines()

    # Extract the [test_info] part
    in_test_info = False
    test_info_lines = []
    for line in lines:
        # Remove the "## " comment at the beginning of each line
        line = re.sub(r"^##\s*", "", line).strip()

        # Check if you have entered the [test_info] section
        if line.startswith("[test_info]"):
            in_test_info = True
            test_info_lines.append(line)
            continue

        # Check to leave the [test_info] section
        if in_test_info and line.startswith("[") and not line.startswith("[test_info]"):
            break

        # If in the [test_info] section, add the line
        if in_test_info:
            test_info_lines.append(line)

    # Add the contents of the [test_info] section to the ConfigParser
    config.read_string("\n".join(test_info_lines))

    # Get the parsed value
    test_info = config["test_info"]
    board = test_info.get("boart")
    mcu = test_info.get("mcu")
    file_suffix = test_info.get("file_suffix")
    burn_method = test_info.get("burn_method")

    return board, mcu, file_suffix, burn_method

    # Example call (debug)
    # board, mcu, file_suffix = parse_cfg_flash_info(
    #     "/home/test/Test/core/utils/klipper_printer.cfg"
    # )
    # print(f"Board: {board}")
    # print(f"MCU: {mcu}")
    # print(f"File Suffix: {file_suffix}")


#! Find out if the keyword information exists in the configuration file.
def check_config_field(config_path, fields_dict):
    if not isinstance(config_path, str) or not config_path:
        return False, False

    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            for key in fields_dict:
                if key in line:
                    fields_dict[key] = True
                    return True, True
    return False, True
