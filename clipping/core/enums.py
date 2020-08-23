from enum import (IntEnum,
                  unique)


@unique
class OverlapKind(IntEnum):
    NONE = 0
    SAME_ORIENTATION = 1
    DIFFERENT_ORIENTATION = 2
