import datetime
import tempfile

from app.utils.parse_logs import (
    parse_data_from_log,
    parse_logging_date,
    parse_logging_time,
)


def test_parse_logging_date():
    date_parse = parse_logging_date("20140616")
    assert date_parse == datetime.datetime(2014, 6, 16)


def test_parse_logging_time():
    time_parse = parse_logging_time("07:29:16")
    assert time_parse.time() == datetime.time(hour=7, minute=29, second=16)


def test_parse_data_from_log():
    data = []
    f = open("app/tests/mocks/mock_log.txt", "r")
    spool_max_size = 1024 * 1024
    fp = tempfile.SpooledTemporaryFile(
        max_size=spool_max_size,
        mode="rb+",
    )
    fp.write(f.read().encode("utf-8"))
    fp.seek(0)
    for parsed_record in parse_data_from_log(
        fp, "{date:date} {time:time} {module} {client_id} {message}"
    ):
        data.append(parsed_record)
    fp.close()
    f.close()
    assert len(data) == 56
    assert "date" in data[0]
