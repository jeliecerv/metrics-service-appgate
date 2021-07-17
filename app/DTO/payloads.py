from enum import Enum

from fastapi.params import Query
from pydantic import BaseModel


class MetricsKey(str, Enum):
    is_user_know = "IsUserKnown".lower()
    is_client_know = "IsClientKnown".lower()
    is_ip_know = "IsIPKnown".lower()
    is_ip_internal = "IsIPInternal".lower()
    last_successful_login_date = "LastSuccessfulLoginDate".lower()
    last_failed_login_date = "LastFailedLoginDate".lower()
    failed_login_count_last_week = "FailedLoginCountLastWeek".lower()


class LogsHandling(BaseModel):
    logs_format: str = Query(
        str("{date:date} {time:time} {module} {client_id} {message}"),
        example=str("{date:date} {time:time} {module} {client_id} {message}"),
        description="follow the format given by the parse module (https://pypi.org/project/parse/)",
    )
