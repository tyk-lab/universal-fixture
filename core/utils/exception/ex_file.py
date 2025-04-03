class FileException(Exception):
    """文件异常基类，所有文件相关异常都继承自此类"""

    pass


class FileReadError(FileException):
    """读取文件时发生异常"""

    def __init__(self, filepath, message="读取文件时出错"):
        self.filepath = filepath
        self.message = f"{message}: {filepath}"
        super().__init__(self.message)


class FileWriteError(FileException):
    """写入文件时发生异常"""

    def __init__(self, filepath, message="写入文件时出错"):
        self.filepath = filepath
        self.message = f"{message}: {filepath}"
        super().__init__(self.message)


class FileFormatError(FileException):
    """文件格式异常，例如解析时格式错误"""

    def __init__(self, filepath, message="文件格式错误"):
        self.filepath = filepath
        self.message = f"{message}: {filepath}"
        super().__init__(self.message)


class FileNotFoundCustomError(FileException):
    """自定义文件未找到异常（注意：内建的 FileNotFoundError 也适用）"""

    def __init__(self, filepath, message="文件未找到"):
        self.filepath = filepath
        self.message = f"{message}: {filepath}"
        super().__init__(self.message)
