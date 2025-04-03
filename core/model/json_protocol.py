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


# todo, 补充log和异常处理
def receive_and_parse_frame(ser):
    # 帧头定义
    FRAME_START = 0x5F
    HEADER_SIZE = 6  # startByte(1) + msgid(1) + dataSize(4)

    try:
        # 读取帧头
        header_data = ser.read(HEADER_SIZE)
        if len(header_data) == HEADER_SIZE:
            # 解析帧头
            start_byte, msgid, data_size = struct.unpack("<BBI", header_data)

            # print(start_byte, msgid, data_size)

            # 验证帧头
            if start_byte == FRAME_START:
                # 读取数据部分
                data = ser.read(data_size)
                # print(data)
                if len(data) == data_size:
                    try:
                        # 尝试解析为JSON
                        json_data = json.loads(data.decode("utf-8"))
                        print("收到JSON数据：", json_data)
                        return json_data
                    except json.JSONDecodeError:
                        print("数据不是有效的JSON格式")
                else:
                    print("数据长度不匹配")
            else:
                print("无效的帧起始字节")
    except Exception as e:
        print("数据接收解析错误：", e)

    return None


def send_json_frame(ser, infoId, payload):
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

    # 分块发送
    chunk_size = 64
    for i in range(0, len(frame), chunk_size):
        chunk = frame[i : i + chunk_size]
        # print(f"发送第 {i//chunk_size + 1} 块，{chunk_size} 字节")
        ser.write(chunk)
        ser.flush()
