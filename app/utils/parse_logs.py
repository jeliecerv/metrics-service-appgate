import datetime

from boltons.tbutils import ParsedException
from fastapi import File
from parse import parse, with_pattern

from .constants import DEFAULT_DATE, DEFAULT_TIME


@with_pattern(r"\d\d\d\d\d\d\d\d")
def parse_logging_date(raw):
    return datetime.datetime.strptime(raw, DEFAULT_DATE)


@with_pattern(r"\d\d:\d\d:\d\d")
def parse_logging_time(raw):
    return datetime.datetime.strptime(raw, DEFAULT_TIME)


def parse_data_from_log(log_file: File, format: str):
    chunk = ""
    custom_parsers = {"date": parse_logging_date, "time": parse_logging_time}

    for line in log_file.file.readlines():
        line_str = line.decode("utf-8")
        parsed = parse(format, line_str, custom_parsers)
        if parsed is not None:
            yield parsed
        else:  # try parsing the stacktrace
            chunk += line_str
            try:
                yield ParsedException.from_string(chunk)
                chunk = ""
            except (IndexError, ValueError):
                pass
