from typing import (Callable,
                    Tuple)

from ground.base import Orientation

from clipping.hints import (Coordinate,
                            Point)

BoundingBox = Tuple[Coordinate, Coordinate, Coordinate, Coordinate]
Orienteer = Callable[[Point, Point, Point], Orientation]
