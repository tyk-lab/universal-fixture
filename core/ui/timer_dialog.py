from PyQt6.QtWidgets import QPushButton, QDialog, QLabel, QVBoxLayout
import threading


class TimerDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.cur_time = 0
        self.timeout_duration = 5
        self.pass_cnt = 0
        self.test_key_name = ""

        self.init_dialog()

    def set_check_fun(self, check_fun, result_fun):
        self.check_fun = check_fun
        self.result_fun = result_fun

    def set_title_name(self, name):
        self.test_key_name = name

    def init_dialog(self):
        self.label = QLabel("当前值: 0,0,0", self)

        button = QPushButton("确定", self)
        button.clicked.connect(self.accept)  # 关闭对话框

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(button)

        self.setLayout(layout)
        self.setWindowTitle("数据更新弹窗")
        self.setGeometry(100, 100, 300, 100)

    def loop_check(self):
        result, cur_val = self.check_fun()
        print("running ", self.cur_time)
        print("cur:", cur_val)
        self.label.setText(f"当前值: {cur_val}")
        self.cur_time += 1

        restart_timer = True
        if result:
            self.pass_cnt += 1
            if self.pass_cnt >= 5:
                print("")
                self.close_dialog(True, cur_val)
                restart_timer = False
        elif self.cur_time >= self.timeout_duration:
            print("over timer")
            self.close_dialog(False, cur_val)
            restart_timer = False

        if restart_timer:
            threading.Timer(1, self.loop_check).start()
            return

    def close_dialog(self, result, log):
        print("close_dialog")
        self.result_fun(self.test_key_name, result, log)
        self.deleteLater()
        # self.close()

    def showEvent(self, event):
        print("show")
        threading.Timer(1, self.loop_check).start()
        super().showEvent(event)
