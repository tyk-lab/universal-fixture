import configparser
import re


def parse_flash_info(file_path):
    # 创建一个 ConfigParser 对象
    config = configparser.ConfigParser()

    # 打开文件并读取内容
    with open(file_path, "r") as file:
        # 读取所有行
        lines = file.readlines()

    # 提取 [test_info] 部分
    in_test_info = False
    test_info_lines = []
    for line in lines:
        # 去掉每行开头的 "## " 注释
        line = re.sub(r"^##\s*", "", line).strip()

        # 检查是否进入 [test_info] 部分
        if line.startswith("[test_info]"):
            in_test_info = True
            test_info_lines.append(line)
            continue

        # 检查是否离开 [test_info] 部分
        if in_test_info and line.startswith("[") and not line.startswith("[test_info]"):
            break

        # 如果在 [test_info] 部分，添加行
        if in_test_info:
            test_info_lines.append(line)

    # 将 [test_info] 部分的内容加入到 ConfigParser 中
    config.read_string("\n".join(test_info_lines))

    # 获取解析后的值
    test_info = config["test_info"]
    board = test_info.get("boart")
    mcu = test_info.get("mcu")
    file_suffix = test_info.get("file_suffix")

    return board, mcu, file_suffix


# 示例调用(debug)
# board, mcu, file_suffix = parse_flash_info(
#     "/home/test/Test/core/utils/klipper_printer.cfg"
# )
# print(f"Board: {board}")
# print(f"MCU: {mcu}")
# print(f"File Suffix: {file_suffix}")
