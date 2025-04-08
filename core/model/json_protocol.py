"""
@File    :   json_transfer.py
@Time    :   2025/04/03
@Desc    :
            Framing Protocol Format
            startByte(1) + msgid(1) + dataSize(4) + data(n)
       eg:    0x5F            0x01      0x00000004   0x7B226E616D65223A202274657374222C202276616C7565223A202276616C7565227D
"""

import json
import struct

from enum import IntEnum

from core.utils.exception.ex_test import (
    TestFrameBeginException,
    TestFrameLengthException,
)


# Defining the frame type
class FrameType(IntEnum):
    Cfg = 0
    Opt = 1
    Request = 2
    Sync = 3
    Shucdown = 4


def build_key_json(port, dev_name, value=None):
    if value != None:
        return {"port": port, "name": dev_name, "value": str(value)}
    return {"port": port, "name": dev_name}


def receive_and_parse_frame(ser):
    from core.utils.msg import CustomDialog
    from core.utils.opt_log import GlobalLogger

    # 帧头定义
    FRAME_START = 0x5F
    HEADER_SIZE = 6  # startByte(1) + msgid(1) + dataSize(4)

    # 读取帧头
    header_data = ser.read(HEADER_SIZE)
    if len(header_data) == HEADER_SIZE:
        # 解析帧头
        start_byte, msgid, data_size = struct.unpack("<BBI", header_data)

        # GlobalLogger.debug_print("state data: ", start_byte, msgid, data_size)

        # 验证帧头
        if start_byte == FRAME_START:
            # 读取数据部分
            data = ser.read(data_size)
            # print(data)
            if len(data) == data_size:
                # 尝试解析为JSON
                json_data = json.loads(data.decode("utf-8"))
                GlobalLogger.debug_print("收到JSON数据：", json_data)
                GlobalLogger.log("send_command_and_format_result:" + str(json_data))
                return json_data
            else:
                raise TestFrameLengthException()
        else:
            raise TestFrameBeginException()


def send_json_frame(ser, infoId, payload):
    from core.utils.opt_log import GlobalLogger

    # 帧头定义
    FRAME_START = 0x5F
    MSGID = infoId

    # 将字典转为 JSON 字符串并编码
    json_str = json.dumps(payload, separators=(",", ":"))
    json_data = json_str.encode("utf-8")
    data_size = len(json_data)

    # 打包帧头
    frame_header = struct.pack("<BBI", FRAME_START, MSGID, data_size)
    frame = frame_header + json_data
    GlobalLogger.log("send_json_frame： " + frame.decode("utf-8"))

    # 分块发送
    chunk_size = 64
    for i in range(0, len(frame), chunk_size):
        chunk = frame[i : i + chunk_size]
        # print(f"发送第 {i//chunk_size + 1} 块，{chunk_size} 字节")
        # GlobalLogger.debug_print(chunk)
        ser.write(chunk)
        ser.flush()
