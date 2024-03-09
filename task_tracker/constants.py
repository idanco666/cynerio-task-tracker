from datetime import timedelta
from typing import Protocol


class ReportRowProto(Protocol):
    user_name: str
    task_name: str
    duration: timedelta
