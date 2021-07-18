import datetime
from typing import Optional

import pandas as pd
from fastapi import Depends, FastAPI, File, UploadFile, HTTPException
from fastapi.params import Query

from app.DTO.payloads import LogsHandling, MetricsKey
from app.utils.parse_logs import parse_data_from_log
from app.utils.search_metrics import search_metrics

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
    for parsed_record in parse_data_from_log(log_file.file, logs_handling.logs_format):
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


@app.get(
    "/metrics/{metric_key}",
    description="Return metrics for logs",
)
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

    try:
        return search_metrics(df, metric_key, username, ip, client_id)
    except Exception as error:
        raise HTTPException(status_code=400, detail="{}".format(error))
