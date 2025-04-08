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

        #!todo 补充内置的模块初始化
        self.dev_frame_dict["syncSQ"] = {"port": "0", "name": "sync"}

    def sync_dev(self, frame_type):
        return self.send_command_and_format_result(frame_type, "syncSQ")

    def init_fixture(self, re_init=False):
        from core.utils.common import GlobalComm
        from core.utils.exception.ex_test import TestConnectException

        self.realease_resouce(re_init)

        if self.serial_dev == None:
            self.serial_dev = serial.Serial(self.serial_port, 9600, timeout=1)

        print("re_init", re_init)
        if re_init:
            if self.sync_dev(FrameType.Sync) == None:
                raise TestConnectException(
                    self.init_fixture.__name__
                    + " : "
                    + GlobalComm.get_langdic_val("exception_tip", "excep_connect")
                )

        if self.dev_frame_dict == {}:
            with open(self.port_path, "r", encoding="utf-8") as f:
                self.port_json = json.load(f)
                self._init_port_info()

    def realease_resouce(self, re_init):
        if re_init:
            print("realease_resouce")
            self.serial_dev.close()
            self.dev_frame_dict = {}
            self.serial_dev = None

    def _wait_fixture_reply(self):
        wait_time_cnt = 0
        while True:
            wait_time_cnt += 1
            if self.serial_dev.in_waiting:
                return receive_and_parse_frame(self.serial_dev)

            if wait_time_cnt > 100000:
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
        from core.utils.common import GlobalComm
        from core.utils.exception.ex_test import TestConnectException

        # GlobalLogger.debug_print("dev_frame_dict:\r\n", self.dev_frame_dict)
        try:
            for btn in self.dev_frame_dict[dev_type].get(dev_type, []):
                btn["value"] = value
            send_json_frame(self.serial_dev, frame_type, self.dev_frame_dict[dev_type])
            # time.sleep(0.1)
        except serial.serialutil.SerialException as e:
            raise TestConnectException(
                self.send_command.__name__
                + " : "
                + GlobalComm.get_langdic_val("exception_tip", "excep_connect_send")
            )

    def send_command_and_format_result(self, frame_type, dev_type):
        """
        发送控制指令，接收相关数据
        frame_type: class FrameType(IntEnum)相关数据
        dev_type: btnSV，fanSQ，协议中的设备类（在port的json文件中的key上）
        """

        from core.utils.common import GlobalComm
        from core.utils.exception.ex_test import TestConnectException

        try:
            send_json_frame(self.serial_dev, frame_type, self.dev_frame_dict[dev_type])
            reply = self._wait_fixture_reply()
            if reply != None:
                fixture_dict = self._format_reply_info(reply)
                return fixture_dict
            return None
        except serial.serialutil.SerialException as e:
            raise TestConnectException(
                self._format_reply_info.__name__
                + " : "
                + GlobalComm.get_langdic_val("exception_tip", "excep_connect_send")
            )

    def is_connect(self, exec_init=False):
        is_fixture_online = self.sync_dev(FrameType.Sync)

        if os.path.exists(self.serial_port) and is_fixture_online != None:
            return True
        elif exec_init:
            print("is_connect exec_init")
            self.init_fixture(exec_init)
        return False
