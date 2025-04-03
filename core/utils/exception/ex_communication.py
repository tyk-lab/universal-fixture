class CommunicationException(Exception):
    """
    通信异常基类，用于描述通信过程中出现的各种异常情况。
    """

    def __init__(self, message="通信异常", details=None):
        """
        初始化异常信息

        参数:
            message: 错误描述，默认为"通信异常"
            details: 附加的详细信息，可以是字符串或其他对象
        """
        self.message = message
        self.details = details
        full_message = f"{message} - 详情: {details}" if details else message
        super().__init__(full_message)

    def __str__(self):
        return (
            f"{self.message} - 详情: {self.details}" if self.details else self.message
        )


class ConnectionTimeoutException(CommunicationException):
    """
    连接超时异常，当通信连接在规定时间内未能建立或响应时抛出。
    """

    def __init__(self, details=None):
        super().__init__("连接超时", details)


class ConnectionFormatException(CommunicationException):
    """
    通信帧格式不对
    """

    def __init__(self, details=None):
        super().__init__("连接超时", details)


class ConnectionLostException(CommunicationException):
    """
    连接中断异常，当通信连接中断或丢失时抛出。
    """

    def __init__(self, details=None):
        super().__init__("连接丢失", details)


class DataCorruptionException(CommunicationException):
    """
    数据损坏异常，当接收到的数据内容不符合预期或校验失败时抛出。
    """

    def __init__(self, details=None):
        super().__init__("数据损坏", details)
