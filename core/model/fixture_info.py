"""
@File    :   fixture_info.py
@Time    :   2025/04/03
@Desc    :   Managing frame information to fixtures
"""

import json
import os
import serial
import time
from core.model.json_protocol import (
    build_key_json,
    FrameType,
    send_json_frame,
    receive_and_parse_frame,
)


class FixtureInfo:
    def __init__(self, port_path, serial_port):
        self.port_path = port_path
        self.serial_port = serial_port
        self.serial_dev = None
        self.dev_frame_dict = {}

    # Initialise the device frame dictionary and initialise the device
    def _init_port_info(self):
        self.dev_frame_dict.clear()

        for dev_module, items in self.port_json.items():
            need_send_value = "0" if "V" in dev_module else None

            frame_info = {dev_module: []}
            if dev_module != None:
                for dev_name, port in items.items():
                    key_json = build_key_json(port, dev_name, need_send_value)
                    frame_info[dev_module].append(key_json)

            self.dev_frame_dict[dev_module] = frame_info
            send_json_frame(self.serial_dev, FrameType.Cfg, frame_info)

    def sync_dev(self, frame_type):
        self.send_command_and_format_result(frame_type, "syncSQ")

    # 执行这个函数，说明port文件已经存在且正确，而串口若不存在则可在界面和log中查看
    def init_fixture(self):

        if self.serial_dev == None:
            self.serial_dev = serial.Serial(self.serial_port, 9600, timeout=1)

        if self.serial_dev.is_open is False:
            self.serial_dev.open()

        if self.dev_frame_dict == {}:
            with open(self.port_path, "r", encoding="utf-8") as f:
                self.port_json = json.load(f)
                self._init_port_info()

    def _wait_fixture_reply(self):
        wait_time_cnt = 0
        while True:
            wait_time_cnt += 1
            if self.serial_dev.in_waiting:
                return receive_and_parse_frame(self.serial_dev)

            if wait_time_cnt > 3000000:
                return None

    def _format_reply_info(self, reply):
        """
        将测试版输出格式：
        "Reply": [
            { "rgw0": "0.9, 0.0, 0.1"},
            { "rgw1": "0.9, 0.0, 0.1"},
            { "rgw2": "0.9, 0.0, 0.1"}
        ],
        转为信息判断的格式：
        {'rgw0': '0.9, 0.0, 0.1', 'rgw1': '0.9, 0.0, 0.1', 'rgw2': '0.9, 0.0, 0.1'}
        """

        fixture_dict = {}
        for sub_dict in reply["Reply"]:
            fixture_dict.update(sub_dict)
        return fixture_dict

    def send_command(self, frame_type, dev_type, value):
        """
        只适用用设备类型带“V”的key
        """

        from core.utils.opt_log import GlobalLogger

        # GlobalLogger.debug_print("dev_frame_dict:\r\n", self.dev_frame_dict)

        for btn in self.dev_frame_dict[dev_type].get(dev_type, []):
            btn["value"] = value
        send_json_frame(self.serial_dev, frame_type, self.dev_frame_dict[dev_type])
        # time.sleep(0.1)

    def send_command_and_format_result(self, frame_type, dev_type):
        """
        发送控制指令，接收相关数据
        frame_type: class FrameType(IntEnum)相关数据
        dev_type: btnSV，fanSQ，协议中的设备类（在port的json文件中的key上）
        """
        send_json_frame(self.serial_dev, frame_type, self.dev_frame_dict[dev_type])
        reply = self._wait_fixture_reply()
        if reply != None:
            fixture_dict = self._format_reply_info(reply)
            return fixture_dict
        return None

    def is_connect(self, exec_init=False):
        if os.path.exists(self.serial_port) and self.serial_dev.is_open:
            return True
        elif exec_init:
            print("init_fixture")
            self.init_fixture()
        return False
