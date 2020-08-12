from .core.enums import (Fill,
                         OperationKind)
from .core.operation import execute
from .hints import Multipolygon


def intersect_multipolygons(left: Multipolygon,
                            right: Multipolygon,
                            *,
                            left_fill: Fill = Fill.EVEN_ODD,
                            right_fill: Fill = Fill.EVEN_ODD,
                            accurate: bool = True) -> Multipolygon:
    return execute(left, right, OperationKind.INTERSECTION, left_fill,
                   right_fill, accurate)


def subtract_multipolygons(minuend: Multipolygon,
                           subtrahend: Multipolygon,
                           *,
                           minuend_fill: Fill = Fill.EVEN_ODD,
                           subtrahend_fill: Fill = Fill.EVEN_ODD,
                           accurate: bool = True) -> Multipolygon:
    return execute(minuend, subtrahend, OperationKind.DIFFERENCE,
                   minuend_fill, subtrahend_fill, accurate)


def symmetric_subtract_multipolygons(left: Multipolygon,
                                     right: Multipolygon,
                                     *,
                                     left_fill: Fill = Fill.EVEN_ODD,
                                     right_fill: Fill = Fill.EVEN_ODD,
                                     accurate: bool = True) -> Multipolygon:
    return execute(left, right, OperationKind.XOR, left_fill,
                   right_fill, accurate)


def unite_multipolygons(subject: Multipolygon,
                        clip: Multipolygon,
                        left_fill: Fill = Fill.EVEN_ODD,
                        right_fill: Fill = Fill.EVEN_ODD,
                        accurate: bool = True) -> Multipolygon:
    return execute(subject, clip, OperationKind.UNION, left_fill,
                   right_fill, accurate)
