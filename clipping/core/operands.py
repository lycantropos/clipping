from abc import (ABC,
                 abstractmethod)
from typing import Union

from ground.hints import (Multipolygon,
                          Polygon)
from reprit.base import generate_repr


class HoleyOperand(ABC):
    __slots__ = 'polygons',

    @property
    @abstractmethod
    def value(self) -> Union[Multipolygon, Polygon]:
        """Returns value of the operand."""


class MultipolygonOperand(HoleyOperand):
    __slots__ = '_value',

    def __init__(self, value: Multipolygon) -> None:
        self._value, self.polygons = value, value.polygons

    __repr__ = generate_repr(__init__)

    @property
    def value(self) -> Multipolygon:
        return self._value


class PolygonOperand(HoleyOperand):
    __slots__ = '_value',

    def __init__(self, value: Polygon) -> None:
        self._value, self.polygons = value, [value]

    __repr__ = generate_repr(__init__)

    @property
    def value(self) -> Polygon:
        return self._value
