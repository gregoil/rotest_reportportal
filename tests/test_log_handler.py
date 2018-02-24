import mock
import logging

import pytest

from rotest_reportportal import ReportPortalLogHandler


@pytest.mark.parametrize("logging_level,level_text", [
    (logging.DEBUG, "DEBUG"),
    (logging.INFO, "INFO"),
    (logging.WARNING, "WARN"),
    (logging.ERROR, "ERROR"),
    (logging.CRITICAL, "ERROR")
])
def test_log_handler(logging_level, level_text):
    service = mock.Mock(log=mock.Mock())

    record = logging.makeLogRecord(
        dict(levelno=logging_level, msg="The message"))

    log_handler = ReportPortalLogHandler(service=service)

    with mock.patch("rotest_reportportal.timestamp", return_value="123"):
        log_handler.emit(record)

    service.log.assert_called_once_with(time="123",
                                        message="The message",
                                        level=level_text)
