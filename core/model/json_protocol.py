"""
@File    :   json_transfer.py
@Time    :   2025/04/03
@Desc    :
            Framing Protocol Format
            startByte(1) + msgid(1) + dataSize(4) + data(n)
       eg:    0x5F            0x01      0x00000004
"""

import json
import struct

from enum import IntEnum


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
    from core.utils.exception.ex_test import (
        TestFrameBeginException,
        TestFrameLengthException,
    )
    from core.utils.opt_log import GlobalLogger

    # Frame header definition
    FRAME_START = 0x5F
    HEADER_SIZE = 6  # startByte(1) + msgid(1) + dataSize(4)

    # Retrieve frame header
    header_data = ser.read(HEADER_SIZE)
    if len(header_data) == HEADER_SIZE:
        # Parse header
        start_byte, msgid, data_size = struct.unpack("<BBI", header_data)

        # GlobalLogger.debug_print("state data: ", start_byte, msgid, data_size)

        # Verify Frame Header
        if start_byte == FRAME_START:
            # Read data section
            data = ser.read(data_size)
            # print(data)
            if len(data) == data_size:
                # Try to parse to JSON
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

    # Frame header definition
    FRAME_START = 0x5F
    MSGID = infoId

    # Convert dictionary to JSON string and encode it
    json_str = json.dumps(payload, separators=(",", ":"))
    json_data = json_str.encode("utf-8")
    data_size = len(json_data)

    # header
    frame_header = struct.pack("<BBI", FRAME_START, MSGID, data_size)
    frame = frame_header + json_data
    GlobalLogger.log("send_json_frame data： " + json_str)

    # chunk
    chunk_size = 64
    for i in range(0, len(frame), chunk_size):
        chunk = frame[i : i + chunk_size]
        # print(f"发送第 {i//chunk_size + 1} 块，{chunk_size} 字节")
        # GlobalLogger.debug_print(chunk)
        ser.write(chunk)
        ser.flush()
