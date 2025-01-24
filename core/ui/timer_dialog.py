from PyQt6.QtWidgets import QPushButton, QDialog, QLabel, QVBoxLayout
from PyQt6.QtCore import QTimer


class TimerDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.cur_time = 0
        self.timeout_duration = 30
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

        # 设置一个计时器来更新数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loop_check)

    def loop_check(self):
        result, stan_diff, cur_diff, cur_val = self.check_fun()
        test_result = f"标准误差值: {stan_diff} \r\n偏差值 {cur_diff} \r\n当前值(晃动后的值): {cur_val}"

        print("running ", self.cur_time)
        print("cur:", cur_val)

        self.label.setStyleSheet("color: green;" if result else "color: red;")
        self.label.setText(test_result)
        self.cur_time += 1

        if result:
            self.pass_cnt += 1
            if self.pass_cnt >= 5:
                print("")
                self.close_dialog(True, test_result)
        elif self.cur_time >= self.timeout_duration:
            print("over timer")
            self.close_dialog(False, test_result)

    def close_dialog(self, result, log):
        print("close_dialog")
        self.result_fun(self.test_key_name, result, log)
        self.timer.stop()
        # self.deleteLater()
        self.close()

    def showEvent(self, event):
        print("show")
        self.timer.start(1000)
        super().showEvent(event)
