from typing import (Callable,
                    Sequence,
                    Tuple)

from ground.base import Orientation
from ground.hints import (Contour as _Contour,
                          Point as _Point)

SegmentEndpoints = Tuple[_Point, _Point]
Region = _Contour
Multiregion = Sequence[Region]
Orienteer = Callable[[_Point, _Point, _Point], Orientation]
