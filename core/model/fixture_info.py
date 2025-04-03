"""
@File    :   fixture_info.py
@Time    :   2025/04/03
@Desc    :   Managing frame information to fixtures
"""

import json

from core.model.json_protocol import (
    build_key_json,
    FrameType,
    send_json_frame,
    receive_and_parse_frame,
)
from core.utils.common import GlobalComm
from core.utils.opt_log import GlobalLogger


class FixtureInfo:
    def __init__(self, port_path, serial):
        self.port_path = port_path
        self.serial = serial
        self.dev_frame_dict = {}

    # Initialise the device frame dictionary and initialise the device
    def _init_port_info(self):
        for dev_module, items in self.port_json.items():
            need_send_value = 0 if "V" in dev_module else None

            frame_info = {dev_module: []}
            if dev_module != None:
                for dev_name, port in items.items():
                    key_json = build_key_json(port, dev_name, need_send_value)
                    frame_info[dev_module].append(key_json)

            self.dev_frame_dict[dev_module] = frame_info
            send_json_frame(self.serial, FrameType.Cfg, frame_info)

    #!todo, 可能会引发异常，如串口不存在等
    def init_fixture(self):
        with open(self.port_path, "r", encoding="utf-8") as f:
            self.port_json = json.load(f)
            self.init_port_info(self.serial)

    def _wait_fixture_reply(self):
        wait_time_cnt = 0
        while True:
            wait_time_cnt += 1
            if self.serial.in_waiting:
                return receive_and_parse_frame(self.serial)

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
        data = json.loads(reply)
        fixture_dict = {}
        for item in data["Reply"]:
            fixture_dict.update(item)
        return fixture_dict

    def send_command_and_format_result(self, frame_type, dev_type):
        send_json_frame(self.serial, frame_type, self.dev_frame_dict[dev_type])
        reply = self.wait_fixture_reply()
        if reply != None:
            return self._format_reply_info(reply)
        return None
