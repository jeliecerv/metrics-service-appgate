from enum import Enum


class MetricsKey(str, Enum):
    is_user_know = "IsUserKnown".lower()
    is_client_know = "IsClientKnown".lower()
    is_ip_know = "IsIPKnown".lower()
    is_ip_internal = "IsIPInternal".lower()
    last_successful_login_date = "LastSuccessfulLoginDate".lower()
    last_failed_login_date = "LastFailedLoginDate".lower()
    failed_login_count_last_week = "FailedLoginCountLastWeek".lower()
