import datetime

import pandas as pd
from app.DTO.payloads import MetricsKey
from app.utils.constants import INTERNAL_IPS


def _validate_params(metric_key: MetricsKey, username: str, ip: str, client_id: str):
    if metric_key in [
        MetricsKey.is_user_know,
        MetricsKey.last_successful_login_date,
        MetricsKey.last_failed_login_date,
    ]:
        if username is None:
            raise Exception("Not valid username param")

    if metric_key in [
        MetricsKey.is_ip_know,
        MetricsKey.is_ip_internal,
    ]:
        if ip is None:
            raise Exception("Not valid ip param")

    if metric_key in [MetricsKey.is_client_know]:
        if client_id is None:
            raise Exception("Not valid client_id param")

    if metric_key == MetricsKey.all_metrics:
        if username is None or ip is None or client_id is None:
            raise Exception("Some params are not valid")


def search_metrics(
    df: pd.DataFrame, metric_key: MetricsKey, username: str, ip: str, client_id: str
):
    try:
        _validate_params(metric_key, username, ip, client_id)
    except Exception as e:
        raise Exception(e)

    result = {
        MetricsKey.is_user_know.value: None,
        MetricsKey.is_client_know: None,
        MetricsKey.is_ip_know: None,
        MetricsKey.is_ip_internal: None,
        MetricsKey.last_successful_login_date: None,
        MetricsKey.last_failed_login_date: None,
        MetricsKey.failed_login_count_last_week: None,
    }

    if metric_key in [MetricsKey.is_user_know, MetricsKey.all_metrics]:
        df["indexes"] = df["message"].str.find(username)
        result[MetricsKey.is_user_know.value] = any(df.loc[df.indexes > -1].any())

    if metric_key in [MetricsKey.is_ip_know, MetricsKey.all_metrics]:
        df["indexes"] = df["message"].str.find(ip)
        result[MetricsKey.is_ip_know.value] = any(df.loc[df.indexes > -1].any())

    if metric_key in [MetricsKey.is_ip_internal, MetricsKey.all_metrics]:
        df["indexes"] = df["message"].str.find(ip)
        if any(df.loc[df.indexes > -1].any()):
            result[MetricsKey.is_ip_internal.value] = ip in INTERNAL_IPS
        else:
            result[MetricsKey.is_ip_internal.value] = False

    if metric_key in [MetricsKey.is_client_know, MetricsKey.all_metrics]:
        df["indexes"] = df["message"].str.find(client_id)
        result[MetricsKey.is_client_know.value] = any(df.loc[df.indexes > -1].any())

    if metric_key in [MetricsKey.last_successful_login_date, MetricsKey.all_metrics]:
        df["indexes"] = df["message"].str.find(username)
        df["indexes"] = df.loc[df.indexes > -1]["message"].str.find("policy_login")
        df = df.loc[df.indexes > -1].sort_values(
            by=["datetime"], inplace=False, ascending=False
        )
        if any(df.loc[df.indexes > -1].any()):
            result[MetricsKey.last_successful_login_date.value] = df.iloc[0].datetime
        else:
            result[MetricsKey.last_successful_login_date.value] = "Is not login yet"

    if metric_key in [MetricsKey.last_failed_login_date, MetricsKey.all_metrics]:
        df["indexes"] = df["message"].str.find(username)
        df["indexes"] = df.loc[df.indexes > -1]["message"].str.find("Failed")
        df = df.loc[df.indexes > -1].sort_values(
            by=["datetime"], inplace=False, ascending=False
        )
        if any(df.loc[df.indexes > -1].any()):
            result[MetricsKey.last_failed_login_date.value] = df.iloc[0].datetime
        else:
            result[MetricsKey.last_failed_login_date.value] = "Is not failed login yet"

    if metric_key in [MetricsKey.failed_login_count_last_week, MetricsKey.all_metrics]:
        today = datetime.datetime.today()
        start_delta = datetime.timedelta(weeks=1)
        start_of_week = today - start_delta
        df = df.loc[df.datetime > start_of_week]
        df["indexes"] = df["message"].str.find("Failed")
        df = df.loc[df.indexes > -1]
        result[MetricsKey.failed_login_count_last_week.value] = len(df)

    if metric_key == MetricsKey.all_metrics:
        return result
    else:
        return result[metric_key.value]
