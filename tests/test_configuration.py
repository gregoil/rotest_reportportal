import mock
import pytest

from rotest_reportportal import get_configuration


@mock.patch.dict("os.environ",
                 {"ROTEST_REPORTPORTAL_TOKEN": "token"})
@mock.patch("rotest_reportportal.open")
@mock.patch("rotest_reportportal.search_config_file")
def test_configuration_fetching(search_config_patch, open_patch):
    search_config_patch.return_value = "rotest.yaml"
    mock.mock_open(open_patch, read_data="""\
        rotest:
            whatever_key: whatever_value

        reportportal:
            endpoint: http://host:8000
            project: nightly
    """)

    configuration = get_configuration()

    assert configuration.endpoint == "http://host:8000"
    assert configuration.project == "nightly"
    assert configuration.token == "token"


@mock.patch("rotest_reportportal.open")
@mock.patch("rotest_reportportal.search_config_file")
def test_missing_configuration(search_config_patch, open_patch):
    search_config_patch.return_value = "rotest.yaml"
    mock.mock_open(open_patch, read_data="""\
        rotest:
            whatever_key: whatever_value
    """)

    with pytest.raises(ValueError, match="No 'reportportal' key is defined"):
        get_configuration()


@mock.patch("rotest_reportportal.open")
@mock.patch("rotest_reportportal.search_config_file")
def test_missing_token(search_config_patch, open_patch):
    search_config_patch.return_value = "rotest.yaml"
    mock.mock_open(open_patch, read_data="""\
        rotest:
            whatever_key: whatever_value

        reportportal:
            endpoint: http://host:8000
            project: nightly
    """)

    with pytest.raises(ValueError,
                       match="You need to define the environment variable .* "
                             "in order to access Report Portal"):
        get_configuration()
