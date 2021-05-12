from abc import (ABC,
                 abstractmethod)
from typing import Union as Union_

from ground.hints import (Multipolygon,
                          Polygon)


class ShapedOperand(ABC):
    __slots__ = 'polygons',

    @property
    @abstractmethod
    def value(self) -> Union_[Multipolygon, Polygon]:
        """Returns value of the operand."""


class MultipolygonOperand(ShapedOperand):
    __slots__ = '_value',

    def __init__(self, value: Multipolygon) -> None:
        self._value, self.polygons = value, value.polygons

    @property
    def value(self) -> Multipolygon:
        return self._value


class PolygonOperand(ShapedOperand):
    __slots__ = '_value',

    def __init__(self, value: Polygon) -> None:
        self._value, self.polygons = value, [value]

    @property
    def value(self) -> Polygon:
        return self._value
