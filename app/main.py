import datetime
from typing import Optional

import pandas as pd
from fastapi import Depends, FastAPI, File, UploadFile
from fastapi.params import Query

from app.DTO.payloads import LogsHandling, MetricsKey
from app.utils.parse_logs import parse_data_from_log
from app.utils.constants import INTERNAL_IPS

app = FastAPI()


@app.post(
    "/log",
    description="Handling all the raw text logs",
)
async def handling_log(
    logs_handling: LogsHandling = Depends(LogsHandling),
    log_file: UploadFile = File(...),
):
    data = []
    for parsed_record in parse_data_from_log(log_file, logs_handling.logs_format):
        data.append(
            {
                "datetime": datetime.datetime.combine(
                    parsed_record["date"], parsed_record["time"].time()
                ),
                "client_id": parsed_record["client_id"],
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
    client_id: Optional[str] = None,
):
    df = pd.read_csv("data/data.csv")
    df["datetime"] = pd.to_datetime(df["datetime"])

    if metric_key in [MetricsKey.is_user_know]:
        df["indexes"] = df["message"].str.find(username)
        return any(df.loc[df.indexes > -1].any())

    if metric_key in [MetricsKey.is_ip_know]:
        df["indexes"] = df["message"].str.find(ip)
        return any(df.loc[df.indexes > -1].any())

    if metric_key in [MetricsKey.is_ip_internal]:
        df["indexes"] = df["message"].str.find(ip)
        if any(df.loc[df.indexes > -1].any()):
            return ip in INTERNAL_IPS

    if metric_key in [MetricsKey.is_client_know]:
        df["indexes"] = df["message"].str.find(client_id)
        return any(df.loc[df.indexes > -1].any())

    if metric_key in [MetricsKey.last_successful_login_date]:
        df["indexes"] = df["message"].str.find(username)
        df["indexes"] = df.loc[df.indexes > -1]["message"].str.find("policy_login")
        df = df.loc[df.indexes > -1].sort_values(
            by=["datetime"], inplace=False, ascending=False
        )
        if any(df.loc[df.indexes > -1].any()):
            return df.iloc[0].datetime
        else:
            return "Is not login yet"

    if metric_key in [MetricsKey.last_failed_login_date]:
        df["indexes"] = df["message"].str.find(username)
        df["indexes"] = df.loc[df.indexes > -1]["message"].str.find("Failed")
        df = df.loc[df.indexes > -1].sort_values(
            by=["datetime"], inplace=False, ascending=False
        )
        if any(df.loc[df.indexes > -1].any()):
            return df.iloc[0].datetime
        else:
            return "Is not login yet"

    if metric_key in [MetricsKey.failed_login_count_last_week]:
        today = datetime.datetime.today()
        start_delta = datetime.timedelta(weeks=1)
        start_of_week = today - start_delta
        df = df.loc[df.datetime > start_of_week]
        df["indexes"] = df["message"].str.find("Failed")
        df = df.loc[df.indexes > -1]
        return df.count()
