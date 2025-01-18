import threading


def task():
    print("定时任务正在执行...")


def start_timer():
    # 计数器，用于记录执行次数
    count = 0

    def run_task():
        nonlocal count
        count += 1
        if count <= 8:
            task()
            # 创建新的定时器
            threading.Timer(1, run_task).start()

    # 启动第一次定时任务
    run_task()


# 启动定时器
start_timer()
