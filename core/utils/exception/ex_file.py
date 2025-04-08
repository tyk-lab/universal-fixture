"""
@File    :   ex_file.py
@Time    :   2025/04/08
@Desc    :   Define classes for file-related exceptions
"""

from core.utils.common import GlobalComm


class FileException(Exception):
    """File exception base class, all file-related exceptions inherit from this class."""

    def __init__(
        self,
        message=GlobalComm.get_langdic_val("excep_test", "file_result"),
        filepath="",
        *args,
        **kwargs,
    ):
        self.filepath = filepath
        self.message = f"{message}: {filepath}"
        super().__init__(message, *args, **kwargs)


class FileReadError(FileException):
    """An exception occurred while reading a file"""

    def __init__(
        self, filepath, message=GlobalComm.get_langdic_val("excep_test", "file_read")
    ):
        super().__init__(message, filepath)


class FileWriteError(FileException):
    """Exception occurred while writing a file"""

    def __init__(
        self, filepath, message=GlobalComm.get_langdic_val("excep_test", "file_write")
    ):
        super().__init__(message, filepath)


class FileFormatError(FileException):
    """File format anomalies, e.g. parsing in the wrong format"""

    def __init__(
        self, filepath, message=GlobalComm.get_langdic_val("excep_test", "file_format")
    ):
        super().__init__(message, filepath)


class FileNotFoundCustomError(FileException):
    """Custom File Not Found Exception (note: the built-in FileNotFoundError also applies)"""

    def __init__(
        self,
        filepath,
        message=GlobalComm.get_langdic_val("excep_test", "file_not_found"),
    ):
        super().__init__(message, filepath)
