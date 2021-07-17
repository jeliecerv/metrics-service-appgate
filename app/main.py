import datetime
from typing import Optional

import pandas as pd
from fastapi import FastAPI, File, UploadFile
from fastapi.params import Query

from app.DTO.payloads import MetricsKey
from app.utils.parse_logs import parse_data_from_log

app = FastAPI()


@app.post("/log")
async def handling_log(log_file: UploadFile = File(...)):
    data = []
    for parsed_record in parse_data_from_log(
        log_file, "{date:date} {time:time} {module} {client_id} {message}"
    ):
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
    if metric_key in [
        MetricsKey.is_user_know,
        MetricsKey.last_successful_login_date,
        MetricsKey.last_failed_login_date,
    ]:
        df["indexes"] = df["message"].str.find(username)
        return any(df.loc[df.indexes > -1].any())
    elif metric_key in [MetricsKey.is_ip_know, MetricsKey.is_ip_internal]:
        df["indexes"] = df["message"].str.find(ip)
        return any(df.loc[df.indexes > -1].any())
    elif metric_key in [MetricsKey.is_client_know]:
        df["indexes"] = df["message"].str.find(client_id)
    else:
        pass
    return {"message": "Hello World"}
