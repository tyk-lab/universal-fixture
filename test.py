import serial
import time
import struct
import json
from enum import Enum, auto, IntEnum

#############################
# 包解析相关
############################


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
        print(chunk)
        ser.write(chunk)
        ser.flush()


###########################
# 其他定义
############################
class FrameType(IntEnum):
    Cfg = 0
    Opt = 1
    Request = 2
    Sync = 3
    Shucdown = 4


#############################
# 测试相关
############################


def build_btn_JsonField(value):
    payload = {
        "btnSV": [
            {"port": "0", "name": "btn1", "value": str(value)},
            {"port": "1", "name": "btn2", "value": str(value)},
            {"port": "2", "name": "btn3", "value": str(value)},
        ]
    }
    return payload


def build_th_JsonField():
    payload = {
        "thSQ": [
            {"port": "0", "name": "th0"},
            {"port": "1", "name": "th1"},
        ]
    }
    return payload


def build_sync_JsonField():
    payload = {
        "syncSQ": [{"port": "0", "name": "sync"}],
    }
    return payload


def build_vol_JsonField():
    payload = {
        "volSQ": [
            {"port": "0", "name": "vol0"},
        ],
    }
    return payload


def build_rgb_JsonField():
    payload = {
        "rgbwSQ": [
            {"port": "0", "name": "rgw0"},
        ],
    }
    return payload


###########################
# 主逻辑
############################


def init_dev(ser):
    send_json_frame(ser, FrameType.Cfg, build_btn_JsonField(0))
    send_json_frame(ser, FrameType.Cfg, build_th_JsonField())
    send_json_frame(ser, FrameType.Cfg, build_sync_JsonField())
    # send_json_frame(ser, FrameType.Cfg, build_vol_JsonField())
    send_json_frame(ser, FrameType.Cfg, build_rgb_JsonField())


def main():
    port = "/dev/serial/by-id/usb-LDO-TEST_LDO-TEST_Virtual_ComPort_in_FS_Mode_0000000C0000-if00"
    baud_rate = 9600
    timeout = 1
    value = 0

    try:
        ser = serial.Serial(port, baud_rate, timeout=timeout)
        if ser.is_open:
            print(f"成功打开串口：{port}，波特率：{baud_rate}")
            # init_dev(ser)

            while True:
                # 检查是否有数据可读
                if ser.in_waiting:
                    receive_and_parse_frame(ser)

                value = 1 if value == 0 else 0
                # send_json_frame(ser, FrameType.Opt, build_btn_JsonField(value))
                # send_json_frame(ser, FrameType.Request, build_th_JsonField())
                send_json_frame(ser, FrameType.Sync, build_sync_JsonField())
                # time.sleep(0.3)

                # # send_json_frame(ser, FrameType.Request, build_vol_JsonField())
                # # time.sleep(0.3)

                # send_json_frame(ser, FrameType.Request, build_rgb_JsonField())
                time.sleep(0.3)

    except Exception as e:
        print("发生异常：", e)
    finally:
        if "ser" in locals() and ser.is_open:
            ser.close()
            print("串口已关闭")


if __name__ == "__main__":
    main()
