from enum import Enum


class ThirdUserAction(Enum):
    END = 0
    START = 1
    CONTINUE = 2
    REPEAT = 3

class ThirdUserTypes(Enum):
    HUMAN_INVESTIGATOR = 0
