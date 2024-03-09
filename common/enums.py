from enum import Enum


class TaskStatus(str, Enum):
    active = 'Active'
    finished = 'Finished'
