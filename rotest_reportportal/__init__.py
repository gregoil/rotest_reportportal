"""Report Portal client to publish test results of the Rotest framework."""
import os
import time
import logging

import yaml
from attrdict import AttrDict
from rotest.common import core_log
from rotest.core.flow import TestFlow
from rotest.core.result.result import TestOutcome
from rotest.common.config import search_config_file
from reportportal_client import ReportPortalServiceAsync
from rotest.core.result.handlers.abstract_handler import AbstractResultHandler
from rotest.core.flow_component import (MODE_CRITICAL, MODE_OPTIONAL,
                                        MODE_FINALLY)

REPORTPORTAL_TOKEN = "ROTEST_REPORTPORTAL_TOKEN"


def timestamp():
    """Return the current timestamp.

    Returns:
        str: current time in the "Unix time" format.
    """
    return str(int(time.time() * 1000))


def get_configuration():
    """Get configuration for accessing Report Portal system."""
    config_file = search_config_file()
    with open(config_file, "r") as rotest_configuration:
        content = yaml.load(rotest_configuration.read())

    if "reportportal" not in content:
        raise ValueError(
            "No 'reportportal' key is defined in {}. "
            "Instead, found the following content:\n{}".format(config_file,
                                                               content))

    configuration = AttrDict(content["reportportal"])

    if REPORTPORTAL_TOKEN not in os.environ:
        raise ValueError(
            "You need to define the environment variable {} in "
            "order to access Report Portal".format(REPORTPORTAL_TOKEN))

    configuration.token = os.environ[REPORTPORTAL_TOKEN]
    return configuration


class ReportPortalLogHandler(logging.Handler):
    """Send every log record to the Report Portal system.

    Logs messages cannot be sent when there is no active test running, so make
    sure to remove the handler when it's outside the scope of any test.
    The handler supports both regular messages and files. For example:

    .. code-block:: python

        log.addHandler(ReportPortalLogHandler(service=service))
        log.info("Regular message in here")

    Attributes:
        service (ReportPortalServiceAsync): Endpoint for interacting with
            Report Portal.
    """
    FORMAT = "%(message)s"

    LOGGING_LEVEL_CONVERSION = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARN",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "ERROR"
    }

    def __init__(self, service, *args, **kwargs):
        super(ReportPortalLogHandler, self).__init__(*args, **kwargs)
        self.service = service
        self.setFormatter(logging.Formatter(self.FORMAT))

    def emit(self, record):
        try:
            message = self.format(record)

            self.service.log(
                time=timestamp(),
                message=message,
                level=self.LOGGING_LEVEL_CONVERSION[record.levelno])
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)
            raise


class ReportPortalHandler(AbstractResultHandler):
    """Send tests results and logs to the Report Portal system.

    Attributes:
        main_test (object): the main test instance to be run.
        service (ReportPortalServiceAsync): Endpoint for interracting with
            Report Portal.
        log_handler (ReportPortalLogHandler): A log handler to send every log
            message to the Report Portal system. Logs can be sent only when
            a test is currently running.
    """
    NAME = "reportportal"

    MODE_TO_STRING = {MODE_CRITICAL: "Critical",
                      MODE_OPTIONAL: "Optional",
                      MODE_FINALLY: "Finally"}

    EXCEPTION_TYPE_TO_STATUS = {TestOutcome.SUCCESS: "PASSED",
                                TestOutcome.ERROR: "FAILED",
                                TestOutcome.FAILED: "FAILED",
                                TestOutcome.SKIPPED: "SKIPPED",
                                TestOutcome.EXPECTED_FAILURE: "PASSED",
                                TestOutcome.UNEXPECTED_SUCCESS: "FAILED"}

    EXCEPTION_TYPE_TO_ISSUE = {TestOutcome.ERROR: "AUTOMATION_BUG",
                               TestOutcome.FAILED: "PRODUCT_BUG",
                               TestOutcome.SKIPPED: "NO_DEFECT"}

    def __init__(self, main_test, *args, **kwargs):
        super(ReportPortalHandler, self).__init__(main_test=main_test,
                                                  *args, **kwargs)

        configuration = get_configuration()
        self.service = ReportPortalServiceAsync(
            endpoint=configuration.endpoint,
            project=configuration.project,
            token=configuration.token)

        self.log_handler = ReportPortalLogHandler(self.service)
        self.comments = []

    def start_test_run(self):
        """Called once before any tests are executed."""
        run_name = self.main_test.data.run_data.run_name
        mode = "DEFAULT"
        if not run_name:
            run_name = self.main_test.__class__.__name__
            mode = "DEBUG"

        description = self.main_test.__doc__

        self.service.start_launch(
            name=run_name,
            start_time=timestamp(),
            description=description,
            mode=mode)

    def start_test(self, test):
        """Called when the given test is about to be run.

        Args:
            test (object): test item instance.
        """
        item_type = "STEP"
        description = test.shortDescription()

        if isinstance(test, TestFlow):
            description = test.__doc__

        mode = getattr(test, "mode", None)
        if mode is not None:
            description = "|{}| {}".format(self.MODE_TO_STRING[mode],
                                           description)

        self.service.start_test_item(
            name=test.data.name,
            description=description,
            tags=test.TAGS if hasattr(test, "TAGS") else None,
            start_time=timestamp(),
            item_type=item_type)

        core_log.addHandler(self.log_handler)
        self.service.log(
            time=timestamp(),
            level="INFO",
            message="work dir:\n{0}".format(os.path.abspath(test.work_dir)))

    def start_composite(self, test):
        """Called when the given TestSuite is about to be run.

        Args:
            test (rotest.core.suite.TestSuite): test item instance.
        """
        if test == self.main_test:
            return

        self.service.start_test_item(
            name=test.data.name,
            description=test.__doc__,
            tags=test.TAGS if hasattr(test, "TAGS") else None,
            start_time=timestamp(),
            item_type="Suite")

    def stop_composite(self, test):
        """Called when the given TestSuite has been run.

        Args:
            test (rotest.core.suite.TestSuite): test item instance.
        """
        if test == self.main_test:
            return

        if test.data.success:
            status = "PASSED"
        else:
            status = "FAILED"

        self.service.finish_test_item(end_time=timestamp(),
                                      status=status)

    def stop_test_run(self):
        """Called once after all tests are executed."""
        self.service.finish_launch(end_time=timestamp())
        self.service.terminate()

    def stop_test(self, test):
        """Called once after a test is finished."""
        core_log.removeHandler(self.log_handler)
        exception_type = test.data.exception_type
        status = self.EXCEPTION_TYPE_TO_STATUS.get(exception_type, "FAILED")

        issue = None
        if exception_type in self.EXCEPTION_TYPE_TO_ISSUE or \
                not exception_type:
            issue = {
                "issue_type":
                    self.EXCEPTION_TYPE_TO_ISSUE.get(exception_type,
                                                     "TO_INVESTIGATE"),
                "comment": "\n".join(self.comments)
            }

        self.service.finish_test_item(end_time=timestamp(),
                                      status=status,
                                      issue=issue)

        self.comments = []

    def add_skip(self, test, reason):
        self.comments.append(reason)

    def add_error(self, test, exception_string):
        reason = [line for line in exception_string.split("\n") if line][-1]
        self.comments.append(reason)

    def add_failure(self, test, exception_string):
        reason = [line for line in exception_string.split("\n") if line][-1]
        self.comments.append(reason)

    def add_unexpected_success(self, test):
        self.service.log(time=timestamp(),
                         message="The test was supposed to fail, but instead "
                                 "it passed",
                         level="ERROR")
