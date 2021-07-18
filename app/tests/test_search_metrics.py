from app.DTO.payloads import MetricsKey
import datetime
import pytest
import pandas as pd

from app.utils.search_metrics import (
    _validate_params,
    search_metrics,
)


@pytest.mark.parametrize(
    "metric,username,ip,client_id,expected",
    [
        (MetricsKey.is_user_know, None, None, None, "Not valid username param"),
        (
            MetricsKey.last_successful_login_date,
            None,
            None,
            None,
            "Not valid username param",
        ),
        (
            MetricsKey.last_failed_login_date,
            None,
            None,
            None,
            "Not valid username param",
        ),
        (MetricsKey.is_ip_know, None, None, None, "Not valid ip param"),
        (MetricsKey.is_ip_internal, None, None, None, "Not valid ip param"),
        (MetricsKey.is_client_know, None, None, None, "Not valid client_id param"),
        (MetricsKey.all_metrics, None, None, None, "Some params are not valid"),
    ],
)
def test_validate_params_exceptions(metric, username, ip, client_id, expected):
    with pytest.raises(Exception) as excinfo:
        _validate_params(metric, username, ip, client_id)
    assert expected in str(excinfo.value)


@pytest.mark.parametrize(
    "metric,username,ip,client_id,expected",
    [
        (MetricsKey.is_user_know, "root", None, None, None),
        (
            MetricsKey.last_successful_login_date,
            "root",
            None,
            None,
            None,
        ),
        (
            MetricsKey.last_failed_login_date,
            "root",
            None,
            None,
            None,
        ),
        (MetricsKey.is_ip_know, None, "127.0.0.1", None, None),
        (MetricsKey.is_ip_internal, None, "127.0.0.1", None, None),
        (MetricsKey.is_client_know, None, None, "123456", None),
        (MetricsKey.all_metrics, "root", "127.0.0.1", "123456", None),
    ],
)
def test_validate_params(metric, username, ip, client_id, expected):
    result = _validate_params(metric, username, ip, client_id)
    assert expected == result


@pytest.mark.parametrize(
    "metric,username,ip,client_id,expected",
    [
        (MetricsKey.is_user_know, "root", None, None, True),
        (MetricsKey.is_user_know, "doejhoe", None, None, False),
        (
            MetricsKey.last_successful_login_date,
            "admin",
            None,
            None,
            datetime.datetime(2014, 6, 16, 5, 44, 49),
        ),
        (
            MetricsKey.last_failed_login_date,
            "admin",
            None,
            None,
            datetime.datetime(2014, 6, 16, 5, 44, 49),
        ),
        (MetricsKey.is_ip_know, None, "61.174.51.202", None, True),
        (MetricsKey.is_ip_internal, None, "61.174.51.202", None, False),
        (MetricsKey.is_ip_internal, None, "192.168.1.207", None, True),
        (MetricsKey.is_client_know, None, None, "533e2272", True),
        (MetricsKey.is_client_know, None, None, "123456789", False),
        (
            MetricsKey.all_metrics,
            "admin",
            "192.168.1.207",
            "4f8a7f94",
            {
                "isuserknown": True,
                "isclientknown": True,
                "isipknown": True,
                "isipinternal": True,
                "lastsuccessfullogindate": datetime.datetime(2014, 6, 16, 5, 44, 49),
                "lastfailedlogindate": "Is not failed login yet",
                "failedlogincountlastweek": 0,
            },
        ),
    ],
)
def test_search_metrics(metric, username, ip, client_id, expected):
    df = pd.read_csv("app/tests/mocks/mock_data.csv")
    df["datetime"] = pd.to_datetime(df["datetime"])
    result = search_metrics(df, metric, username, ip, client_id)
    assert result == expected
