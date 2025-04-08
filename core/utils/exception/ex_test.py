"""
@File    :   ex_test.py
@Time    :   2025/04/08
@Desc    :   Define classes for test-related exceptions
"""

from core.utils.common import GlobalComm


class TestResultException(Exception):
    """Base test result exceptions, from which all test-related exceptions are inherited"""

    def __init__(
        self,
        message=GlobalComm.get_langdic_val("excep_test", "test_result"),
        *args,
        **kwargs
    ):
        self.message = message
        super().__init__(message, *args, **kwargs)


class TestFailureException(TestResultException):
    """Test Failure Exception, used to indicate that a test has not passed"""

    def __init__(
        self, message=GlobalComm.get_langdic_val("excep_test", "test_failure")
    ):
        super().__init__(message)


class TestTimeoutException(TestResultException):
    """Test timeout exception, used to indicate that a test has run longer than the scheduled time"""

    def __init__(
        self, message=GlobalComm.get_langdic_val("excep_test", "test_timeout")
    ):
        super().__init__(message)


class TestConnectException(TestResultException):
    """Connection exception in test, used to indicate that the test did not pass"""

    def __init__(
        self, message=GlobalComm.get_langdic_val("excep_test", "test_connect")
    ):
        super().__init__(message)


class TestFrameException(TestResultException):
    """Test data frame exception, used to indicate that the test has not passed"""

    def __init__(self, message=GlobalComm.get_langdic_val("excep_test", "test_frame")):
        super().__init__(message)


class TestFrameLengthException(TestFrameException):
    """Test data frame length exception, used to indicate that the test has not passed"""

    def __init__(
        self, message=GlobalComm.get_langdic_val("excep_test", "test_frame_length")
    ):
        super().__init__(message)


class TestFrameBeginException(TestFrameException):
    """Test data frame start bit exception, used to indicate that the test has not passed"""

    def __init__(
        self, message=GlobalComm.get_langdic_val("excep_test", "test_frame_begin")
    ):
        super().__init__(message)
