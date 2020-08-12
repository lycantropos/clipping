from enum import (IntEnum,
                  unique)


class Base(IntEnum):
    def __repr__(self) -> str:
        return type(self).__qualname__ + '.' + self._name_


@unique
class EdgeSide(Base):
    LEFT = 0
    RIGHT = 1


@unique
class Fill(Base):
    EVEN_ODD = 0
    NON_ZERO = 1
    POSITIVE = 2
    NEGATIVE = 3


@unique
class OperationKind(Base):
    INTERSECTION = 0
    UNION = 1
    DIFFERENCE = 2
    XOR = 3


@unique
class OperandKind(Base):
    SUBJECT = 0
    CLIP = 1


@unique
class PointInPolygonResult(IntEnum):
    ON = -1
    INSIDE = 0
    OUTSIDE = 1
