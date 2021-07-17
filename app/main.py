import datetime
from enum import Enum
from typing import Optional
from fastapi.params import Query

import pandas as pd
from boltons.tbutils import ParsedException
from fastapi import FastAPI, File, UploadFile
from parse import parse, with_pattern

app = FastAPI()

DEFAULT_DATE = "%Y%m%d"
DEFAULT_TIME = "%H:%M:%S"


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


class MetricsKey(str, Enum):
    is_user_know = "IsUserKnown".lower()
    is_client_know = "IsClientKnown".lower()
    is_ip_know = "IsIPKnown".lower()
    is_ip_internal = "IsIPInternal".lower()
    last_successful_login_date = "LastSuccessfulLoginDate".lower()
    last_failed_login_date = "LastFailedLoginDate".lower()
    failed_login_count_last_week = "FailedLoginCountLastWeek".lower()


@app.post("/log")
async def handling_log(log_file: UploadFile = File(...)):
    data = []
    for parsed_record in parse_data_from_log(
        log_file, "{date:date} {time:time} {module} {log_id} {message}"
    ):
        data.append(
            {
                "datetime": datetime.datetime.combine(
                    parsed_record["date"], parsed_record["time"].time()
                ),
                "log_id": parsed_record["log_id"],
                "message": parsed_record["message"].strip(),
            }
        )
    df = pd.DataFrame(data)
    df.to_csv("data/data.csv", index=False)
    return {"filename": log_file.filename}


@app.get("/metrics/{metric_key}")
async def metrics(
    metric_key: MetricsKey,
    username: Optional[str] = Query(None, min_length=1),
    ip: Optional[str] = Query(
        None,
        min_length=7,
        max_length=15,
        regex="^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
    ),
):
    df = pd.read_csv("data/data.csv")
    df["indexes"] = df["message"].str.find("UserA")
    return {"message": "Hello World"}
