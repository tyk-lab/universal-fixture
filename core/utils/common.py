import json
import os
from core.utils.msg import CustomDialog


class GlobalComm:
    setting_path = "core/cfg/settings.json"
    language_path = "core/cfg/language.json"

    language_json = dict()
    setting_json = dict()

    language = ""

    test_enable = True

    @staticmethod
    def get_langdic_val(sub_key_str, obj_str):
        return GlobalComm.language_json[GlobalComm.language][sub_key_str][obj_str]

    @staticmethod
    def load_json_cfg():
        result = False

        # print(os.getcwd())
        try:
            with open(GlobalComm.setting_path, "r", encoding="utf-8") as f:
                GlobalComm.setting_json = json.load(f)
                # print(GlobalComm.setting_json)

            with open(GlobalComm.language_path, "r", encoding="utf-8") as f:

                GlobalComm.language_json = json.load(f)
                GlobalComm.language = GlobalComm.setting_json["language"]
                # print(GlobalComm.language_json)
                # print(GlobalComm.language)

            result = True
        except Exception as e:
            error = f"exception can't load cfg files:  {e}"
            dialog = CustomDialog()
            dialog.show_warning(error)
            return result
        finally:
            return result

    @staticmethod
    def set_cur_language(language):
        GlobalComm.language = language

    @staticmethod
    def save_json_setting(key, val):
        with open(GlobalComm.setting_path, "w") as f:
            GlobalComm.setting_json[key] = val
            json.dump(GlobalComm.setting_json, f, ensure_ascii=False, indent=4)
