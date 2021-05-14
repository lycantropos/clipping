from abc import (ABC,
                 abstractmethod)
from typing import Union

from ground.hints import (Multipolygon,
                          Multisegment,
                          Polygon,
                          Segment)
from reprit.base import generate_repr

from .hints import (Multiregion,
                    Region)


class LinearOperand(ABC):
    __slots__ = 'segments',

    @property
    @abstractmethod
    def value(self) -> Union[Multisegment, Segment]:
        """Returns value of the operand."""


class MultisegmentOperand(LinearOperand):
    __slots__ = '_value'

    def __init__(self, value: Multisegment) -> None:
        self.segments, self._value = value.segments, value

    @property
    def value(self) -> Multisegment:
        return self._value


class SegmentOperand(LinearOperand):
    __slots__ = '_value'

    def __init__(self, value: Segment) -> None:
        self.segments, self._value = [value], value

    @property
    def value(self) -> Segment:
        return self._value


class HolelessOperand(ABC):
    __slots__ = 'regions',

    @property
    @abstractmethod
    def value(self) -> Union[Multiregion, Region]:
        """Returns value of the operand."""


class MultiregionOperand(HolelessOperand):
    __slots__ = '_value',

    def __init__(self, value: Multiregion) -> None:
        self._value, self.regions = value, value

    __repr__ = generate_repr(__init__)

    @property
    def value(self) -> Multiregion:
        return self._value


class RegionOperand(HolelessOperand):
    __slots__ = '_value',

    def __init__(self, value: Region) -> None:
        self._value, self.regions = value, [value]

    __repr__ = generate_repr(__init__)

    @property
    def value(self) -> Region:
        return self._value


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
