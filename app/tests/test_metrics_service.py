from app.DTO.payloads import MetricsKey
import datetime
import pytest


def test_log(client):
    files = {
        "log_file": (
            "mock_log",
            open("app/tests/mocks/mock_log.txt", "rb"),
            "text/plain",
        )
    }
    response = client.post("/log", files=files)
    assert response.status_code == 200
    assert response.json() == {"filename": "mock_log"}


@pytest.mark.run(after="test_log")
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
            "2014-06-16T05:44:49",
        ),
        (
            MetricsKey.last_failed_login_date,
            "admin",
            None,
            None,
            "2014-06-16T05:44:49",
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
                "lastsuccessfullogindate": "2014-06-16T05:44:49",
                "lastfailedlogindate": "Is not failed login yet",
                "failedlogincountlastweek": 0,
            },
        ),
    ],
)
def test_metrics(client, metric, username, ip, client_id, expected):
    params = {
        "username": username,
        "ip": ip,
        "client_id": client_id,
    }
    response = client.get(f"/metrics/{metric}", params=params)
    assert response.status_code == 200
    assert response.json() == expected
