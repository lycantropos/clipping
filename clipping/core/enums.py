from enum import (IntEnum,
                  unique)


@unique
class EdgeType(IntEnum):
    NORMAL = 0
    NON_CONTRIBUTING = 1
    SAME_TRANSITION = 2
    DIFFERENT_TRANSITION = 3
