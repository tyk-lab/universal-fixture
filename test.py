def check_btn_state(state):
    result = False
    if not result:
        excep_list = [1, 2, 3]
        a = 3
        raise Exception(excep_list, a)
    return result


# 使用时捕获异常并访问异常列表
try:
    check_btn_state(True)
except Exception as e:
    excep_list = e.args[0]  # 从异常中获取列表
    a = e.args[1]
    print(excep_list, a)
