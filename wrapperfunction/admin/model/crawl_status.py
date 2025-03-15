from enum import Enum


class CrawlingStatus(Enum):
    INPROGRESS = "InProgress"
    SUCCESS = "Success"
    ERROR = "Error"