from collections import defaultdict
from datetime import timedelta
from typing import Dict, List

from constants import ReportRowProto


class ReportBuilder:
    def __init__(self):
        self.__report = defaultdict(list)

    def add(self, row: ReportRowProto) -> None:
        self.__report[row.user_name].append({row.task_name: format_timedelta(row.duration)})

    def get(self) -> Dict[str, List[Dict[str, str]]]:
        return self.__report


def format_timedelta(duration: timedelta) -> str:
    formatted = ''
    days = duration.days
    seconds = duration.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if days:
        formatted += f"{days} days"

    if hours:
        formatted += f"{hours} hours"

    if minutes or not formatted:
        formatted += f"{minutes} minutes"

    return formatted
