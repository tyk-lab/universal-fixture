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
        filepath="",
        message=GlobalComm.get_langdic_val("excep_file", "file_result"),
        *args,
        **kwargs,
    ):
        self.filepath = filepath
        self.message = f"{message}: {filepath}"
        super().__init__(message, *args, **kwargs)


class FileReadError(FileException):
    """An exception occurred while reading a file"""

    def __init__(
        self,
        filepath,
        message=GlobalComm.get_langdic_val("excep_file", "file_read"),
        *args,
        **kwargs,
    ):
        super().__init__(filepath, message, *args, **kwargs)


class FileWriteError(FileException):
    """Exception occurred while writing a file"""

    def __init__(
        self,
        filepath,
        message=GlobalComm.get_langdic_val("excep_file", "file_write"),
        *args,
        **kwargs,
    ):
        super().__init__(filepath, message, *args, **kwargs)


class FileFormatError(FileException):
    """File format anomalies, e.g. parsing in the wrong format"""

    def __init__(
        self,
        filepath,
        message=GlobalComm.get_langdic_val("excep_file", "file_format"),
        *args,
        **kwargs,
    ):
        super().__init__(filepath, message, *args, **kwargs)


class FileNotFoundCustomError(FileException):
    """Custom File Not Found Exception (note: the built-in FileNotFoundError also applies)"""

    def __init__(
        self,
        filepath,
        message=GlobalComm.get_langdic_val("excep_file", "file_not_found"),
        *args,
        **kwargs,
    ):
        super().__init__(filepath, message, *args, **kwargs)
