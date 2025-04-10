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

    # Port information is initialised only on serial port exceptions and the first time.
    def _init_port_info(self):
        self.dev_frame_dict.clear()
        need_send_value = "0"
        for dev_module, items in self.port_json.items():
            frame_info = {dev_module: []}
            if dev_module != None:
                for dev_name, port in items.items():
                    if (
                        dev_name == "default_val"
                    ):  # Set initial default value according to default_val, can only be 0/1
                        need_send_value = port
                        print("val:", need_send_value)
                        continue
                    key_json = build_key_json(port, dev_name, need_send_value)
                    frame_info[dev_module].append(key_json)

            self.dev_frame_dict[dev_module] = frame_info
            send_json_frame(self.serial_dev, FrameType.Cfg, frame_info)

        #! Supplementary built-in module initialisation
        self.dev_frame_dict["syncSQ"] = {"port": "0", "name": "sync"}

    def sync_dev(self, frame_type):
        return self.send_command_and_format_result(frame_type, "syncSQ")

    # Retry to initialise the checker only if the serial port is abnormal
    def init_fixture(self, re_init=False):
        from core.utils.exception.ex_test import TestConnectException
        from core.utils.opt_log import GlobalLogger

        self.realease_resouce(re_init)

        if self.serial_dev == None:
            self.serial_dev = serial.Serial(self.serial_port, 9600, timeout=1)

        GlobalLogger.debug_print("init_fixture re_init", re_init)
        if re_init:
            if self.sync_dev(FrameType.Sync) == None:
                raise TestConnectException()

        if self.dev_frame_dict == {}:
            with open(self.port_path, "r", encoding="utf-8") as f:
                self.port_json = json.load(f)
                self._init_port_info()

    def realease_resouce(self, re_init):
        from core.utils.opt_log import GlobalLogger

        """If the gage breaks in the middle of the test, the current resources need to be released.

        Args:
            re_init (_type_): _description_
        """
        if re_init:
            GlobalLogger.debug_print("realease_resouce, maybe serial exception")
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
        Format the beta output:
        "Reply": [
            { "rgw0": "0.9, 0.0, 0.1"},
            { "rgw1": "0.9, 0.0, 0.1"},
            { "rgw2": "0.9, 0.0, 0.1"}
        ],
        Converted to an informative judgement format:
        {'rgw0': '0.9, 0.0, 0.1', 'rgw1': '0.9, 0.0, 0.1', 'rgw2': '0.9, 0.0, 0.1'}
        """

        fixture_dict = {}
        for sub_dict in reply["Reply"]:
            fixture_dict.update(sub_dict)
        return fixture_dict

    def send_command(self, frame_type, dev_type, value):
        """
        Only applicable to keys with "V" device type.
        """
        from core.utils.common import GlobalComm
        from core.utils.exception.ex_test import TestConnectException

        # GlobalLogger.debug_print("dev_frame_dict:\r\n", self.dev_frame_dict)
        for btn in self.dev_frame_dict[dev_type].get(dev_type, []):
            btn["value"] = value
        send_json_frame(self.serial_dev, frame_type, self.dev_frame_dict[dev_type])
        # time.sleep(0.1)

    def send_command_and_format_result(self, frame_type, dev_type):
        """
        Sending control commands and receiving relevant data
        frame_type: class FrameType(IntEnum)Related Data
        dev_type: btnSV, fanSQ, device class in protocol (on key in port's json file)
        """

        from core.utils.common import GlobalComm
        from core.utils.exception.ex_test import TestConnectException

        send_json_frame(self.serial_dev, frame_type, self.dev_frame_dict[dev_type])
        reply = self._wait_fixture_reply()
        if reply != None:
            fixture_dict = self._format_reply_info(reply)
            return fixture_dict
        return None

    def is_connect(self, exec_init=False):
        """Check that the fixtures are connected

        Args:
            exec_init (bool, optional): Reinitialise if True. Defaults to False.

        Returns:
            _type_: _description_
        """
        is_fixture_online = self.sync_dev(FrameType.Sync)

        if os.path.exists(self.serial_port) and is_fixture_online != None:
            return True
        elif exec_init:
            print("is_connect exec_init")
            self.init_fixture(exec_init)
        return False
