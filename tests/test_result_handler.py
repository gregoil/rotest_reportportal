import mock
from rotest.core.case import TestCase
from rotest.core.block import TestBlock
from rotest.core.suite import TestSuite

from rotest_reportportal import ReportPortalHandler


@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_result_handler_creation(configuration_patch, service_patch):
    configuration_patch.return_value.endpoint = "http://host:8000"
    configuration_patch.return_value.project = "nightly"
    configuration_patch.return_value.token = "token"

    main_test = mock.Mock()

    ReportPortalHandler(main_test=main_test)

    service_patch.assert_called_once_with(endpoint="http://host:8000",
                                          project="nightly",
                                          token="token")


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_starting_public_run(configuration_patch, service_patch, _time_patch):
    configuration_patch.return_value.endpoint = "http://host:8000"
    configuration_patch.return_value.project = "nightly"
    configuration_patch.return_value.token = "token"

    main_test = mock.Mock()
    main_test.data.run_data.run_name = "run name"
    main_test.__doc__ = "test documentation"

    handler = ReportPortalHandler(main_test=main_test)
    handler.start_test_run()

    service_patch.return_value.start_launch.assert_called_once_with(
        name="run name",
        start_time="123",
        description="test documentation",
        mode="DEFAULT"
    )


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_starting_debug_run(configuration_patch, service_patch, _time_patch):
    configuration_patch.return_value.endpoint = "http://host:8000"
    configuration_patch.return_value.project = "nightly"
    configuration_patch.return_value.token = "token"

    main_test = mock.Mock()
    main_test.data.run_data.run_name = ""
    main_test.__class__.__name__ = "run name"
    main_test.__doc__ = "test documentation"

    handler = ReportPortalHandler(main_test=main_test)
    handler.start_test_run()

    service_patch.return_value.start_launch.assert_called_once_with(
        name="run name",
        start_time="123",
        description="test documentation",
        mode="DEBUG"
    )


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_finishing_run(_configuration_patch, service_patch, _time_patch):
    main_test = mock.Mock()

    handler = ReportPortalHandler(main_test=main_test)
    handler.stop_test_run()

    service_patch.return_value.finish_launch.assert_called_once_with(
        end_time="123",
    )
    service_patch.return_value.terminate.assert_called_once_with()


class Case(TestCase):
    __test__ = False  # Not a test to be executed by pytest

    TAGS = ["TAG1", "TAG2"]

    def test_method(self):
        """Case documentation."""
        pass


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_starting_test_case(_configuration_patch, service_patch, _time_patch):
    main_test = mock.Mock(parents_count=0)
    test_case = Case(methodName="test_method", parent=main_test)

    handler = ReportPortalHandler(main_test=main_test)
    handler.start_test(test_case)

    service_patch.return_value.start_test_item.assert_called_once_with(
        name="Case.test_method",
        description="Case documentation.",
        tags=["TAG1", "TAG2"],
        start_time="123",
        item_type="STEP"
    )


class Block(TestBlock):
    __test__ = False  # Not a test to be executed by pytest

    def test_method(self):
        """Block documentation."""
        pass


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_starting_block(_configuration_patch, service_patch, _time_patch):
    main_test = mock.Mock()
    block = Block()

    handler = ReportPortalHandler(main_test=main_test)
    handler.start_test(block)

    service_patch.return_value.start_test_item.assert_called_once_with(
        name="Block.test_method",
        description="|Critical| Block documentation.",
        tags=None,
        start_time="123",
        item_type="STEP"
    )


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_starting_flow(_configuration_patch, service_patch, _time_patch):
    main_test = mock.Mock()

    # Defining in method level,
    # so pytest won't try to run ``Flow`` and ``TestFlow``
    from rotest.core.flow import TestFlow

    class Flow(TestFlow):
        """Flow documentation."""
        TAGS = ["TAG1", "TAG2"]
        blocks = (Block,)

    handler = ReportPortalHandler(main_test=main_test)
    handler.start_test(Flow())

    service_patch.return_value.start_test_item.assert_called_once_with(
        name="Flow",
        description="Flow documentation.",
        tags=["TAG1", "TAG2"],
        start_time="123",
        item_type="STEP"
    )


class Suite(TestSuite):
    """Suite documentation."""
    TAGS = ["TAG1", "TAG2"]

    components = (Case,)


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_starting_suite(_configuration_patch, service_patch, _time_patch):
    main_test = mock.Mock()
    suite = Suite()

    handler = ReportPortalHandler(main_test=main_test)
    handler.start_composite(suite)

    service_patch.return_value.start_test_item.assert_called_once_with(
        name="Suite",
        description="Suite documentation.",
        tags=["TAG1", "TAG2"],
        start_time="123",
        item_type="Suite"
    )


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_starting_main_suite(_configuration_patch, service_patch, _time_patch):
    main_test = mock.Mock()

    handler = ReportPortalHandler(main_test=main_test)
    handler.start_composite(main_test)

    service_patch.return_value.start_test_item.assert_not_called()


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_finishing_main_suite(_configuration_patch, service_patch,
                              _time_patch):
    main_test = mock.Mock()

    handler = ReportPortalHandler(main_test=main_test)
    handler.stop_composite(main_test)

    service_patch.return_value.stop_test_item.assert_not_called()


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_finishing_successful_suite(_configuration_patch, service_patch,
                                    _time_patch):
    main_test = mock.Mock()
    suite = Suite()
    suite.data.success = True

    handler = ReportPortalHandler(main_test=main_test)
    handler.stop_composite(suite)

    service_patch.return_value.finish_test_item.assert_called_once_with(
        end_time="123",
        status="PASSED"
    )


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_finishing_failed_suite(_configuration_patch, service_patch,
                                _time_patch):
    main_test = mock.Mock()
    suite = Suite()
    suite.data.success = False

    handler = ReportPortalHandler(main_test=main_test)
    handler.stop_composite(suite)

    service_patch.return_value.finish_test_item.assert_called_once_with(
        end_time="123",
        status="FAILED"
    )


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_successful_test(_configuration_patch, service_patch, _time_patch):
    main_test = mock.Mock(parents_count=0)
    case = Case(methodName="test_method", parent=main_test)

    handler = ReportPortalHandler(main_test=main_test)
    handler.add_success(case)

    service_patch.return_value.finish_test_item.assert_called_once_with(
        end_time="123",
        status="PASSED"
    )


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_skipped_test(_configuration_patch, service_patch, _time_patch):
    main_test = mock.Mock(parents_count=0)
    case = Case(methodName="test_method", parent=main_test)

    handler = ReportPortalHandler(main_test=main_test)
    handler.add_skip(case, reason="Reason for skipping.")

    service_patch.return_value.finish_test_item.assert_called_once_with(
        end_time="123",
        status="SKIPPED",
        issue={"issue_type": "NO_DEFECT",
               "comment": "Reason for skipping."}
    )


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_failed_test(_configuration_patch, service_patch, _time_patch):
    main_test = mock.Mock(parents_count=0)
    case = Case(methodName="test_method", parent=main_test)

    handler = ReportPortalHandler(main_test=main_test)
    handler.add_failure(case, exception_string="Exception message.")

    service_patch.return_value.finish_test_item.assert_called_once_with(
        end_time="123",
        status="FAILED",
        issue={"issue_type": "PRODUCT_BUG",
               "comment": "Exception message."}
    )


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_error(_configuration_patch, service_patch, _time_patch):
    main_test = mock.Mock(parents_count=0)
    case = Case(methodName="test_method", parent=main_test)

    handler = ReportPortalHandler(main_test=main_test)
    handler.add_error(case, exception_string="Exception message.")

    service_patch.return_value.finish_test_item.assert_called_once_with(
        end_time="123",
        status="FAILED",
        issue={"issue_type": "AUTOMATION_BUG",
               "comment": "Exception message."}
    )


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_expected_failure(_configuration_patch, service_patch, _time_patch):
    main_test = mock.Mock(parents_count=0)
    case = Case(methodName="test_method", parent=main_test)

    handler = ReportPortalHandler(main_test=main_test)
    handler.add_expected_failure(case, exception_string="Exception message.")

    service_patch.return_value.finish_test_item.assert_called_once_with(
        end_time="123",
        status="PASSED"
    )


@mock.patch("rotest_reportportal.timestamp", return_value="123")
@mock.patch("rotest_reportportal.ReportPortalServiceAsync")
@mock.patch("rotest_reportportal.get_configuration")
def test_unexpected_success(_configuration_patch, service_patch, _time_patch):
    main_test = mock.Mock(parents_count=0)
    case = Case(methodName="test_method", parent=main_test)

    handler = ReportPortalHandler(main_test=main_test)
    handler.add_unexpected_success(case)

    service_patch.return_value.finish_test_item.assert_called_once_with(
        end_time="123",
        status="FAILED"
    )
