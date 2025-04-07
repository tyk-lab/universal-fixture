# test_exceptions.py
# 定义基础测试结果异常
class TestResultException(Exception):
    """基础测试结果异常，所有测试相关异常都继承自该类"""

    pass


# 定义测试失败异常
class TestFailureException(TestResultException):
    """测试失败异常，用于表示测试未通过"""

    def __init__(self, message="测试失败"):
        super().__init__(message)


# 定义测试超时异常
class TestTimeoutException(TestResultException):
    """测试超时异常，用于表示测试运行超过预定时间"""

    def __init__(self, timeout, message="测试超时"):
        self.timeout = timeout
        super().__init__(f"{message}：超过 {timeout} 秒")


# 定义测试失联异常
class TestConnectException(TestResultException):
    """测试失败异常，用于表示测试未通过"""

    def __init__(self, message="通信失联"):
        super().__init__(message)


# 定义测试通信数据帧异常
class TestFrameException(TestResultException):
    """测试失败异常，用于表示测试未通过"""

    def __init__(self, message="通信数据帧"):
        super().__init__(message)


# 定义测试通信数据帧异常
class TestFrameLengthException(TestFrameException):
    """测试失败异常，用于表示测试未通过"""

    def __init__(self, message="通信数据帧长度"):
        super().__init__(message)


class TestFrameBeginException(TestFrameException):
    """测试失败异常，用于表示测试未通过"""

    def __init__(self, message="通信数据帧起始字节错误"):
        super().__init__(message)
