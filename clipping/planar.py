"""
Boolean operations on geometries in the plane.

Based on algorithm by F. Martinez et al.

Reference:
    https://doi.org/10.1016/j.advengsoft.2013.04.004
    http://www4.ujaen.es/~fmartin/bool_op.html

########
Glossary
########

**Region** --- contour with points that lie within it.

**Multiregion** --- sequence of two or more regions
such that intersection of distinct regions is a discrete points set.
"""
from typing import (Optional as _Optional,
                    Sequence as _Sequence,
                    Union as _Union)

from ground.base import (Context as _Context,
                         get_context as _get_context)
from ground.hints import (Empty as _Empty,
                          Mix as _Mix,
                          Multipoint as _Multipoint,
                          Multipolygon as _Multipolygon,
                          Multisegment as _Multisegment,
                          Polygon as _Polygon,
                          Segment as _Segment)

from .core import (holeless as _holeless,
                   holey as _holey,
                   linear as _linear,
                   mixed as _mixed,
                   operands as _operands)
from .hints import (Multiregion as _Multiregion,
                    Region as _Region)


def intersect_segments(first: _Segment,
                       second: _Segment,
                       *,
                       context: _Optional[_Context] = None
                       ) -> _Union[_Empty, _Multipoint, _Segment]:
    """
    Returns intersection of segments.

    Time complexity:
        ``O(1)``
    Memory complexity:
        ``O(1)``

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Multipoint = context.multipoint_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (intersect_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                     Segment(Point(6, 0), Point(10, 0)))
    ...  is EMPTY)
    True
    >>> (intersect_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                     Segment(Point(4, 0), Point(8, 0)))
    ...  == Multipoint([Point(4, 0)]))
    True
    >>> (intersect_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                     Segment(Point(2, 0), Point(6, 0)))
    ...  == Segment(Point(2, 0), Point(4, 0)))
    True
    """
    return _linear.intersect_segments(
            first, second, _get_context() if context is None else context)


def subtract_segments(minuend: _Segment,
                      subtrahend: _Segment,
                      *,
                      context: _Optional[_Context] = None
                      ) -> _Union[_Empty, _Multisegment, _Segment]:
    """
    Returns difference of segments.

    Time complexity:
        ``O(1)``
    Memory complexity:
        ``O(1)``

    :param minuend: segment to subtract from.
    :param subtrahend: segment to subtract.
    :param context: geometric context.
    :returns: difference of minuend with subtrahend.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (subtract_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 0)))
    ...  is subtract_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                       Segment(Point(0, 0), Point(6, 0)))
    ...  is EMPTY)
    True
    >>> (subtract_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(2, 0), Point(6, 0)))
    ...  == Segment(Point(0, 0), Point(2, 0)))
    True
    >>> (subtract_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(6, 0), Point(10, 0)))
    ...  == subtract_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                       Segment(Point(4, 0), Point(8, 0)))
    ...  == Segment(Point(0, 0), Point(4, 0)))
    True
    >>> (subtract_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(1, 0), Point(3, 0)))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(3, 0), Point(4, 0))]))
    True
    """
    return _linear.subtract_segments(
            minuend, subtrahend,
            _get_context() if context is None else context)


def symmetric_subtract_segments(first: _Segment,
                                second: _Segment,
                                *,
                                context: _Optional[_Context] = None
                                ) -> _Union[_Empty, _Multisegment, _Segment]:
    """
    Returns symmetric difference of segments.

    Time complexity:
        ``O(1)``
    Memory complexity:
        ``O(1)``

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: symmetric difference of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (symmetric_subtract_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                              Segment(Point(0, 0), Point(4, 0)))
    ...  is EMPTY)
    True
    >>> (symmetric_subtract_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                              Segment(Point(4, 0), Point(8, 0)))
    ...  == Segment(Point(0, 0), Point(8, 0)))
    True
    >>> (symmetric_subtract_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                              Segment(Point(1, 0), Point(3, 0)))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(3, 0), Point(4, 0))]))
    True
    >>> (symmetric_subtract_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                              Segment(Point(2, 0), Point(6, 0)))
    ...  == Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                   Segment(Point(4, 0), Point(6, 0))]))
    True
    >>> (symmetric_subtract_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                              Segment(Point(6, 0), Point(10, 0)))
    ...  == Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                   Segment(Point(6, 0), Point(10, 0))]))
    True
    """
    return _linear.symmetric_subtract_segments(
            first, second, _get_context() if context is None else context)


def unite_segments(first: _Segment,
                   second: _Segment,
                   *,
                   context: _Optional[_Context] = None
                   ) -> _Union[_Multisegment, _Segment]:
    """
    Returns union of segments.

    Time complexity:
        ``O(1)``
    Memory complexity:
        ``O(1)``

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: union of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (unite_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                 Segment(Point(0, 0), Point(4, 0)))
    ...  == unite_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(1, 0), Point(3, 0)))
    ...  == Segment(Point(0, 0), Point(4, 0)))
    True
    >>> (unite_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                 Segment(Point(4, 0), Point(8, 0)))
    ...  == Segment(Point(0, 0), Point(8, 0)))
    True
    >>> (unite_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                 Segment(Point(2, 0), Point(6, 0)))
    ...  == Segment(Point(0, 0), Point(6, 0)))
    True
    >>> (unite_segments(Segment(Point(0, 0), Point(4, 0)),
    ...                 Segment(Point(6, 0), Point(10, 0)))
    ...  == Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                   Segment(Point(6, 0), Point(10, 0))]))
    True
    """
    return _linear.unite_segments(
            first, second, _get_context() if context is None else context)


def complete_intersect_segment_with_multisegment(
        segment: _Segment,
        multisegment: _Multisegment,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Mix, _Multipoint, _Multisegment, _Segment]:
    """
    Returns intersection of segments.

    Time complexity:
        ``O(len(multisegment.segments))``
    Memory complexity:
        ``O(len(multisegment.segments))``

    :param segment: first operand.
    :param multisegment: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Mix = context.mix_cls
    >>> Multipoint = context.multipoint_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (complete_intersect_segment_with_multisegment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(6, 0), Point(10, 0)),
    ...                    Segment(Point(6, 0), Point(6, 4))]))
    ...  is EMPTY)
    True
    >>> (complete_intersect_segment_with_multisegment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(4, 0), Point(8, 0)),
    ...                    Segment(Point(4, 0), Point(4, 4))]))
    ...  == Multipoint([Point(4, 0)]))
    True
    >>> (complete_intersect_segment_with_multisegment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(0, 4))]))
    ...  == Segment(Point(0, 0), Point(4, 0)))
    True
    >>> (complete_intersect_segment_with_multisegment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(3, 0), Point(4, 0))]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(3, 0), Point(4, 0))]))
    True
    >>> (complete_intersect_segment_with_multisegment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(2, 0), Point(2, 1)),
    ...                    Segment(Point(3, 0), Point(4, 0))]))
    ...  == Mix(Multipoint([Point(2, 0)]),
    ...         Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                       Segment(Point(3, 0), Point(4, 0))]), EMPTY))
    True
    """
    return _linear.complete_intersect_segment_with_multisegment(
            segment, multisegment,
            _get_context() if context is None else context)


def intersect_segment_with_multisegment(
        segment: _Segment,
        multisegment: _Multisegment,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Mix, _Multipoint, _Multisegment, _Segment]:
    """
    Returns intersection of segments.

    Time complexity:
        ``O(len(multisegment.segments))``
    Memory complexity:
        ``O(len(multisegment.segments))``

    :param segment: first operand.
    :param multisegment: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (intersect_segment_with_multisegment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(6, 0), Point(10, 0)),
    ...                    Segment(Point(6, 0), Point(6, 4))]))
    ...  is intersect_segment_with_multisegment(
    ...          Segment(Point(0, 0), Point(4, 0)),
    ...          Multisegment([Segment(Point(4, 0), Point(8, 0)),
    ...                        Segment(Point(4, 0), Point(4, 4))]))
    ... is EMPTY)
    True
    >>> (intersect_segment_with_multisegment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(0, 4))]))
    ...  == Segment(Point(0, 0), Point(4, 0)))
    True
    >>> (intersect_segment_with_multisegment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(3, 0), Point(4, 0))]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(3, 0), Point(4, 0))]))
    True
    >>> (intersect_segment_with_multisegment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(2, 0), Point(2, 1)),
    ...                    Segment(Point(3, 0), Point(4, 0))]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(3, 0), Point(4, 0))]))
    True
    """
    return _linear.intersect_segment_with_multisegment(
            segment, multisegment,
            _get_context() if context is None else context)


def subtract_multisegment_from_segment(
        minuend: _Segment,
        subtrahend: _Multisegment,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Multisegment, _Segment]:
    """
    Returns difference of segment with multisegment.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = segments_count + intersections_count``,
    ``segments_count = len(subtrahend.segments) + 1``,
    ``intersections_count`` --- number of intersections between segments.

    :param minuend: segment to subtract from.
    :param subtrahend: multisegment to subtract.
    :param context: geometric context.
    :returns: difference of minuend with subtrahend.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (subtract_multisegment_from_segment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 1), Point(0, 3))]))
    ...  is subtract_multisegment_from_segment(
    ...          Segment(Point(0, 0), Point(4, 0)),
    ...          Multisegment([Segment(Point(0, 0), Point(6, 0)),
    ...                        Segment(Point(0, 1), Point(0, 3))]))
    ...  is EMPTY)
    True
    >>> (subtract_multisegment_from_segment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(2, 0), Point(4, 0)),
    ...                    Segment(Point(0, 1), Point(0, 3))]))
    ...  == Segment(Point(0, 0), Point(2, 0)))
    True
    >>> (subtract_multisegment_from_segment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(3, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(1, 0))]))
    ...  == Segment(Point(1, 0), Point(3, 0)))
    True
    >>> (subtract_multisegment_from_segment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(6, 0), Point(10, 0)),
    ...                    Segment(Point(0, 1), Point(0, 3))]))
    ...  == subtract_multisegment_from_segment(
    ...          Segment(Point(0, 0), Point(4, 0)),
    ...          Multisegment([Segment(Point(4, 0), Point(8, 0)),
    ...                        Segment(Point(0, 1), Point(0, 3))]))
    ...  == Segment(Point(0, 0), Point(4, 0)))
    True
    >>> (subtract_multisegment_from_segment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(1, 0), Point(3, 0)),
    ...                    Segment(Point(0, 1), Point(0, 3))]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(3, 0), Point(4, 0))]))
    True
    """
    return (_linear.Difference(_operands.SegmentOperand(minuend),
                               _operands.MultisegmentOperand(subtrahend),
                               _get_context() if context is None else context)
            .compute())


def subtract_segment_from_multisegment(
        minuend: _Multisegment,
        subtrahend: _Segment,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Multisegment, _Segment]:
    """
    Returns difference of segment with multisegment.

    Time complexity:
        ``O(len(subtrahend.segments))``
    Memory complexity:
        ``O(len(subtrahend.segments))``

    :param minuend: multisegment to subtract from.
    :param subtrahend: segment to subtract.
    :param context: geometric context.
    :returns: difference of minuend with subtrahend.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (subtract_segment_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(3, 0), Point(4, 0))]),
    ...      Segment(Point(0, 0), Point(4, 0)))
    ...  is subtract_segment_from_multisegment(
    ...          Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                        Segment(Point(3, 0), Point(4, 0))]),
    ...          Segment(Point(0, 0), Point(6, 0)))
    ...  is EMPTY)
    True
    >>> (subtract_segment_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                    Segment(Point(0, 1), Point(0, 3))]),
    ...      Segment(Point(0, 1), Point(0, 3)))
    ...  == subtract_segment_from_multisegment(
    ...          Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                        Segment(Point(3, 0), Point(4, 0))]),
    ...          Segment(Point(2, 0), Point(4, 0)))
    ...  == Segment(Point(0, 0), Point(2, 0)))
    True
    >>> (subtract_segment_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(3, 0), Point(4, 0))]),
    ...      Segment(Point(1, 0), Point(3, 0)))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(3, 0), Point(4, 0))]))
    True
    >>> (subtract_segment_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 1), Point(0, 3))]),
    ...      Segment(Point(1, 0), Point(3, 0)))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(3, 0), Point(4, 0)),
    ...                   Segment(Point(0, 1), Point(0, 3))]))
    True
    """
    return _linear.subtract_segment_from_multisegment(
            minuend, subtrahend,
            _get_context() if context is None else context)


def symmetric_subtract_multisegment_from_segment(
        first: _Segment,
        second: _Multisegment,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Multisegment, _Segment]:
    """
    Returns symmetric difference of segment and multisegment.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = segments_count + intersections_count``,
    ``segments_count = len(second.segments) + 1``,
    ``intersections_count`` --- number of intersections between segments.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: symmetric difference of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (symmetric_subtract_multisegment_from_segment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                    Segment(Point(2, 0), Point(4, 0))]))
    ...  is EMPTY)
    True
    >>> (symmetric_subtract_multisegment_from_segment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 1), Point(0, 3))]))
    ...  == Segment(Point(0, 1), Point(0, 3)))
    True
    >>> (symmetric_subtract_multisegment_from_segment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(3, 0), Point(4, 0))]))
    ...  == Segment(Point(1, 0), Point(3, 0)))
    True
    >>> (symmetric_subtract_multisegment_from_segment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(4, 0), Point(8, 0)),
    ...                    Segment(Point(0, 1), Point(0, 3))]))
    ...  == Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                   Segment(Point(0, 1), Point(0, 3)),
    ...                   Segment(Point(4, 0), Point(8, 0))]))
    True
    >>> (symmetric_subtract_multisegment_from_segment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(1, 0), Point(3, 0)),
    ...                    Segment(Point(0, 1), Point(0, 3))]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(0, 3)),
    ...                   Segment(Point(3, 0), Point(4, 0))]))
    True
    """
    return _linear.SymmetricDifference(
            _operands.SegmentOperand(first),
            _operands.MultisegmentOperand(second),
            _get_context() if context is None else context).compute()


def unite_segment_with_multisegment(first: _Segment,
                                    second: _Multisegment,
                                    *,
                                    context: _Optional[_Context] = None
                                    ) -> _Union[_Multisegment, _Segment]:
    """
    Returns symmetric difference of segment and multisegment.

    Time complexity:
        ``O(len(second.segments))``
    Memory complexity:
        ``O(len(second.segments))``

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: symmetric difference of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (unite_segment_with_multisegment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                    Segment(Point(2, 0), Point(4, 0))]))
    ...  == unite_segment_with_multisegment(
    ...          Segment(Point(0, 0), Point(4, 0)),
    ...          Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                        Segment(Point(3, 0), Point(4, 0))]))
    ...  == Segment(Point(0, 0), Point(4, 0)))
    True
    >>> (unite_segment_with_multisegment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 1), Point(0, 3))]))
    ...  == Multisegment([Segment(Point(0, 1), Point(0, 3)),
    ...                   Segment(Point(0, 0), Point(4, 0))]))
    True
    >>> (unite_segment_with_multisegment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multisegment([Segment(Point(4, 0), Point(8, 0)),
    ...                    Segment(Point(0, 1), Point(0, 3))]))
    ...  == Multisegment([Segment(Point(4, 0), Point(8, 0)),
    ...                   Segment(Point(0, 1), Point(0, 3)),
    ...                   Segment(Point(0, 0), Point(4, 0))]))
    True
    >>> (unite_segment_with_multisegment(
    ...      Segment(Point(1, 0), Point(3, 0)),
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 1), Point(0, 3))]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(3, 0), Point(4, 0)),
    ...                   Segment(Point(0, 1), Point(0, 3)),
    ...                   Segment(Point(1, 0), Point(3, 0))]))
    True
    """
    return _linear.unite_segment_with_multisegment(
            first, second, _get_context() if context is None else context)


def complete_intersect_segment_with_polygon(
        segment: _Segment,
        polygon: _Polygon,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Mix, _Multipoint, _Multisegment, _Segment]:
    """
    Returns intersection of segment with polygon
    considering cases with geometries touching each other in points.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = polygon_edges_count + 1``,
    ``polygon_edges_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``,
    ``intersections_count`` --- number of intersections between segment
    and polygon edges.

    :param segment: first operand.
    :param polygon: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Mix = context.mix_cls
    >>> Multipoint = context.multipoint_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                   Point(0, 4)])
    >>> inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                         Point(1, 3)])
    >>> clockwise_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                   Point(3, 3), Point(3, 1)])
    >>> (complete_intersect_segment_with_polygon(
    ...      Segment(Point(0, 0), Point(1, 0)), Polygon(inner_square, []))
    ...  is EMPTY)
    True
    >>> (complete_intersect_segment_with_polygon(
    ...      Segment(Point(0, 0), Point(1, 1)), Polygon(inner_square, []))
    ...  == Multipoint([Point(1, 1)]))
    True
    >>> (complete_intersect_segment_with_polygon(
    ...      Segment(Point(0, 0), Point(1, 1)), Polygon(square, []))
    ...  == Segment(Point(0, 0), Point(1, 1)))
    True
    >>> (complete_intersect_segment_with_polygon(
    ...      Segment(Point(0, 0), Point(4, 4)),
    ...      Polygon(square, [clockwise_inner_square]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 1)),
    ...                   Segment(Point(3, 3), Point(4, 4))]))
    True
    >>> (complete_intersect_segment_with_polygon(
    ...      Segment(Point(1, 1), Point(4, 4)),
    ...      Polygon(square, [clockwise_inner_square]))
    ...  == Mix(Multipoint([Point(1, 1)]), Segment(Point(3, 3), Point(4, 4)),
    ...         EMPTY))
    True
    """
    return _mixed.CompleteIntersection(
            _operands.SegmentOperand(segment),
            _operands.PolygonOperand(polygon),
            _get_context() if context is None else context).compute()


def intersect_segment_with_polygon(segment: _Segment,
                                   polygon: _Polygon,
                                   *,
                                   context: _Optional[_Context] = None
                                   ) -> _Union[_Empty, _Multisegment,
                                               _Segment]:
    """
    Returns intersection of segment with polygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = polygon_edges_count + 1``,
    ``polygon_edges_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``,
    ``intersections_count`` --- number of intersections between segment
    and polygon edges.

    :param segment: first operand.
    :param polygon: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                   Point(0, 4)])
    >>> inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                         Point(1, 3)])
    >>> clockwise_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                   Point(3, 3), Point(3, 1)])
    >>> (intersect_segment_with_polygon(Segment(Point(0, 0), Point(1, 0)),
    ...                                 Polygon(inner_square, []))
    ...  is intersect_segment_with_polygon(Segment(Point(0, 0), Point(1, 1)),
    ...                                    Polygon(inner_square, []))
    ...  is EMPTY)
    True
    >>> (intersect_segment_with_polygon(Segment(Point(0, 0), Point(1, 1)),
    ...                                 Polygon(square, []))
    ...  == Segment(Point(0, 0), Point(1, 1)))
    True
    >>> (intersect_segment_with_polygon(Segment(Point(1, 1), Point(4, 4)),
    ...                                 Polygon(square,
    ...                                         [clockwise_inner_square]))
    ...  == Segment(Point(3, 3), Point(4, 4)))
    True
    >>> (intersect_segment_with_polygon(Segment(Point(0, 0), Point(4, 4)),
    ...                                 Polygon(square,
    ...                                         [clockwise_inner_square]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 1)),
    ...                   Segment(Point(3, 3), Point(4, 4))]))
    True
    """
    return (_mixed.Intersection(_operands.SegmentOperand(segment),
                                _operands.PolygonOperand(polygon),
                                _get_context() if context is None else context)
            .compute())


def subtract_polygon_from_segment(minuend: _Segment,
                                  subtrahend: _Polygon,
                                  *,
                                  context: _Optional[_Context] = None
                                  ) -> _Union[_Empty, _Multisegment, _Segment]:
    """
    Returns difference of segment with polygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = subtrahend_edges_count + 1``,
    ``subtrahend_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in subtrahend.polygons)``,
    ``intersections_count`` --- number of intersections between segment
    and polygon edges.

    :param minuend: segment to subtract from.
    :param subtrahend: polygon to subtract.
    :param context: geometric context.
    :returns: difference of minuend with subtrahend.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> square = Contour([Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)])
    >>> inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                         Point(1, 3)])
    >>> clockwise_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                   Point(3, 3), Point(3, 1)])
    >>> (subtract_polygon_from_segment(Segment(Point(0, 0), Point(1, 1)),
    ...                                Polygon(square, []))
    ...  is EMPTY)
    True
    >>> (subtract_polygon_from_segment(Segment(Point(0, 0), Point(1, 0)),
    ...                                Polygon(inner_square, []))
    ...  == Segment(Point(0, 0), Point(1, 0)))
    True
    >>> (subtract_polygon_from_segment(Segment(Point(0, 0), Point(1, 1)),
    ...                                Polygon(inner_square, []))
    ...  == Segment(Point(0, 0), Point(1, 1)))
    True
    >>> (subtract_polygon_from_segment(Segment(Point(1, 1), Point(4, 4)),
    ...                                Polygon(square,
    ...                                        [clockwise_inner_square]))
    ...  == subtract_polygon_from_segment(Segment(Point(0, 0), Point(4, 4)),
    ...                                   Polygon(square,
    ...                                           [clockwise_inner_square]))
    ...  == Segment(Point(1, 1), Point(3, 3)))
    True
    >>> (subtract_polygon_from_segment(Segment(Point(0, 0), Point(4, 4)),
    ...                                Polygon(inner_square, []))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 1)),
    ...                   Segment(Point(3, 3), Point(4, 4))]))
    True
    """
    return (_mixed.Difference(_operands.SegmentOperand(minuend),
                              _operands.PolygonOperand(subtrahend),
                              _get_context() if context is None else context)
            .compute())


def symmetric_subtract_polygon_from_segment(segment: _Segment,
                                            polygon: _Polygon,
                                            *,
                                            context: _Optional[_Context] = None
                                            ) -> _Union[_Mix, _Polygon]:
    """
    Returns symmetric difference of segment with polygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = polygon_edges_count + 1``,
    ``polygon_edges_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``,
    ``intersections_count`` --- number of intersections between segment
    and polygon edges.

    :param segment: first operand.
    :param polygon: second operand.
    :param context: geometric context.
    :returns: symmetric difference of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Mix = context.mix_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                   Point(0, 4)])
    >>> inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                         Point(1, 3)])
    >>> clockwise_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                   Point(3, 3), Point(3, 1)])
    >>> (symmetric_subtract_polygon_from_segment(
    ...      Segment(Point(0, 0), Point(1, 1)), Polygon(square, []))
    ...  == Polygon(square, []))
    True
    >>> (symmetric_subtract_polygon_from_segment(
    ...      Segment(Point(0, 0), Point(1, 1)), Polygon(inner_square, []))
    ...  == Mix(EMPTY, Segment(Point(0, 0), Point(1, 1)),
    ...         Polygon(inner_square, [])))
    True
    >>> (symmetric_subtract_polygon_from_segment(
    ...      Segment(Point(1, 1), Point(8, 8)),
    ...      Polygon(square, [clockwise_inner_square]))
    ...  == Mix(EMPTY, Multisegment([Segment(Point(1, 1), Point(3, 3)),
    ...                              Segment(Point(4, 4), Point(8, 8))]),
    ...         Polygon(square, [clockwise_inner_square])))
    True
    """
    return _mixed.SymmetricDifference(
            _operands.SegmentOperand(segment),
            _operands.PolygonOperand(polygon),
            _get_context() if context is None else context).compute()


def unite_segment_with_polygon(segment: _Segment,
                               polygon: _Polygon,
                               *,
                               context: _Optional[_Context] = None
                               ) -> _Union[_Mix, _Polygon]:
    """
    Returns union of segment with polygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = polygon_edges_count + 1``,
    ``polygon_edges_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``,
    ``intersections_count`` --- number of intersections between segment
    and polygon edges.

    :param segment: first operand.
    :param polygon: second operand.
    :param context: geometric context.
    :returns: union of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Mix = context.mix_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                   Point(0, 4)])
    >>> inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                         Point(1, 3)])
    >>> clockwise_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                   Point(3, 3), Point(3, 1)])
    >>> (unite_segment_with_polygon(Segment(Point(0, 0), Point(1, 1)),
    ...                             Polygon(square, []))
    ...  == Polygon(square, []))
    True
    >>> (unite_segment_with_polygon(Segment(Point(0, 0), Point(1, 1)),
    ...                             Polygon(inner_square, []))
    ...  == Mix(EMPTY, Segment(Point(0, 0), Point(1, 1)),
    ...         Polygon(inner_square, [])))
    True
    >>> (unite_segment_with_polygon(Segment(Point(1, 1), Point(8, 8)),
    ...                             Polygon(square, [clockwise_inner_square]))
    ...  == Mix(EMPTY, Multisegment([Segment(Point(1, 1), Point(3, 3)),
    ...                              Segment(Point(4, 4), Point(8, 8))]),
    ...         Polygon(square, [clockwise_inner_square])))
    True
    """
    return (_mixed.Union(_operands.SegmentOperand(segment),
                         _operands.PolygonOperand(polygon),
                         _get_context() if context is None else context)
            .compute())


def complete_intersect_segment_with_multipolygon(
        segment: _Segment,
        multipolygon: _Multipolygon,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Mix, _Multipoint, _Multisegment, _Segment]:
    """
    Returns intersection of segment with multipolygon
    considering cases with geometries touching each other in points.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = multipolygon_edges_count + 1``,
    ``multipolygon_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``,
    ``intersections_count`` --- number of intersections between segment
    and multipolygon edges.

    :param segment: first operand.
    :param multipolygon: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Mix = context.mix_cls
    >>> Contour = context.contour_cls
    >>> Multipoint = context.multipoint_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> (complete_intersect_segment_with_multipolygon(
    ...      Segment(Point(0, 0), Point(2, 0)),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  is EMPTY)
    True
    >>> (complete_intersect_segment_with_multipolygon(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Multipoint([Point(4, 0)]))
    True
    >>> (complete_intersect_segment_with_multipolygon(
    ...      Segment(Point(0, 0), Point(2, 2)),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Segment(Point(1, 1), Point(2, 2)))
    True
    >>> (complete_intersect_segment_with_multipolygon(
    ...      Segment(Point(0, 0), Point(4, 4)),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square, [])]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 1)),
    ...                   Segment(Point(3, 3), Point(4, 4))]))
    True
    >>> (complete_intersect_segment_with_multipolygon(
    ...      Segment(Point(1, 1), Point(8, 8)),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square, [])]))
    ...  == Mix(Multipoint([Point(1, 1)]),
    ...         Multisegment([Segment(Point(3, 3), Point(4, 4)),
    ...                       Segment(Point(4, 4), Point(8, 8))]), EMPTY))
    True
    """
    return _mixed.CompleteIntersection(
            _operands.SegmentOperand(segment),
            _operands.MultipolygonOperand(multipolygon),
            _get_context() if context is None else context).compute()


def intersect_segment_with_multipolygon(segment: _Segment,
                                        multipolygon: _Multipolygon,
                                        *,
                                        context: _Optional[_Context] = None
                                        ) -> _Union[_Empty, _Multisegment,
                                                    _Segment]:
    """
    Returns intersection of segment with multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = multipolygon_edges_count + 1``,
    ``multipolygon_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``,
    ``intersections_count`` --- number of intersections between segment
    and multipolygon edges.

    :param segment: first operand.
    :param multipolygon: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> (intersect_segment_with_multipolygon(
    ...      Segment(Point(0, 0), Point(2, 0)),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  is intersect_segment_with_multipolygon(
    ...          Segment(Point(0, 0), Point(4, 0)),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_square, [])]))
    ...  is EMPTY)
    True
    >>> (intersect_segment_with_multipolygon(
    ...      Segment(Point(0, 0), Point(2, 2)),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Segment(Point(1, 1), Point(2, 2)))
    True
    >>> (intersect_segment_with_multipolygon(
    ...      Segment(Point(0, 0), Point(4, 4)),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square, [])]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 1)),
    ...                   Segment(Point(3, 3), Point(4, 4))]))
    True
    >>> (intersect_segment_with_multipolygon(
    ...      Segment(Point(1, 1), Point(8, 8)),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square, [])]))
    ...  == Multisegment([Segment(Point(3, 3), Point(4, 4)),
    ...                   Segment(Point(4, 4), Point(8, 8))]))
    True
    """
    return (_mixed.Intersection(_operands.SegmentOperand(segment),
                                _operands.MultipolygonOperand(multipolygon),
                                _get_context() if context is None else context)
            .compute())


def subtract_multipolygon_from_segment(minuend: _Segment,
                                       subtrahend: _Multipolygon,
                                       *,
                                       context: _Optional[_Context] = None
                                       ) -> _Union[_Empty, _Multisegment,
                                                   _Segment]:
    """
    Returns difference of segment with multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = subtrahend_edges_count + 1``,
    ``subtrahend_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in subtrahend.polygons)``,
    ``intersections_count`` --- number of intersections between segment
    and multipolygon edges.

    :param minuend: segment to subtract from.
    :param subtrahend: multipolygon to subtract.
    :param context: geometric context.
    :returns: difference of minuend with subtrahend.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> (subtract_multipolygon_from_segment(
    ...      Segment(Point(0, 0), Point(4, 0)),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  is EMPTY)
    True
    >>> (subtract_multipolygon_from_segment(
    ...      Segment(Point(0, 0), Point(4, 4)),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square, [])]))
    ...  == Segment(Point(1, 1), Point(3, 3)))
    True
    >>> (subtract_multipolygon_from_segment(
    ...      Segment(Point(0, 0), Point(4, 4)),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 1)),
    ...                   Segment(Point(3, 3), Point(4, 4))]))
    True
    """
    return (_mixed.Difference(_operands.SegmentOperand(minuend),
                              _operands.MultipolygonOperand(subtrahend),
                              _get_context() if context is None else context)
            .compute())


def symmetric_subtract_multipolygon_from_segment(
        segment: _Segment,
        multipolygon: _Multipolygon,
        *,
        context: _Optional[_Context] = None) -> _Union[_Mix, _Multipolygon]:
    """
    Returns symmetric difference of segment with multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = multipolygon_edges_count + 1``,
    ``multipolygon_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``,
    ``intersections_count`` --- number of intersections between segment
    and multipolygon edges.

    :param segment: first operand.
    :param multipolygon: second operand.
    :param context: geometric context.
    :returns: symmetric difference of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Mix = context.mix_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> (symmetric_subtract_multipolygon_from_segment(
    ...      Segment(Point(0, 0), Point(4, 4)),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Multipolygon([Polygon(first_square, []),
    ...                   Polygon(third_square, [])]))
    True
    >>> (symmetric_subtract_multipolygon_from_segment(
    ...      Segment(Point(0, 0), Point(4, 4)),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square, [])]))
    ...  == Mix(EMPTY, Segment(Point(1, 1), Point(3, 3)),
    ...         Multipolygon([Polygon(first_square,
    ...                               [clockwise_first_inner_square]),
    ...                       Polygon(third_square, [])])))
    True
    >>> (symmetric_subtract_multipolygon_from_segment(
    ...      Segment(Point(0, 0), Point(4, 4)),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Mix(EMPTY, Multisegment([Segment(Point(0, 0), Point(1, 1)),
    ...                              Segment(Point(3, 3), Point(4, 4))]),
    ...         Multipolygon([Polygon(first_inner_square, []),
    ...                       Polygon(second_square, [])])))
    True
    """
    return _mixed.SymmetricDifference(
            _operands.SegmentOperand(segment),
            _operands.MultipolygonOperand(multipolygon),
            _get_context() if context is None else context).compute()


def unite_segment_with_multipolygon(segment: _Segment,
                                    multipolygon: _Multipolygon,
                                    *,
                                    context: _Optional[_Context] = None
                                    ) -> _Union[_Mix, _Multipolygon]:
    """
    Returns union of segment with multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = multipolygon_edges_count + 1``,
    ``multipolygon_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``,
    ``intersections_count`` --- number of intersections between segment
    and multipolygon edges.

    :param segment: first operand.
    :param multipolygon: second operand.
    :param context: geometric context.
    :returns: union of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Mix = context.mix_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> (unite_segment_with_multipolygon(
    ...      Segment(Point(0, 0), Point(4, 4)),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Multipolygon([Polygon(first_square, []),
    ...                   Polygon(third_square, [])]))
    True
    >>> (unite_segment_with_multipolygon(
    ...      Segment(Point(0, 0), Point(4, 4)),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square, [])]))
    ...  == Mix(EMPTY, Segment(Point(1, 1), Point(3, 3)),
    ...         Multipolygon([Polygon(first_square,
    ...                               [clockwise_first_inner_square]),
    ...                       Polygon(third_square, [])])))
    True
    >>> (unite_segment_with_multipolygon(
    ...      Segment(Point(0, 0), Point(4, 4)),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Mix(EMPTY, Multisegment([Segment(Point(0, 0), Point(1, 1)),
    ...                              Segment(Point(3, 3), Point(4, 4))]),
    ...         Multipolygon([Polygon(first_inner_square, []),
    ...                       Polygon(second_square, [])])))
    True
    """
    return (_mixed.Union(_operands.SegmentOperand(segment),
                         _operands.MultipolygonOperand(multipolygon),
                         _get_context() if context is None else context)
            .compute())


def segments_to_multisegment(segments: _Sequence[_Segment],
                             *,
                             context: _Optional[_Context] = None
                             ) -> _Union[_Empty, _Segment, _Multisegment]:
    """
    Returns multisegment from given segments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = segments_count + intersections_count``,
    ``segments_count = len(segments)``,
    ``intersections_count`` --- number of intersections between segments.

    :param segments: target segments.
    :param context: geometric context.
    :returns: multisegment from segments.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (segments_to_multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                            Segment(Point(0, 1), Point(1, 0))])
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    True
    >>> (segments_to_multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                            Segment(Point(1, 0), Point(3, 0))])
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(1, 0), Point(2, 0)),
    ...                   Segment(Point(2, 0), Point(3, 0))]))
    True
    """
    return _linear.merge_segments(
            segments, _get_context() if context is None else context)


def complete_intersect_multisegments(first: _Multisegment,
                                     second: _Multisegment,
                                     *,
                                     context: _Optional[_Context] = None
                                     ) -> _Union[_Empty, _Mix, _Multipoint,
                                                 _Multisegment, _Segment]:
    """
    Returns intersection of multisegments considering cases
    with segments touching each other in points.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = segments_count + intersections_count``,
    ``segments_count = len(first.segments) + len(second.segments)``,
    ``intersections_count`` --- number of intersections between multisegments.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Mix = context.mix_cls
    >>> Multipoint = context.multipoint_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (complete_intersect_multisegments(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]),
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    True
    >>> (complete_intersect_multisegments(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 1))]),
    ...      Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                    Segment(Point(0, 0), Point(2, 2))]))
    ...  == Mix(Multipoint([Point(1, 1)]), Segment(Point(0, 0), Point(1, 0)),
    ...         EMPTY))
    True
    """
    return _linear.CompleteIntersection(
            _operands.MultisegmentOperand(first),
            _operands.MultisegmentOperand(second),
            _get_context() if context is None else context).compute()


def intersect_multisegments(first: _Multisegment,
                            second: _Multisegment,
                            *,
                            context: _Optional[_Context] = None
                            ) -> _Union[_Empty, _Segment, _Multisegment]:
    """
    Returns intersection of multisegments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = segments_count + intersections_count``,
    ``segments_count = len(first.segments) + len(second.segments)``,
    ``intersections_count`` --- number of intersections between multisegments.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (intersect_multisegments(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]),
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    True
    >>> (intersect_multisegments(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 1))]),
    ...      Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                    Segment(Point(0, 0), Point(2, 2))]))
    ...  == Segment(Point(0, 0), Point(1, 0)))
    True
    """
    return _linear.Intersection(
            _operands.MultisegmentOperand(first),
            _operands.MultisegmentOperand(second),
            _get_context() if context is None else context).compute()


def subtract_multisegments(minuend: _Multisegment,
                           subtrahend: _Multisegment,
                           *,
                           context: _Optional[_Context] = None
                           ) -> _Union[_Empty, _Segment, _Multisegment]:
    """
    Returns difference of multisegments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = segments_count + intersections_count``,
    ``segments_count = len(first.segments) + len(second.segments)``,
    ``intersections_count`` --- number of intersections between multisegments.

    :param minuend: multisegment to subtract from.
    :param subtrahend: multisegment to subtract.
    :param context: geometric context.
    :returns: difference between minuend and subtrahend.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (subtract_multisegments(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]),
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]))
    ...  is EMPTY)
    True
    >>> (subtract_multisegments(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 1))]),
    ...      Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                    Segment(Point(0, 0), Point(2, 2))]))
    ...  == Segment(Point(0, 1), Point(1, 1)))
    True
    """
    return (_linear.Difference(_operands.MultisegmentOperand(minuend),
                               _operands.MultisegmentOperand(subtrahend),
                               _get_context() if context is None else context)
            .compute())


def symmetric_subtract_multisegments(first: _Multisegment,
                                     second: _Multisegment,
                                     *,
                                     context: _Optional[_Context] = None
                                     ) -> _Union[_Empty, _Segment,
                                                 _Multisegment]:
    """
    Returns symmetric difference of multisegments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = segments_count + intersections_count``,
    ``segments_count = len(first.segments) + len(second.segments)``,
    ``intersections_count`` --- number of intersections between multisegments.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: symmetric difference of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (symmetric_subtract_multisegments(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]),
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]))
    ...  is EMPTY)
    True
    >>> (symmetric_subtract_multisegments(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 1))]),
    ...      Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                    Segment(Point(0, 0), Point(2, 2))]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 1)),
    ...                   Segment(Point(0, 1), Point(1, 1)),
    ...                   Segment(Point(1, 0), Point(2, 0)),
    ...                   Segment(Point(1, 1), Point(2, 2))]))
    True
    """
    return _linear.SymmetricDifference(
            _operands.MultisegmentOperand(first),
            _operands.MultisegmentOperand(second),
            _get_context() if context is None else context).compute()


def unite_multisegments(first: _Multisegment,
                        second: _Multisegment,
                        *,
                        context: _Optional[_Context] = None) -> _Multisegment:
    """
    Returns union of multisegments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = segments_count + intersections_count``,
    ``segments_count = len(first.segments) + len(second.segments)``,
    ``intersections_count`` --- number of intersections between multisegments.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: union of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> (unite_multisegments(Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                                    Segment(Point(0, 1), Point(1, 0))]),
    ...                      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                                    Segment(Point(0, 1), Point(1, 0))]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    True
    >>> (unite_multisegments(Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                                    Segment(Point(0, 1), Point(1, 1))]),
    ...                      Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                                    Segment(Point(0, 0), Point(2, 2))]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 0), Point(1, 1)),
    ...                   Segment(Point(0, 1), Point(1, 1)),
    ...                   Segment(Point(1, 0), Point(2, 0)),
    ...                   Segment(Point(1, 1), Point(2, 2))]))
    True
    """
    return (_linear.Union(_operands.MultisegmentOperand(first),
                          _operands.MultisegmentOperand(second),
                          _get_context() if context is None else context)
            .compute())


def complete_intersect_multisegment_with_polygon(
        multisegment: _Multisegment,
        polygon: _Polygon,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Mix, _Multipoint, _Multisegment, _Segment]:
    """
    Returns intersection of multisegment with polygon
    considering cases with geometries touching each other in points.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = len(multisegment.segments)\
 + polygon_edges_count``,
    ``polygon_edges_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``,
    ``intersections_count`` --- number of intersections between multisegment
    and polygon edges.

    :param multisegment: multisegment to intersect with.
    :param polygon: polygon to intersect with.
    :param context: geometric context.
    :returns: intersection of multisegment with polygon.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Mix = context.mix_cls
    >>> Contour = context.contour_cls
    >>> Multipoint = context.multipoint_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> (complete_intersect_multisegment_with_polygon(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]),
    ...      Polygon(Contour([Point(0, 0), Point(1, 0), Point(0, 1)]), []))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    True
    >>> (complete_intersect_multisegment_with_polygon(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(1, 1), Point(2, 2))]),
    ...      Polygon(Contour([Point(0, 0), Point(1, 0), Point(1, 1),
    ...                       Point(0, 1)]), []))
    ...  == Mix(Multipoint([Point(1, 1)]), Segment(Point(0, 0), Point(1, 0)),
    ...         EMPTY))
    True
    """
    return _mixed.CompleteIntersection(
            _operands.MultisegmentOperand(multisegment),
            _operands.PolygonOperand(polygon),
            _get_context() if context is None else context).compute()


def intersect_multisegment_with_polygon(
        multisegment: _Multisegment,
        polygon: _Polygon,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Multisegment, _Segment]:
    """
    Returns intersection of multisegment with polygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = len(multisegment.segments)\
 + polygon_edges_count``,
    ``polygon_edges_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``,
    ``intersections_count`` --- number of intersections between multisegment
    and polygon edges.

    :param multisegment: multisegment to intersect with.
    :param polygon: polygon to intersect with.
    :param context: geometric context.
    :returns: intersection of multisegment with polygon.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> (intersect_multisegment_with_polygon(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]),
    ...      Polygon(Contour([Point(0, 0), Point(1, 0), Point(0, 1)]), []))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    True
    >>> (intersect_multisegment_with_polygon(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(1, 1), Point(2, 2))]),
    ...      Polygon(Contour([Point(0, 0), Point(1, 0), Point(1, 1),
    ...                       Point(0, 1)]), []))
    ...  == Segment(Point(0, 0), Point(1, 0)))
    True
    """
    return (_mixed.Intersection(_operands.MultisegmentOperand(multisegment),
                                _operands.PolygonOperand(polygon),
                                _get_context() if context is None else context)
            .compute())


def subtract_polygon_from_multisegment(
        minuend: _Multisegment,
        subtrahend: _Polygon,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Multisegment, _Segment]:
    """
    Returns difference of multisegment with polygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = len(minuend.segments)\
 + subtrahend_edges_count``,
    ``subtrahend_edges_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``,
    ``intersections_count`` --- number of intersections between multisegment
    and polygon edges.

    :param minuend: multisegment to subtract from.
    :param subtrahend: polygon to subtract.
    :param context: geometric context.
    :returns: difference of minuend with subtrahend.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipoint = context.multipoint_cls
    >>> Polygon = context.polygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> (subtract_polygon_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]),
    ...      Polygon(Contour([Point(0, 0), Point(1, 0), Point(0, 1)]), []))
    ...  is EMPTY)
    True
    >>> (subtract_polygon_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(1, 1), Point(2, 2))]),
    ...      Polygon(Contour([Point(0, 0), Point(1, 0), Point(1, 1),
    ...                       Point(0, 1)]), []))
    ...  == Segment(Point(1, 1), Point(2, 2)))
    True
    """
    return (_mixed.Difference(_operands.MultisegmentOperand(minuend),
                              _operands.PolygonOperand(subtrahend),
                              _get_context() if context is None else context)
            .compute())


def symmetric_subtract_polygon_from_multisegment(
        multisegment: _Multisegment,
        polygon: _Polygon,
        *,
        context: _Optional[_Context] = None) -> _Union[_Mix, _Polygon]:
    """
    Returns symmetric difference of multisegment with polygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = len(multisegment.segments)\
 + polygon_edges_count``,
    ``polygon_edges_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``,
    ``intersections_count`` --- number of intersections between multisegment
    and polygon edges.

    :param multisegment: first operand.
    :param polygon: second operand.
    :param context: geometric context.
    :returns: symmetric difference of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Mix = context.mix_cls
    >>> Polygon = context.polygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> (symmetric_subtract_polygon_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]),
    ...      Polygon(Contour([Point(0, 0), Point(1, 0), Point(0, 1)]), []))
    ...  == Polygon(Contour([Point(0, 0), Point(1, 0), Point(0, 1)]), []))
    True
    >>> (symmetric_subtract_polygon_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(1, 1), Point(2, 2))]),
    ...      Polygon(Contour([Point(0, 0), Point(1, 0), Point(1, 1),
    ...                       Point(0, 1)]), []))
    ...  == Mix(EMPTY, Segment(Point(1, 1), Point(2, 2)),
    ...         Polygon(Contour([Point(0, 0), Point(1, 0), Point(1, 1),
    ...                          Point(0, 1)]), [])))
    True
    >>> (symmetric_subtract_polygon_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(1, 0), Point(2, 0)),
    ...                    Segment(Point(1, 1), Point(2, 2))]),
    ...      Polygon(Contour([Point(0, 0), Point(1, 0), Point(1, 1),
    ...                       Point(0, 1)]), []))
    ...  == Mix(EMPTY, Multisegment([Segment(Point(1, 0), Point(2, 0)),
    ...                              Segment(Point(1, 1), Point(2, 2))]),
    ...         Polygon(Contour([Point(0, 0), Point(1, 0), Point(1, 1),
    ...                          Point(0, 1)]), [])))
    True
    """
    return _mixed.SymmetricDifference(
            _operands.MultisegmentOperand(multisegment),
            _operands.PolygonOperand(polygon),
            _get_context() if context is None else context).compute()


def unite_multisegment_with_polygon(
        multisegment: _Multisegment,
        polygon: _Polygon,
        *,
        context: _Optional[_Context] = None) -> _Union[_Mix, _Polygon]:
    """
    Returns union of multisegment with polygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = len(multisegment.segments)\
 + polygon_edges_count``,
    ``polygon_edges_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``,
    ``intersections_count`` --- number of intersections between multisegment
    and polygon edges.

    :param multisegment: first operand.
    :param polygon: second operand.
    :param context: geometric context.
    :returns: union of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Mix = context.mix_cls
    >>> Polygon = context.polygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> (unite_multisegment_with_polygon(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]),
    ...      Polygon(Contour([Point(0, 0), Point(1, 0), Point(0, 1)]), []))
    ...  == Polygon(Contour([Point(0, 0), Point(1, 0), Point(0, 1)]), []))
    True
    >>> (unite_multisegment_with_polygon(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(1, 1), Point(2, 2))]),
    ...      Polygon(Contour([Point(0, 0), Point(1, 0), Point(1, 1),
    ...                       Point(0, 1)]), []))
    ...  == Mix(EMPTY, Segment(Point(1, 1), Point(2, 2)),
    ...         Polygon(Contour([Point(0, 0), Point(1, 0), Point(1, 1),
    ...                          Point(0, 1)]), [])))
    True
    >>> (unite_multisegment_with_polygon(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(1, 0), Point(2, 0)),
    ...                    Segment(Point(1, 1), Point(2, 2))]),
    ...      Polygon(Contour([Point(0, 0), Point(1, 0), Point(1, 1),
    ...                       Point(0, 1)]), []))
    ...  == Mix(EMPTY, Multisegment([Segment(Point(1, 0), Point(2, 0)),
    ...                              Segment(Point(1, 1), Point(2, 2))]),
    ...         Polygon(Contour([Point(0, 0), Point(1, 0), Point(1, 1),
    ...                          Point(0, 1)]), [])))
    True
    """
    return (_mixed.Union(_operands.MultisegmentOperand(multisegment),
                         _operands.PolygonOperand(polygon),
                         _get_context() if context is None else context)
            .compute())


def complete_intersect_multisegment_with_multipolygon(
        multisegment: _Multisegment,
        multipolygon: _Multipolygon,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Mix, _Multipoint, _Multisegment, _Segment]:
    """
    Returns intersection of multisegment with multipolygon
    considering cases with geometries touching each other in points.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = len(multisegment.segments)\
 + multipolygon_edges_count``,
    ``multipolygon_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``,
    ``intersections_count`` --- number of intersections between multisegment
    and multipolygon edges.

    :param multisegment: multisegment to intersect with.
    :param multipolygon: multipolygon to intersect with.
    :param context: geometric context.
    :returns: intersection of multisegment with multipolygon.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Mix = context.mix_cls
    >>> Contour = context.contour_cls
    >>> Multipoint = context.multipoint_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> (complete_intersect_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                    Segment(Point(0, 0), Point(0, 2))]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  is EMPTY)
    True
    >>> (complete_intersect_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(0, 4))]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Multipoint([Point(4, 0)]))
    True
    >>> (complete_intersect_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                    Segment(Point(0, 0), Point(2, 2))]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Segment(Point(1, 1), Point(2, 2)))
    True
    >>> (complete_intersect_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 4))]),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                   Segment(Point(0, 0), Point(4, 4))]))
    True
    >>> (complete_intersect_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 4))]),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square, [])]))
    ...  == Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                   Segment(Point(0, 0), Point(1, 1)),
    ...                   Segment(Point(3, 3), Point(4, 4))]))
    True
    >>> (complete_intersect_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 4))]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Mix(Multipoint([Point(4, 0), Point(4, 4)]),
    ...         Segment(Point(1, 1), Point(3, 3)), EMPTY))
    True
    """
    return _mixed.CompleteIntersection(
            _operands.MultisegmentOperand(multisegment),
            _operands.MultipolygonOperand(multipolygon),
            _get_context() if context is None else context).compute()


def intersect_multisegment_with_multipolygon(
        multisegment: _Multisegment,
        multipolygon: _Multipolygon,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Multisegment, _Segment]:
    """
    Returns intersection of multisegment with multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = len(multisegment.segments)\
 + multipolygon_edges_count``,
    ``multipolygon_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``,
    ``intersections_count`` --- number of intersections between multisegment
    and multipolygon edges.

    :param multisegment: multisegment to intersect with.
    :param multipolygon: multipolygon to intersect with.
    :param context: geometric context.
    :returns: intersection of multisegment with multipolygon.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> (intersect_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(0, 4))]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  is EMPTY)
    True
    >>> (intersect_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 4))]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Segment(Point(1, 1), Point(3, 3)))
    True
    >>> (intersect_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 4))]),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                   Segment(Point(0, 0), Point(4, 4))]))
    True
    >>> (intersect_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 4))]),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square, [])]))
    ...  == Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                   Segment(Point(0, 0), Point(1, 1)),
    ...                   Segment(Point(3, 3), Point(4, 4))]))
    True
    """
    return (_mixed.Intersection(_operands.MultisegmentOperand(multisegment),
                                _operands.MultipolygonOperand(multipolygon),
                                _get_context() if context is None else context)
            .compute())


def subtract_multipolygon_from_multisegment(
        minuend: _Multisegment,
        subtrahend: _Multipolygon,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Multisegment, _Segment]:
    """
    Returns difference of multisegment with multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = len(minuend.segments)\
 + multipolygon_edges_count``,
    ``subtrahend_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in subtrahend.polygons)``,
    ``intersections_count`` --- number of intersections between multisegment
    and multipolygon edges.

    :param minuend: multisegment to subtract from.
    :param subtrahend: multipolygon to subtract.
    :param context: geometric context.
    :returns: difference of minuend with subtrahend.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> (subtract_multipolygon_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 4))]),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  is EMPTY)
    True
    >>> (subtract_multipolygon_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 4))]),
    ...      Multipolygon([Polygon(first_square, [clockwise_first_inner_square]),
    ...                    Polygon(third_square, [])]))
    ...  == Segment(Point(1, 1), Point(3, 3)))
    True
    >>> (subtract_multipolygon_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 4))]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 1)),
    ...                   Segment(Point(0, 0), Point(4, 0)),
    ...                   Segment(Point(3, 3), Point(4, 4))]))
    True
    """
    return (_mixed.Difference(_operands.MultisegmentOperand(minuend),
                              _operands.MultipolygonOperand(subtrahend),
                              _get_context() if context is None else context)
            .compute())


def symmetric_subtract_multipolygon_from_multisegment(
        multisegment: _Multisegment,
        multipolygon: _Multipolygon,
        *,
        context: _Optional[_Context] = None) -> _Union[_Mix, _Multipolygon]:
    """
    Returns symmetric difference of multisegment with multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = len(multisegment.segments)\
 + multipolygon_edges_count``,
    ``multipolygon_edges_count = len(multipolygon.border.vertices)\
 + sum(len(hole.vertices) for hole in multipolygon.holes)``,
    ``intersections_count`` --- number of intersections between multisegment
    and multipolygon edges.

    :param multisegment: first operand.
    :param multipolygon: second operand.
    :param context: geometric context.
    :returns: symmetric difference of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Mix = context.mix_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> (symmetric_subtract_multipolygon_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 4))]),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Multipolygon([Polygon(first_square, []),
    ...                   Polygon(third_square, [])]))
    True
    >>> (symmetric_subtract_multipolygon_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 4))]),
    ...      Multipolygon([Polygon(first_square, [clockwise_first_inner_square]),
    ...                    Polygon(third_square, [])]))
    ...  == Mix(EMPTY, Segment(Point(1, 1), Point(3, 3)),
    ...         Multipolygon([Polygon(first_square,
    ...                               [clockwise_first_inner_square]),
    ...                       Polygon(third_square, [])])))
    True
    >>> (symmetric_subtract_multipolygon_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 4))]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Mix(EMPTY, Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                              Segment(Point(0, 0), Point(1, 1)),
    ...                              Segment(Point(3, 3), Point(4, 4))]),
    ...         Multipolygon([Polygon(first_inner_square, []),
    ...                       Polygon(second_square, [])])))
    True
    """
    return _mixed.SymmetricDifference(
            _operands.MultisegmentOperand(multisegment),
            _operands.MultipolygonOperand(multipolygon),
            _get_context() if context is None else context).compute()


def unite_multisegment_with_multipolygon(
        multisegment: _Multisegment,
        multipolygon: _Multipolygon,
        *,
        context: _Optional[_Context] = None) -> _Union[_Mix, _Multipolygon]:
    """
    Returns union of multisegment with multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = len(multisegment.segments)\
 + multipolygon_edges_count``,
    ``multipolygon_edges_count = len(multipolygon.border.vertices)\
 + sum(len(hole.vertices) for hole in multipolygon.holes)``,
    ``intersections_count`` --- number of intersections between multisegment
    and multipolygon edges.

    :param multisegment: first operand.
    :param multipolygon: second operand.
    :param context: geometric context.
    :returns: union of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Mix = context.mix_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> (unite_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 4))]),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Multipolygon([Polygon(first_square, []),
    ...                   Polygon(third_square, [])]))
    True
    >>> (unite_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 4))]),
    ...      Multipolygon([Polygon(first_square, [clockwise_first_inner_square]),
    ...                    Polygon(third_square, [])]))
    ...  == Mix(EMPTY, Segment(Point(1, 1), Point(3, 3)),
    ...         Multipolygon([Polygon(first_square,
    ...                               [clockwise_first_inner_square]),
    ...                       Polygon(third_square, [])])))
    True
    >>> (unite_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                    Segment(Point(0, 0), Point(4, 4))]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Mix(EMPTY, Multisegment([Segment(Point(0, 0), Point(4, 0)),
    ...                              Segment(Point(0, 0), Point(1, 1)),
    ...                              Segment(Point(3, 3), Point(4, 4))]),
    ...         Multipolygon([Polygon(first_inner_square, []),
    ...                       Polygon(second_square, [])])))
    True
    """
    return _mixed.Union(
            _operands.MultisegmentOperand(multisegment),
            _operands.MultipolygonOperand(multipolygon),
            _get_context() if context is None else context).compute()


def complete_intersect_regions(first: _Region,
                               second: _Region,
                               *,
                               context: _Optional[_Context] = None
                               ) -> _Union[_Empty, _Mix, _Multipoint,
                                           _Multipolygon, _Multisegment,
                                           _Polygon, _Segment]:
    """
    Returns intersection of regions
    considering cases with regions touching each other in points/segments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = len(first.vertices) + len(second.vertices)``,
    ``intersections_count`` --- number of intersections between regions edges.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Mix = context.mix_cls
    >>> Multipoint = context.multipoint_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> (complete_intersect_regions(first_inner_square, second_square)
    ...  is EMPTY)
    True
    >>> (complete_intersect_regions(first_square, third_square)
    ...  == Multipoint([Point(4, 4)]))
    True
    >>> (complete_intersect_regions(first_square, second_square)
    ...  == Segment(Point(4, 0), Point(4, 4)))
    True
    >>> (complete_intersect_regions(first_square, first_square)
    ...  == Polygon(first_square, []))
    True
    """
    return _holeless.CompleteIntersection(
            _operands.RegionOperand(first), _operands.RegionOperand(second),
            _get_context() if context is None else context).compute()


def intersect_regions(first: _Region,
                      second: _Region,
                      *,
                      context: _Optional[_Context] = None
                      ) -> _Union[_Empty, _Multipolygon, _Polygon]:
    """
    Returns intersection of regions.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = len(first.vertices) + len(second.vertices)``,
    ``intersections_count`` --- number of intersections between regions edges.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> (intersect_regions(first_inner_square, second_square)
    ...  is intersect_regions(first_square, third_square)
    ...  is intersect_regions(first_square, second_square)
    ...  is EMPTY)
    True
    >>> (intersect_regions(first_square, first_square)
    ...  == Polygon(first_square, []))
    True
    """
    return _holeless.Intersection(
            _operands.RegionOperand(first), _operands.RegionOperand(second),
            _get_context() if context is None else context).compute()


def complete_intersect_region_with_multiregion(
        region: _Region,
        multiregion: _Multiregion,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Mix, _Multipoint, _Multipolygon, _Multisegment, _Polygon,
            _Segment]:
    """
    Returns intersection of region with multiregion
    considering cases with regions touching each other in points/segments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = len(region.vertices) + multiregion_edges_count``,
    ``multiregion_edges_count = sum(len(region.vertices)\
 for region in multiregion)``,
    ``intersections_count`` --- number of intersections between regions edges.

    :param region: first operand.
    :param multiregion: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Mix = context.mix_cls
    >>> Multipoint = context.multipoint_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> (complete_intersect_region_with_multiregion(
    ...      second_inner_square, [first_square, third_square])
    ...  is EMPTY)
    True
    >>> (complete_intersect_region_with_multiregion(
    ...      first_square, [second_inner_square, third_square])
    ...  == Multipoint([Point(4, 4)]))
    True
    >>> (complete_intersect_region_with_multiregion(
    ...      second_square, [first_square, third_square])
    ...  == Multisegment([Segment(Point(4, 0), Point(4, 4)),
    ...                   Segment(Point(4, 4), Point(8, 4))]))
    True
    >>> (complete_intersect_region_with_multiregion(
    ...      first_square, [first_inner_square, second_inner_square])
    ...  == Polygon(first_inner_square, []))
    True
    >>> (complete_intersect_region_with_multiregion(
    ...      first_square, [first_inner_square, third_square])
    ...  == Mix(Multipoint([Point(4, 4)]), EMPTY,
    ...         Polygon(first_inner_square, [])))
    True
    >>> (complete_intersect_region_with_multiregion(
    ...      first_square, [first_inner_square, second_square])
    ...  == Mix(EMPTY, Segment(Point(4, 0), Point(4, 4)),
    ...         Polygon(first_inner_square, [])))
    True
    """
    return _holeless.CompleteIntersection(
            _operands.RegionOperand(region),
            _operands.MultiregionOperand(multiregion),
            _get_context() if context is None else context).compute()


def intersect_region_with_multiregion(
        region: _Region,
        multiregion: _Multiregion,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Multipolygon, _Polygon]:
    """
    Returns intersection of region with multiregion.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = len(region.vertices) + multiregion_edges_count``,
    ``multiregion_edges_count = sum(len(region.vertices)\
 for region in multiregion)``,
    ``intersections_count`` --- number of intersections between regions edges.

    :param region: first operand.
    :param multiregion: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> (intersect_region_with_multiregion(
    ...      second_inner_square, [first_square, third_square])
    ...  is intersect_region_with_multiregion(
    ...          first_square, [second_inner_square, third_square])
    ...  is intersect_region_with_multiregion(
    ...          second_square, [first_square, third_square])
    ...  is EMPTY)
    True
    >>> (intersect_region_with_multiregion(
    ...      first_square, [first_inner_square, second_inner_square])
    ...  == intersect_region_with_multiregion(
    ...          first_square, [first_inner_square, third_square])
    ...  == intersect_region_with_multiregion(
    ...          first_square, [first_inner_square, second_square])
    ...  == Polygon(first_inner_square, []))
    True
    """
    return _holeless.Intersection(
            _operands.RegionOperand(region),
            _operands.MultiregionOperand(multiregion),
            _get_context() if context is None else context).compute()


def complete_intersect_multiregions(first: _Multiregion,
                                    second: _Multiregion,
                                    *,
                                    context: _Optional[_Context] = None
                                    ) -> _Union[_Empty, _Mix, _Multipoint,
                                                _Multipolygon, _Multisegment,
                                                _Polygon, _Segment]:
    """
    Returns intersection of multiregions
    considering cases with regions touching each other in points/segments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = first_edges_count + second_edges_count``,
    ``first_edges_count = sum(len(region.vertices) for region in first)``,
    ``second_edges_count = sum(len(region.vertices) for region in second)``,
    ``intersections_count`` --- number of intersections between multiregions
    edges.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Mix = context.mix_cls
    >>> Multipoint = context.multipoint_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> (complete_intersect_multiregions(
    ...      [first_inner_square, third_inner_square],
    ...      [second_square, fourth_square])
    ...  is EMPTY)
    True
    >>> (complete_intersect_multiregions([first_square, third_square],
    ...                                  [second_square, fourth_square])
    ...  == Multisegment([Segment(Point(0, 4), Point(4, 4)),
    ...                   Segment(Point(4, 0), Point(4, 4)),
    ...                   Segment(Point(4, 4), Point(8, 4)),
    ...                   Segment(Point(4, 4), Point(4, 8))]))
    True
    >>> (complete_intersect_multiregions([first_square, second_inner_square],
    ...                                  [first_inner_square, second_square])
    ...  == Mix(EMPTY, Segment(Point(4, 0), Point(4, 4)),
    ...         Multipolygon([Polygon(first_inner_square, []),
    ...                       Polygon(second_inner_square, [])])))
    True
    >>> (complete_intersect_multiregions([first_square, third_inner_square],
    ...                                  [first_inner_square, third_square])
    ...  == Mix(Multipoint([Point(4, 4)]), EMPTY,
    ...         Multipolygon([Polygon(first_inner_square, []),
    ...                       Polygon(third_inner_square, [])])))
    True
    >>> (complete_intersect_multiregions(
    ...      [first_square, third_square],
    ...      [first_inner_square, third_inner_square])
    ...  == complete_intersect_multiregions(
    ...          [first_inner_square, third_inner_square],
    ...          [first_square, third_square])
    ...  == complete_intersect_multiregions(
    ...          [first_square, third_inner_square],
    ...          [first_inner_square, third_inner_square])
    ...  == complete_intersect_multiregions(
    ...          [first_inner_square, third_inner_square],
    ...          [first_square, third_inner_square])
    ...  == complete_intersect_multiregions(
    ...          [first_inner_square, third_inner_square],
    ...          [first_inner_square, second_inner_square, third_inner_square])
    ...  == complete_intersect_multiregions(
    ...          [first_inner_square, second_inner_square, third_inner_square],
    ...          [first_inner_square, third_inner_square])
    ...  == Multipolygon([Polygon(first_inner_square, []),
    ...                   Polygon(third_inner_square, [])]))
    True
    >>> (complete_intersect_multiregions([first_square, third_square],
    ...                                  [first_square, third_square])
    ...  == Multipolygon([Polygon(first_square, []),
    ...                   Polygon(third_square, [])]))
    True
    """
    return _holeless.CompleteIntersection(
            _operands.MultiregionOperand(first),
            _operands.MultiregionOperand(second),
            _get_context() if context is None else context).compute()


def intersect_multiregions(first: _Multiregion,
                           second: _Multiregion,
                           *,
                           context: _Optional[_Context] = None
                           ) -> _Union[_Empty, _Multipolygon, _Polygon]:
    """
    Returns intersection of multiregions.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = first_edges_count + second_edges_count``,
    ``first_edges_count = sum(len(region.vertices) for region in first)``,
    ``second_edges_count = sum(len(region.vertices) for region in second)``,
    ``intersections_count`` --- number of intersections between multiregions
    edges.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> (intersect_multiregions([first_inner_square, third_inner_square],
    ...                         [second_square, fourth_square])
    ...  is intersect_multiregions([first_square, third_square],
    ...                            [second_square, fourth_square])
    ...  is EMPTY)
    True
    >>> (intersect_multiregions([first_square, third_inner_square],
    ...                         [first_inner_square, third_square])
    ...  == intersect_multiregions([first_square, third_square],
    ...                            [first_inner_square, third_inner_square])
    ...  == intersect_multiregions([first_inner_square, third_inner_square],
    ...                            [first_square, third_square])
    ...  == Multipolygon([Polygon(first_inner_square, []),
    ...                   Polygon(third_inner_square, [])]))
    True
    >>> (intersect_multiregions([first_square, second_inner_square],
    ...                         [first_inner_square, second_inner_square])
    ...  == intersect_multiregions([first_inner_square, second_inner_square],
    ...                            [first_square, second_inner_square])
    ...  == intersect_multiregions(
    ...          [first_inner_square, second_inner_square],
    ...          [first_inner_square, second_inner_square, third_inner_square])
    ...  == intersect_multiregions(
    ...          [first_inner_square, second_inner_square, third_inner_square],
    ...          [first_inner_square, second_inner_square])
    ...  == Multipolygon([Polygon(first_inner_square, []),
    ...                   Polygon(second_inner_square, [])]))
    True
    >>> (intersect_multiregions([first_square, third_square],
    ...                         [first_square, third_square])
    ...  == Multipolygon([Polygon(first_square, []),
    ...                   Polygon(third_square, [])]))
    True
    """
    return _holeless.Intersection(
            _operands.MultiregionOperand(first),
            _operands.MultiregionOperand(second),
            _get_context() if context is None else context).compute()


def complete_intersect_polygons(first: _Polygon,
                                second: _Polygon,
                                *,
                                context: _Optional[_Context] = None
                                ) -> _Union[_Empty, _Mix, _Multipoint,
                                            _Multisegment, _Polygon, _Segment]:
    """
    Returns intersection of polygons considering cases
    with polygons touching each other in points/segments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = first_edges_count + second_edges_count``,
    ``first_edges_count = len(first.border.vertices)\
 + sum(len(hole.vertices) for hole in first.holes)``,
    ``second_edges_count = len(second.border.vertices)\
 + sum(len(hole.vertices) for hole in second.holes)``,
    ``intersections_count`` --- number of intersections between polygons edges.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Mix = context.mix_cls
    >>> Multipoint = context.multipoint_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> complete_intersect_polygons(Polygon(first_inner_square, []),
    ...                             Polygon(second_square, [])) is EMPTY
    True
    >>> (complete_intersect_polygons(Polygon(first_square, []),
    ...                              Polygon(third_square, []))
    ...  == Multipoint([Point(4, 4)]))
    True
    >>> (complete_intersect_polygons(Polygon(first_square, []),
    ...                              Polygon(second_square, []))
    ... == Segment(Point(4, 0), Point(4, 4)))
    True
    >>> (complete_intersect_polygons(Polygon(first_inner_square, []),
    ...                              Polygon(first_square,
    ...                                      [clockwise_first_inner_square]))
    ...  == Multisegment([Segment(Point(1, 1), Point(3, 1)),
    ...                   Segment(Point(1, 1), Point(1, 3)),
    ...                   Segment(Point(1, 3), Point(3, 3)),
    ...                   Segment(Point(3, 1), Point(3, 3))]))
    True
    >>> (complete_intersect_polygons(Polygon(first_square, []),
    ...                              Polygon(first_inner_square, []))
    ...  == Polygon(first_inner_square, []))
    True
    >>> (complete_intersect_polygons(Polygon(first_square, []),
    ...                              Polygon(first_square, []))
    ...  == Polygon(first_square, []))
    True
    >>> (complete_intersect_polygons(Polygon(first_square,
    ...                                      [clockwise_first_inner_square]),
    ...                              Polygon(first_square,
    ...                                      [clockwise_first_inner_square]))
    ...  == Polygon(first_square, [clockwise_first_inner_square]))
    True
    """
    return _holey.CompleteIntersection(
            _operands.PolygonOperand(first), _operands.PolygonOperand(second),
            _get_context() if context is None else context).compute()


def intersect_polygons(first: _Polygon,
                       second: _Polygon,
                       *,
                       context: _Optional[_Context] = None
                       ) -> _Union[_Empty, _Multipolygon, _Polygon]:
    """
    Returns intersection of polygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = first_edges_count + second_edges_count``,
    ``first_edges_count = len(first.border.vertices)\
 + sum(len(hole.vertices) for hole in first.holes)``,
    ``second_edges_count = len(second.border.vertices)\
 + sum(len(hole.vertices) for hole in second.holes)``,
    ``intersections_count`` --- number of intersections between polygons edges.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> (intersect_polygons(Polygon(first_inner_square, []),
    ...                     Polygon(second_square, []))
    ...  is intersect_polygons(Polygon(first_square, []),
    ...                        Polygon(second_square, []))
    ...  is intersect_polygons(Polygon(first_inner_square, []),
    ...                        Polygon(first_square,
    ...                                [clockwise_first_inner_square]))
    ...  is EMPTY)
    True
    >>> (intersect_polygons(Polygon(first_square, []),
    ...                     Polygon(first_inner_square, []))
    ...  == Polygon(first_inner_square, []))
    True
    >>> (intersect_polygons(Polygon(first_square,
    ...                             [clockwise_first_inner_square]),
    ...                     Polygon(first_square,
    ...                             [clockwise_first_inner_square]))
    ...  == Polygon(first_square, [clockwise_first_inner_square]))
    True
    """
    return _holey.Intersection(
            _operands.PolygonOperand(first), _operands.PolygonOperand(second),
            _get_context() if context is None else context).compute()


def subtract_polygons(minuend: _Polygon,
                      subtrahend: _Polygon,
                      *,
                      context: _Optional[_Context] = None
                      ) -> _Union[_Empty, _Multipolygon, _Polygon]:
    """
    Returns difference of polygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = minuend_edges_count + subtrahend_edges_count``,
    ``minuend_edges_count = len(minuend.border.vertices)\
 + sum(len(hole.vertices) for hole in minuend.holes)``,
    ``subtrahend_edges_count = len(subtrahend.border.vertices)\
 + sum(len(hole.vertices) for hole in subtrahend.holes)``,
    ``intersections_count`` --- number of intersections between polygons edges.

    :param minuend: polygon to subtract from.
    :param subtrahend: polygon to subtract.
    :param context: geometric context.
    :returns: difference between minuend and subtrahend.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> (subtract_polygons(Polygon(first_square, []),
    ...                    Polygon(first_square, []))
    ...  is subtract_polygons(Polygon(first_inner_square, []),
    ...                       Polygon(first_square, []))
    ...  is subtract_polygons(Polygon(first_square,
    ...                               [clockwise_first_inner_square]),
    ...                       Polygon(first_square,
    ...                               [clockwise_first_inner_square]))
    ...  is EMPTY)
    True
    >>> (subtract_polygons(Polygon(first_inner_square, []),
    ...                    Polygon(second_square, []))
    ...  == subtract_polygons(Polygon(first_inner_square, []),
    ...                       Polygon(first_square,
    ...                               [clockwise_first_inner_square]))
    ...  == Polygon(first_inner_square, []))
    True
    >>> (subtract_polygons(Polygon(first_square, []),
    ...                    Polygon(first_inner_square, []))
    ...  == subtract_polygons(Polygon(first_square, [first_inner_square]),
    ...                       Polygon(second_square, []))
    ...  == Polygon(first_square, [clockwise_first_inner_square]))
    True
    """
    return _holey.Difference(
            _operands.PolygonOperand(minuend),
            _operands.PolygonOperand(subtrahend),
            _get_context() if context is None else context).compute()


def symmetric_subtract_polygons(first: _Polygon,
                                second: _Polygon,
                                *,
                                context: _Optional[_Context] = None
                                ) -> _Union[_Empty, _Multipolygon, _Polygon]:
    """
    Returns symmetric difference of polygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = first_edges_count + second_edges_count``,
    ``first_edges_count = len(first.border.vertices)\
 + sum(len(hole.vertices) for hole in first.holes)``,
    ``second_edges_count = len(second.border.vertices)\
 + sum(len(hole.vertices) for hole in second.holes)``,
    ``intersections_count`` --- number of intersections between polygons edges.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: symmetric difference of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> (symmetric_subtract_polygons(Polygon(first_square, []),
    ...                              Polygon(first_square, []))
    ...  is symmetric_subtract_polygons(
    ...          Polygon(first_square, [clockwise_first_inner_square]),
    ...          Polygon(first_square, [clockwise_first_inner_square]))
    ...  is EMPTY)
    True
    >>> (symmetric_subtract_polygons(Polygon(first_square,
    ...                                      [clockwise_first_inner_square]),
    ...                              Polygon(first_inner_square, []))
    ...  == Polygon(first_square, []))
    True
    >>> (symmetric_subtract_polygons(Polygon(first_square, []),
    ...                              Polygon(second_square, []))
    ...  == Polygon(Contour([Point(0, 0), Point(8, 0), Point(8, 4),
    ...                      Point(0, 4)]), []))
    True
    >>> (symmetric_subtract_polygons(
    ...      Polygon(first_square, [clockwise_first_inner_square]),
    ...      Polygon(second_square, []))
    ...  == Polygon(Contour([Point(0, 0), Point(8, 0), Point(8, 4),
    ...                      Point(0, 4)]), [clockwise_first_inner_square]))
    True
    >>> (symmetric_subtract_polygons(Polygon(first_square, []),
    ...                              Polygon(third_square, []))
    ...  == Multipolygon([Polygon(first_square, []),
    ...                   Polygon(third_square, [])]))
    True
    >>> (symmetric_subtract_polygons(Polygon(first_square,
    ...                                      [clockwise_first_inner_square]),
    ...                              Polygon(third_square, []))
    ...  == Multipolygon([Polygon(first_square,
    ...                           [clockwise_first_inner_square]),
    ...                   Polygon(third_square, [])]))
    True
    """
    return _holey.SymmetricDifference(
            _operands.PolygonOperand(first), _operands.PolygonOperand(second),
            _get_context() if context is None else context).compute()


def unite_polygons(first: _Polygon,
                   second: _Polygon,
                   *,
                   context: _Optional[_Context] = None
                   ) -> _Union[_Multipolygon, _Polygon]:
    """
    Returns union of polygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = first_edges_count + second_edges_count``,
    ``first_edges_count = len(first.border.vertices)\
 + sum(len(hole.vertices) for hole in first.holes)``,
    ``second_edges_count = len(second.border.vertices)\
 + sum(len(hole.vertices) for hole in second.holes)``,
    ``intersections_count`` --- number of intersections between polygons edges.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: union of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> clockwise_second_inner_square = Contour([Point(5, 1), Point(7, 1),
    ...                                          Point(7, 3), Point(5, 3)])
    >>> clockwise_third_inner_square = Contour([Point(5, 5), Point(5, 7),
    ...                                         Point(7, 7), Point(7, 5)])
    >>> (unite_polygons(Polygon(first_square, []),
    ...                 Polygon(first_inner_square, []))
    ...  == unite_polygons(Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(first_inner_square, []))
    ...  == Polygon(first_square, []))
    True
    >>> (unite_polygons(Polygon(first_square, []),
    ...                 Polygon(second_square, []))
    ...  == Polygon(Contour([Point(0, 0), Point(8, 0), Point(8, 4),
    ...                      Point(0, 4)]), []))
    True
    >>> (unite_polygons(Polygon(first_square, [clockwise_first_inner_square]),
    ...                 Polygon(second_square, []))
    ...  == Polygon(Contour([Point(0, 0), Point(8, 0), Point(8, 4),
    ...                      Point(0, 4)]), [clockwise_first_inner_square]))
    True
    >>> (unite_polygons(Polygon(first_square, []),
    ...                 Polygon(third_square, []))
    ...  == Multipolygon([Polygon(first_square, []),
    ...                   Polygon(third_square, [])]))
    True
    >>> (unite_polygons(Polygon(first_square, [clockwise_first_inner_square]),
    ...                 Polygon(third_square, []))
    ...  == Multipolygon([Polygon(first_square,
    ...                           [clockwise_first_inner_square]),
    ...                   Polygon(third_square, [])]))
    True
    """
    return _holey.Union(
            _operands.PolygonOperand(first), _operands.PolygonOperand(second),
            _get_context() if context is None else context).compute()


def complete_intersect_polygon_with_multipolygon(
        polygon: _Polygon,
        multipolygon: _Multipolygon,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Mix, _Multipoint, _Multipolygon, _Multisegment, _Polygon,
            _Segment]:
    """
    Returns intersection of polygon with multipolygon considering cases
    with polygons touching each other in points/segments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = polygon_edges_count + multipolygon_edges_count``,
    ``polygon_edges_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``,
    ``multipolygon_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``,
    ``intersections_count`` --- number of intersections between polygons edges.

    :param polygon: first operand.
    :param multipolygon: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Mix = context.mix_cls
    >>> Multipoint = context.multipoint_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> clockwise_second_inner_square = Contour([Point(5, 1), Point(5, 3),
    ...                                          Point(7, 3), Point(7, 1)])
    >>> clockwise_third_inner_square = Contour([Point(5, 5), Point(5, 7),
    ...                                         Point(7, 7), Point(7, 5)])
    >>> (complete_intersect_polygon_with_multipolygon(
    ...      Polygon(first_inner_square, []),
    ...      Multipolygon([Polygon(second_square, []),
    ...                    Polygon(fourth_square, [])]))
    ...  is EMPTY)
    True
    >>> (complete_intersect_polygon_with_multipolygon(
    ...      Polygon(first_square, []),
    ...      Multipolygon([Polygon(second_inner_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Multipoint([Point(4, 4)]))
    True
    >>> (complete_intersect_polygon_with_multipolygon(
    ...      Polygon(first_square, []),
    ...      Multipolygon([Polygon(second_square, []),
    ...                    Polygon(fourth_square, [])]))
    ... == Multisegment([Segment(Point(0, 4), Point(4, 4)),
    ...                  Segment(Point(4, 0), Point(4, 4))]))
    True
    >>> (complete_intersect_polygon_with_multipolygon(
    ...      Polygon(first_inner_square, []),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square,
    ...                            [clockwise_third_inner_square])]))
    ...  == Multisegment([Segment(Point(1, 1), Point(3, 1)),
    ...                   Segment(Point(1, 1), Point(1, 3)),
    ...                   Segment(Point(1, 3), Point(3, 3)),
    ...                   Segment(Point(3, 1), Point(3, 3))]))
    True
    >>> (complete_intersect_polygon_with_multipolygon(
    ...      Polygon(first_square, []),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  == complete_intersect_polygon_with_multipolygon(
    ...          Polygon(first_inner_square, []),
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_square, [])]))
    ...  == complete_intersect_polygon_with_multipolygon(
    ...          Polygon(first_square, []),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == complete_intersect_polygon_with_multipolygon(
    ...          Polygon(first_inner_square, []),
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == complete_intersect_polygon_with_multipolygon(
    ...          Polygon(first_inner_square, []),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == complete_intersect_polygon_with_multipolygon(
    ...          Polygon(first_inner_square, []),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == Polygon(first_inner_square, []))
    True
    >>> (complete_intersect_polygon_with_multipolygon(
    ...      Polygon(first_square, []),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Polygon(first_square, []))
    True
    >>> (complete_intersect_polygon_with_multipolygon(
    ...      Polygon(first_square, []),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Mix(Multipoint([Point(4, 4)]), EMPTY,
    ...         Polygon(first_inner_square, [])))
    True
    >>> (complete_intersect_polygon_with_multipolygon(
    ...      Polygon(first_square, []),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Mix(EMPTY, Segment(Point(4, 0), Point(4, 4)),
    ...         Polygon(first_inner_square, [])))
    True
    """
    return _holey.CompleteIntersection(
            _operands.PolygonOperand(polygon),
            _operands.MultipolygonOperand(multipolygon),
            _get_context() if context is None else context).compute()


def intersect_polygon_with_multipolygon(polygon: _Polygon,
                                        multipolygon: _Multipolygon,
                                        *,
                                        context: _Optional[_Context] = None
                                        ) -> _Union[_Empty, _Multipolygon,
                                                    _Polygon]:
    """
    Returns intersection of multipolygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = polygon_edges_count + multipolygon_edges_count``,
    ``polygon_edges_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``,
    ``multipolygon_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``,
    ``intersections_count`` --- number of intersections between polygons edges.

    :param polygon: first operand.
    :param multipolygon: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> clockwise_second_inner_square = Contour([Point(5, 1), Point(5, 3),
    ...                                          Point(7, 3), Point(7, 1)])
    >>> clockwise_third_inner_square = Contour([Point(5, 5), Point(5, 7),
    ...                                         Point(7, 7), Point(7, 5)])
    >>> (intersect_polygon_with_multipolygon(
    ...      Polygon(first_inner_square, []),
    ...      Multipolygon([Polygon(second_square, []),
    ...                    Polygon(fourth_square, [])]))
    ...  is intersect_polygon_with_multipolygon(
    ...          Polygon(first_square, []),
    ...          Multipolygon([Polygon(second_square, []),
    ...                        Polygon(fourth_square, [])]))
    ...  is intersect_polygon_with_multipolygon(
    ...          Polygon(first_inner_square, []),
    ...          Multipolygon([Polygon(first_square,
    ...                                [clockwise_first_inner_square]),
    ...                        Polygon(third_square,
    ...                                [clockwise_third_inner_square])]))
    ...  is EMPTY)
    True
    >>> (intersect_polygon_with_multipolygon(
    ...      Polygon(first_square, []),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Polygon(first_inner_square, []))
    True
    >>> (intersect_polygon_with_multipolygon(
    ...      Polygon(first_square, []),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == intersect_polygon_with_multipolygon(
    ...          Polygon(first_square, []),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == intersect_polygon_with_multipolygon(
    ...          Polygon(first_inner_square, []),
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_square, [])]))
    ...  == intersect_polygon_with_multipolygon(
    ...          Polygon(first_square, []),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == intersect_polygon_with_multipolygon(
    ...          Polygon(first_inner_square, []),
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == intersect_polygon_with_multipolygon(
    ...          Polygon(first_inner_square, []),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == intersect_polygon_with_multipolygon(
    ...          Polygon(first_inner_square, []),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == Polygon(first_inner_square, []))
    True
    >>> (intersect_polygon_with_multipolygon(
    ...      Polygon(first_square, []),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Polygon(first_square, []))
    True
    """
    return _holey.Intersection(
            _operands.PolygonOperand(polygon),
            _operands.MultipolygonOperand(multipolygon),
            _get_context() if context is None else context).compute()


def subtract_multipolygon_from_polygon(minuend: _Polygon,
                                       subtrahend: _Multipolygon,
                                       *,
                                       context: _Optional[_Context] = None
                                       ) -> _Union[_Empty, _Multipolygon,
                                                   _Polygon]:
    """
    Returns difference of polygon with multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = first_edges_count + second_edges_count``,
    ``first_edges_count = len(minuend.border.vertices)\
 + sum(len(hole.vertices) for hole in minuend.holes)``,
    ``second_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in subtrahend.polygons)``,
    ``intersections_count`` --- number of intersections between polygons edges.

    :param minuend: polygon to subtract from.
    :param subtrahend: multipolygon to subtract.
    :param context: geometric context.
    :returns: difference between minuend and subtrahend.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> outer_square = Contour([Point(0, 0), Point(8, 0), Point(8, 8),
    ...                         Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> clockwise_second_inner_square = Contour([Point(5, 1), Point(5, 3),
    ...                                          Point(7, 3), Point(7, 1)])
    >>> clockwise_third_inner_square = Contour([Point(5, 5), Point(5, 7),
    ...                                         Point(7, 7), Point(7, 5)])
    >>> (subtract_multipolygon_from_polygon(
    ...      Polygon(first_square, []),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  is subtract_multipolygon_from_polygon(
    ...          Polygon(first_inner_square, []),
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_square, [])]))
    ...  is subtract_multipolygon_from_polygon(
    ...          Polygon(first_inner_square, []),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  is EMPTY)
    True
    >>> (subtract_multipolygon_from_polygon(
    ...      Polygon(first_inner_square, []),
    ...      Multipolygon([Polygon(second_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ... == subtract_multipolygon_from_polygon(
    ...          Polygon(first_inner_square, []),
    ...          Multipolygon([Polygon(first_square,
    ...                                [clockwise_first_inner_square]),
    ...                        Polygon(third_square,
    ...                                [clockwise_third_inner_square])]))
    ...  == Polygon(first_inner_square, []))
    True
    >>> (subtract_multipolygon_from_polygon(
    ...      Polygon(first_square, []),
    ...      Multipolygon([Polygon(second_square, []),
    ...                    Polygon(fourth_square, [])]))
    ...  == Polygon(first_square, []))
    True
    >>> (subtract_multipolygon_from_polygon(
    ...      Polygon(first_square, []),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Polygon(first_square, [clockwise_first_inner_square]))
    True
    >>> (subtract_multipolygon_from_polygon(
    ...      Polygon(outer_square, []),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Multipolygon([Polygon(fourth_square, []),
    ...                   Polygon(second_square, [])]))
    True
    >>> (subtract_multipolygon_from_polygon(
    ...      Polygon(outer_square, []),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square,
    ...                            [clockwise_third_inner_square])]))
    ...  == Multipolygon([Polygon(fourth_square, []),
    ...                   Polygon(first_inner_square, []),
    ...                   Polygon(second_square, []),
    ...                   Polygon(third_inner_square, [])]))
    True
    >>> (subtract_multipolygon_from_polygon(
    ...      Polygon(outer_square, []),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, []),
    ...                    Polygon(third_inner_square, []),
    ...                    Polygon(fourth_square, [])]))
    ...  == Multipolygon([Polygon(first_square,
    ...                           [clockwise_first_inner_square]),
    ...                   Polygon(third_square,
    ...                           [clockwise_third_inner_square])]))
    True
    """
    return _holey.Difference(
            _operands.PolygonOperand(minuend),
            _operands.MultipolygonOperand(subtrahend),
            _get_context() if context is None else context).compute()


def subtract_polygon_from_multipolygon(minuend: _Multipolygon,
                                       subtrahend: _Polygon,
                                       *,
                                       context: _Optional[_Context] = None
                                       ) -> _Union[_Empty, _Multipolygon,
                                                   _Polygon]:
    """
    Returns difference of multipolygon with polygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = minuend_edges_count + subtrahend_edges_count``,
    ``minuend_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in minuend.polygons)``,
    ``subtrahend_edges_count = len(subtrahend.border.vertices)\
 + sum(len(hole.vertices) for hole in subtrahend.holes)``,
    ``intersections_count`` --- number of intersections between polygons edges.

    :param minuend: multipolygon to subtract from.
    :param subtrahend: polygon to subtract.
    :param context: geometric context.
    :returns: difference between minuend and subtrahend.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> outer_square = Contour([Point(0, 0), Point(8, 0), Point(8, 8),
    ...                         Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> clockwise_second_inner_square = Contour([Point(5, 1), Point(5, 3),
    ...                                          Point(7, 3), Point(7, 1)])
    >>> clockwise_third_inner_square = Contour([Point(5, 5), Point(5, 7),
    ...                                         Point(7, 7), Point(7, 5)])
    >>> (subtract_polygon_from_multipolygon(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]),
    ...      Polygon(outer_square, []))
    ...  is subtract_polygon_from_multipolygon(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Polygon(outer_square, []))
    ...  is EMPTY)
    True
    >>> (subtract_polygon_from_multipolygon(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]),
    ...      Polygon(third_square, []))
    ...  == Polygon(first_square, []))
    True
    >>> (subtract_polygon_from_multipolygon(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_inner_square, [])]),
    ...          Polygon(third_inner_square, []))
    ...  == subtract_polygon_from_multipolygon(
    ...              Multipolygon([Polygon(first_inner_square, []),
    ...                            Polygon(second_inner_square, []),
    ...                            Polygon(third_inner_square, [])]),
    ...              Polygon(third_inner_square, []))
    ...  == subtract_polygon_from_multipolygon(
    ...              Multipolygon([Polygon(first_square, []),
    ...                            Polygon(second_inner_square, [])]),
    ...              Polygon(first_square, [clockwise_first_inner_square]))
    ...  == Multipolygon([Polygon(first_inner_square, []),
    ...                   Polygon(second_inner_square, [])]))
    True
    >>> (subtract_polygon_from_multipolygon(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]),
    ...      Polygon(second_square, []))
    ...  == Multipolygon([Polygon(first_square, []),
    ...                   Polygon(third_square, [])]))
    True
    >>> (subtract_polygon_from_multipolygon(
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_square, [])]),
    ...          Polygon(first_inner_square, []))
    ...  == subtract_polygon_from_multipolygon(
    ...              Multipolygon([Polygon(first_square,
    ...                                    [clockwise_first_inner_square]),
    ...                            Polygon(third_square, [])]),
    ...              Polygon(first_inner_square, []))
    ...  == Multipolygon([Polygon(first_square,
    ...                           [clockwise_first_inner_square]),
    ...                   Polygon(third_square, [])]))
    True
    """
    return _holey.Difference(
            _operands.MultipolygonOperand(minuend),
            _operands.PolygonOperand(subtrahend),
            _get_context() if context is None else context).compute()


def symmetric_subtract_multipolygon_from_polygon(
        polygon: _Polygon,
        multipolygon: _Multipolygon,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Multipolygon, _Polygon]:
    """
    Returns symmetric difference of polygon with multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = polygon_edges_count + multipolygon_edges_count``,
    ``polygon_edges_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``,
    ``multipolygon_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``,
    ``intersections_count`` --- number of intersections between polygons edges.

    :param polygon: first operand.
    :param multipolygon: second operand.
    :param context: geometric context.
    :returns: symmetric difference of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> outer_square = Contour([Point(0, 0), Point(8, 0), Point(8, 8),
    ...                         Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> clockwise_second_inner_square = Contour([Point(5, 1), Point(5, 3),
    ...                                          Point(7, 3), Point(7, 1)])
    >>> clockwise_third_inner_square = Contour([Point(5, 5), Point(5, 7),
    ...                                         Point(7, 7), Point(7, 5)])
    >>> (symmetric_subtract_multipolygon_from_polygon(
    ...      Polygon(first_square, []),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Polygon(third_square, []))
    True
    >>> (symmetric_subtract_multipolygon_from_polygon(
    ...          Polygon(first_square, []),
    ...          Multipolygon([Polygon(second_square, []),
    ...                        Polygon(fourth_square, [])]))
    ...  == Polygon(Contour([Point(0, 0), Point(8, 0), Point(8, 4),
    ...                      Point(4, 4), Point(4, 8), Point(0, 8)]), []))
    True
    >>> (symmetric_subtract_multipolygon_from_polygon(
    ...      Polygon(outer_square, []),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  == Polygon(outer_square, [clockwise_first_inner_square,
    ...                            clockwise_second_inner_square,
    ...                            clockwise_third_inner_square]))
    True
    >>> (symmetric_subtract_multipolygon_from_polygon(
    ...          Polygon(first_inner_square, []),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == Multipolygon([Polygon(second_inner_square, []),
    ...                   Polygon(third_inner_square, [])]))
    True
    >>> (symmetric_subtract_multipolygon_from_polygon(
    ...      Polygon(first_inner_square, []),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square, [])]))
    ... == symmetric_subtract_multipolygon_from_polygon(
    ...          Polygon(outer_square, []),
    ...          Multipolygon([Polygon(second_square, []),
    ...                        Polygon(fourth_square, [])]))
    ... == Multipolygon([Polygon(first_square, []),
    ...                  Polygon(third_square, [])]))
    True
    >>> (symmetric_subtract_multipolygon_from_polygon(
    ...      Polygon(first_inner_square, []),
    ...      Multipolygon([Polygon(second_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  == Multipolygon([Polygon(first_inner_square, []),
    ...                   Polygon(second_inner_square, []),
    ...                   Polygon(third_inner_square, [])]))
    True
    >>> (symmetric_subtract_multipolygon_from_polygon(
    ...      Polygon(outer_square, []),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square,
    ...                            [clockwise_third_inner_square])]))
    ...  == symmetric_subtract_multipolygon_from_polygon(
    ...          Polygon(outer_square, [clockwise_first_inner_square,
    ...                                 clockwise_third_inner_square]),
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_square, [])]))
    ...  == Multipolygon([Polygon(fourth_square, []),
    ...                   Polygon(first_inner_square, []),
    ...                   Polygon(second_square, []),
    ...                   Polygon(third_inner_square, [])]))
    True
    >>> (symmetric_subtract_multipolygon_from_polygon(
    ...      Polygon(first_square, []),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  == symmetric_subtract_multipolygon_from_polygon(
    ...          Polygon(first_inner_square, []),
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == Multipolygon([Polygon(first_square,
    ...                           [clockwise_first_inner_square]),
    ...                   Polygon(third_inner_square, [])]))
    True
    >>> (symmetric_subtract_multipolygon_from_polygon(
    ...      Polygon(outer_square, []),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, []),
    ...                    Polygon(third_inner_square, []),
    ...                    Polygon(fourth_square, [])]))
    ...  == Multipolygon([Polygon(first_square,
    ...                           [clockwise_first_inner_square]),
    ...                   Polygon(third_square,
    ...                           [clockwise_third_inner_square])]))
    True
    """
    return _holey.SymmetricDifference(
            _operands.PolygonOperand(polygon),
            _operands.MultipolygonOperand(multipolygon),
            _get_context() if context is None else context).compute()


def unite_polygon_with_multipolygon(polygon: _Polygon,
                                    multipolygon: _Multipolygon,
                                    *,
                                    context: _Optional[_Context] = None
                                    ) -> _Union[_Multipolygon, _Polygon]:
    """
    Returns union of polygon with multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = polygon_edges_count + multipolygon_edges_count``,
    ``polygon_edges_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``,
    ``multipolygon_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``,
    ``intersections_count`` --- number of intersections between polygons edges.

    :param polygon: first operand.
    :param multipolygon: second operand.
    :param context: geometric context.
    :returns: union of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> outer_square = Contour([Point(0, 0), Point(8, 0), Point(8, 8),
    ...                         Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> clockwise_second_inner_square = Contour([Point(5, 1), Point(7, 1),
    ...                                          Point(7, 3), Point(5, 3)])
    >>> clockwise_third_inner_square = Contour([Point(5, 5), Point(5, 7),
    ...                                         Point(7, 7), Point(7, 5)])
    >>> (unite_polygon_with_multipolygon(
    ...          Polygon(first_square, []),
    ...          Multipolygon([Polygon(second_square, []),
    ...                        Polygon(fourth_square, [])]))
    ...  == Polygon(Contour([Point(0, 0), Point(8, 0), Point(8, 4),
    ...                      Point(4, 4), Point(4, 8), Point(0, 8)]), []))
    True
    >>> (unite_polygon_with_multipolygon(
    ...      Polygon(outer_square, []),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  == unite_polygon_with_multipolygon(
    ...          Polygon(outer_square, []),
    ...          Multipolygon([Polygon(first_square,
    ...                                [clockwise_first_inner_square]),
    ...                        Polygon(third_square,
    ...                                [clockwise_third_inner_square])]))
    ...  == Polygon(outer_square, []))
    True
    >>> (unite_polygon_with_multipolygon(
    ...      Polygon(first_inner_square, []),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square, [])]))
    ... == Multipolygon([Polygon(first_square, []),
    ...                  Polygon(third_square, [])]))
    True
    >>> (unite_polygon_with_multipolygon(
    ...      Polygon(first_inner_square, []),
    ...      Multipolygon([Polygon(second_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  == unite_polygon_with_multipolygon(
    ...          Polygon(first_inner_square, []),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == Multipolygon([Polygon(first_inner_square, []),
    ...                   Polygon(second_inner_square, []),
    ...                   Polygon(third_inner_square, [])]))
    True
    >>> (unite_polygon_with_multipolygon(
    ...      Polygon(first_square, [clockwise_first_inner_square]),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square,
    ...                            [clockwise_third_inner_square])]))
    ...  == Multipolygon([Polygon(first_square,
    ...                           [clockwise_first_inner_square]),
    ...                   Polygon(third_square,
    ...                           [clockwise_third_inner_square])]))
    True
    """
    return _holey.Union(
            _operands.PolygonOperand(polygon),
            _operands.MultipolygonOperand(multipolygon),
            _get_context() if context is None else context).compute()


def complete_intersect_multipolygons(
        first: _Multipolygon,
        second: _Multipolygon,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Mix, _Multipoint, _Multipolygon, _Multisegment, _Polygon,
            _Segment]:
    """
    Returns intersection of multipolygons considering cases
    with polygons touching each other in points/segments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = first_edges_count + second_edges_count``,
    ``first_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in first.polygons)``,
    ``second_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in second.polygons)``,
    ``intersections_count`` --- number of intersections between multipolygons
    edges.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Mix = context.mix_cls
    >>> Multipoint = context.multipoint_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> clockwise_second_inner_square = Contour([Point(5, 1), Point(5, 3),
    ...                                          Point(7, 3), Point(7, 1)])
    >>> clockwise_third_inner_square = Contour([Point(5, 5), Point(5, 7),
    ...                                         Point(7, 7), Point(7, 5)])
    >>> (complete_intersect_multipolygons(
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(second_square, []),
    ...                    Polygon(fourth_square, [])]))
    ...  is EMPTY)
    True
    >>> (complete_intersect_multipolygons(
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]),
    ...      Multipolygon([Polygon(third_inner_square, []),
    ...                    Polygon(fourth_square, [])]))
    ...  == Multipoint([Point(4, 4)]))
    True
    >>> (complete_intersect_multipolygons(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]),
    ...      Multipolygon([Polygon(second_square, []),
    ...                    Polygon(fourth_square, [])]))
    ... == Multisegment([Segment(Point(0, 4), Point(4, 4)),
    ...                  Segment(Point(4, 0), Point(4, 4)),
    ...                  Segment(Point(4, 4), Point(8, 4)),
    ...                  Segment(Point(4, 4), Point(4, 8))]))
    True
    >>> (complete_intersect_multipolygons(
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(third_square,
    ...                            [clockwise_third_inner_square])]))
    ...  == Multisegment([Segment(Point(1, 1), Point(3, 1)),
    ...                   Segment(Point(1, 1), Point(1, 3)),
    ...                   Segment(Point(1, 3), Point(3, 3)),
    ...                   Segment(Point(3, 1), Point(3, 3)),
    ...                   Segment(Point(5, 5), Point(7, 5)),
    ...                   Segment(Point(5, 5), Point(5, 7)),
    ...                   Segment(Point(5, 7), Point(7, 7)),
    ...                   Segment(Point(7, 5), Point(7, 7))]))
    True
    >>> (complete_intersect_multipolygons(
    ...      Multipolygon([Polygon(first_square,
    ...                            [clockwise_first_inner_square]),
    ...                    Polygon(second_inner_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square,
    ...                            [clockwise_second_inner_square])]))
    ...  == Multisegment([Segment(Point(1, 1), Point(3, 1)),
    ...                   Segment(Point(1, 1), Point(1, 3)),
    ...                   Segment(Point(1, 3), Point(3, 3)),
    ...                   Segment(Point(3, 1), Point(3, 3)),
    ...                   Segment(Point(4, 0), Point(4, 4)),
    ...                   Segment(Point(5, 1), Point(7, 1)),
    ...                   Segment(Point(5, 1), Point(5, 3)),
    ...                   Segment(Point(5, 3), Point(7, 3)),
    ...                   Segment(Point(7, 1), Point(7, 3))]))
    True
    >>> (complete_intersect_multipolygons(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Multipolygon([Polygon(first_square, []),
    ...                   Polygon(third_square, [])]))
    True
    >>> (complete_intersect_multipolygons(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  == complete_intersect_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_square, [])]))
    ...  == complete_intersect_multipolygons(
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == complete_intersect_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == complete_intersect_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == complete_intersect_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == Multipolygon([Polygon(first_inner_square, []),
    ...                   Polygon(third_inner_square, [])]))
    True
    >>> (complete_intersect_multipolygons(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(second_inner_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square,
    ...                            [clockwise_second_inner_square])]))
    ...  == Mix(EMPTY, Multisegment([Segment(Point(4, 0), Point(4, 4)),
    ...                              Segment(Point(5, 1), Point(7, 1)),
    ...                              Segment(Point(5, 1), Point(5, 3)),
    ...                              Segment(Point(5, 3), Point(7, 3)),
    ...                              Segment(Point(7, 1), Point(7, 3))]),
    ...         Polygon(first_inner_square, [])))
    True
    >>> (complete_intersect_multipolygons(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Mix(Multipoint([Point(4, 4)]), EMPTY,
    ...         Multipolygon([Polygon(first_inner_square, []),
    ...                       Polygon(third_inner_square, [])])))
    True
    >>> (complete_intersect_multipolygons(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(second_inner_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Mix(EMPTY, Segment(Point(4, 0), Point(4, 4)),
    ...         Multipolygon([Polygon(first_inner_square, []),
    ...                       Polygon(second_inner_square, [])])))
    True
    """
    return _holey.CompleteIntersection(
            _operands.MultipolygonOperand(first),
            _operands.MultipolygonOperand(second),
            _get_context() if context is None else context).compute()


def intersect_multipolygons(first: _Multipolygon,
                            second: _Multipolygon,
                            *,
                            context: _Optional[_Context] = None
                            ) -> _Union[_Empty, _Multipolygon, _Polygon]:
    """
    Returns intersection of multipolygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = first_edges_count + second_edges_count``,
    ``first_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in first.polygons)``,
    ``second_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in second.polygons)``,
    ``intersections_count`` --- number of intersections between multipolygons
    edges.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> clockwise_second_inner_square = Contour([Point(5, 1), Point(7, 1),
    ...                                          Point(7, 3), Point(5, 3)])
    >>> clockwise_third_inner_square = Contour([Point(5, 5), Point(5, 7),
    ...                                         Point(7, 7), Point(7, 5)])
    >>> (intersect_multipolygons(
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(second_square, []),
    ...                    Polygon(fourth_square, [])]))
    ...  is intersect_multipolygons(
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_square, [])]),
    ...          Multipolygon([Polygon(second_square, []),
    ...                        Polygon(fourth_square, [])]))
    ...  is intersect_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_square,
    ...                                [clockwise_first_inner_square]),
    ...                        Polygon(third_square,
    ...                                [clockwise_third_inner_square])]))
    ...  is EMPTY)
    True
    >>> (intersect_multipolygons(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(second_inner_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Multipolygon([Polygon(first_inner_square, []),
    ...                   Polygon(second_inner_square, [])]))
    True
    >>> (intersect_multipolygons(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == intersect_multipolygons(
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == intersect_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_square, [])]))
    ...  == intersect_multipolygons(
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == intersect_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == intersect_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == intersect_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == Multipolygon([Polygon(first_inner_square, []),
    ...                   Polygon(third_inner_square, [])]))
    True
    >>> (intersect_multipolygons(Multipolygon([Polygon(first_square, []),
    ...                                        Polygon(third_square, [])]),
    ...                          Multipolygon([Polygon(first_square, []),
    ...                                        Polygon(third_square, [])]))
    ...  == Multipolygon([Polygon(first_square, []),
    ...                   Polygon(third_square, [])]))
    True
    """
    return _holey.Intersection(
            _operands.MultipolygonOperand(first),
            _operands.MultipolygonOperand(second),
            _get_context() if context is None else context).compute()


def subtract_multipolygons(minuend: _Multipolygon,
                           subtrahend: _Multipolygon,
                           *,
                           context: _Optional[_Context] = None
                           ) -> _Union[_Empty, _Multipolygon, _Polygon]:
    """
    Returns difference of multipolygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = minuend_edges_count + subtrahend_edges_count``,
    ``minuend_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in minuend.polygons)``,
    ``subtrahend_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in subtrahend.polygons)``,
    ``intersections_count`` --- number of intersections between multipolygons
    edges.

    :param minuend: multipolygon to subtract from.
    :param subtrahend: multipolygon to subtract.
    :param context: geometric context.
    :returns: difference between minuend and subtrahend.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> clockwise_second_inner_square = Contour([Point(5, 1), Point(5, 3),
    ...                                          Point(7, 3), Point(7, 1)])
    >>> clockwise_third_inner_square = Contour([Point(5, 5), Point(5, 7),
    ...                                         Point(7, 7), Point(7, 5)])
    >>> (subtract_multipolygons(Multipolygon([Polygon(first_square, []),
    ...                                       Polygon(third_square, [])]),
    ...                         Multipolygon([Polygon(first_square, []),
    ...                                       Polygon(third_square, [])]))
    ...  is subtract_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_square, [])]))
    ...  is subtract_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  is subtract_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  is EMPTY)
    True
    >>> (subtract_multipolygons(
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_inner_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  == Polygon(second_inner_square, []))
    True
    >>> (subtract_multipolygons(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(second_inner_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == subtract_multipolygons(
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_square, [])]))
    ...  == subtract_multipolygons(
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == Polygon(first_square, [clockwise_first_inner_square]))
    True
    >>> (subtract_multipolygons(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]),
    ...      Multipolygon([Polygon(second_square, []),
    ...                    Polygon(fourth_square, [])]))
    ...  == Multipolygon([Polygon(first_square, []),
    ...                   Polygon(third_square, [])]))
    True
    >>> (subtract_multipolygons(
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(second_square, []),
    ...                    Polygon(fourth_square, [])]))
    ... == subtract_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_square,
    ...                                [clockwise_first_inner_square]),
    ...                        Polygon(third_square,
    ...                                [clockwise_third_inner_square])]))
    ... == Multipolygon([Polygon(first_inner_square, []),
    ...                  Polygon(third_inner_square, [])]))
    True
    >>> (subtract_multipolygons(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  == Multipolygon([Polygon(first_square,
    ...                           [clockwise_first_inner_square]),
    ...                   Polygon(third_square,
    ...                           [clockwise_third_inner_square])]))
    True
    """
    return _holey.Difference(
            _operands.MultipolygonOperand(minuend),
            _operands.MultipolygonOperand(subtrahend),
            _get_context() if context is None else context).compute()


def symmetric_subtract_multipolygons(first: _Multipolygon,
                                     second: _Multipolygon,
                                     *,
                                     context: _Optional[_Context] = None
                                     ) -> _Union[_Empty, _Multipolygon,
                                                 _Polygon]:
    """
    Returns symmetric difference of multipolygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = first_edges_count + second_edges_count``,
    ``first_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in first.polygons)``,
    ``second_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in second.polygons)``,
    ``intersections_count`` --- number of intersections between multipolygons
    edges.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: symmetric difference of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> clockwise_second_inner_square = Contour([Point(5, 1), Point(5, 3),
    ...                                          Point(7, 3), Point(7, 1)])
    >>> clockwise_third_inner_square = Contour([Point(5, 5), Point(5, 7),
    ...                                         Point(7, 7), Point(7, 5)])
    >>> (symmetric_subtract_multipolygons(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  is EMPTY)
    True
    >>> (symmetric_subtract_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == symmetric_subtract_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == Polygon(second_inner_square, []))
    True
    >>> (symmetric_subtract_multipolygons(
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_square, [])]),
    ...          Multipolygon([Polygon(second_square, []),
    ...                        Polygon(fourth_square, [])]))
    ...  == Polygon(Contour([Point(0, 0), Point(8, 0), Point(8, 8),
    ...                      Point(0, 8)]), []))
    True
    >>> (symmetric_subtract_multipolygons(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  == symmetric_subtract_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == Polygon(first_square, [clockwise_first_inner_square]))
    True
    >>> (symmetric_subtract_multipolygons(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(second_inner_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Polygon(Contour([Point(0, 0), Point(8, 0), Point(8, 4),
    ...                      Point(0, 4)]),
    ...             [clockwise_first_inner_square,
    ...              clockwise_second_inner_square]))
    True
    >>> (symmetric_subtract_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_square,
    ...                                [clockwise_first_inner_square]),
    ...                        Polygon(third_square,
    ...                                [clockwise_third_inner_square])]))
    ... == Multipolygon([Polygon(first_square, []),
    ...                  Polygon(third_square, [])]))
    True
    >>> (symmetric_subtract_multipolygons(
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(second_square, []),
    ...                    Polygon(fourth_square, [])]))
    ...  == Multipolygon([Polygon(fourth_square, []),
    ...                   Polygon(first_inner_square, []),
    ...                   Polygon(second_square, []),
    ...                   Polygon(third_inner_square, [])]))
    True
    >>> (symmetric_subtract_multipolygons(
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == symmetric_subtract_multipolygons(
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_square, [])]))
    ...  == symmetric_subtract_multipolygons(
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == Multipolygon([Polygon(first_square,
    ...                           [clockwise_first_inner_square]),
    ...                   Polygon(third_square,
    ...                           [clockwise_third_inner_square])]))
    True
    """
    return _holey.SymmetricDifference(
            _operands.MultipolygonOperand(first),
            _operands.MultipolygonOperand(second),
            _get_context() if context is None else context).compute()


def unite_multipolygons(first: _Multipolygon,
                        second: _Multipolygon,
                        *,
                        context: _Optional[_Context] = None
                        ) -> _Union[_Multipolygon, _Polygon]:
    """
    Returns union of multipolygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = first_edges_count + second_edges_count``,
    ``first_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in first.polygons)``,
    ``second_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in second.polygons)``,
    ``intersections_count`` --- number of intersections between multipolygons
    edges.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context.
    :returns: union of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> clockwise_first_inner_square = Contour([Point(1, 1), Point(1, 3),
    ...                                         Point(3, 3), Point(3, 1)])
    >>> clockwise_second_inner_square = Contour([Point(5, 1), Point(7, 1),
    ...                                          Point(7, 3), Point(5, 3)])
    >>> clockwise_third_inner_square = Contour([Point(5, 5), Point(5, 7),
    ...                                         Point(7, 7), Point(7, 5)])
    >>> (unite_multipolygons(Multipolygon([Polygon(first_square, []),
    ...                                    Polygon(second_inner_square, [])]),
    ...                      Multipolygon([Polygon(first_inner_square, []),
    ...                                    Polygon(second_square, [])]))
    ...  == Polygon(Contour([Point(0, 0), Point(8, 0), Point(8, 4),
    ...                      Point(0, 4)]), []))
    True
    >>> (unite_multipolygons(Multipolygon([Polygon(first_square, []),
    ...                                    Polygon(third_square, [])]),
    ...                      Multipolygon([Polygon(second_square, []),
    ...                                    Polygon(fourth_square, [])]))
    ...  == Polygon(Contour([Point(0, 0), Point(8, 0), Point(8, 8),
    ...                      Point(0, 8)]), []))
    True
    >>> (unite_multipolygons(Multipolygon([Polygon(first_square, []),
    ...                                    Polygon(third_inner_square, [])]),
    ...                      Multipolygon([Polygon(first_inner_square, []),
    ...                                    Polygon(third_inner_square, [])]))
    ...  == unite_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == Multipolygon([Polygon(first_square, []),
    ...                   Polygon(third_inner_square, [])]))
    True
    >>> (unite_multipolygons(Multipolygon([Polygon(first_square, []),
    ...                                    Polygon(third_square, [])]),
    ...                      Multipolygon([Polygon(first_square, []),
    ...                                    Polygon(third_square, [])]))
    ...  == unite_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_square,
    ...                                [clockwise_first_inner_square]),
    ...                        Polygon(third_square,
    ...                                [clockwise_third_inner_square])]))
    ... == unite_multipolygons(Multipolygon([Polygon(first_inner_square, []),
    ...                                      Polygon(third_inner_square, [])]),
    ...                        Multipolygon([Polygon(first_square, []),
    ...                                      Polygon(third_square, [])]))
    ... == unite_multipolygons(Multipolygon([Polygon(first_square, []),
    ...                                      Polygon(third_inner_square, [])]),
    ...                        Multipolygon([Polygon(first_inner_square, []),
    ...                                      Polygon(third_square, [])]))
    ...  == unite_multipolygons(
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ... == Multipolygon([Polygon(first_square, []),
    ...                  Polygon(third_square, [])]))
    True
    >>> (unite_multipolygons(Multipolygon([Polygon(first_inner_square, []),
    ...                                    Polygon(third_inner_square, [])]),
    ...                      Multipolygon([Polygon(first_inner_square, []),
    ...                                    Polygon(second_inner_square, []),
    ...                                    Polygon(third_inner_square, [])]))
    ...  == unite_multipolygons(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(second_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]))
    ...  == Multipolygon([Polygon(first_inner_square, []),
    ...                   Polygon(second_inner_square, []),
    ...                   Polygon(third_inner_square, [])]))
    True
    >>> (unite_multipolygons(
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(second_square, []),
    ...                    Polygon(fourth_square, [])]))
    ...  == Multipolygon([Polygon(fourth_square, []),
    ...                   Polygon(first_inner_square, []),
    ...                   Polygon(second_square, []),
    ...                   Polygon(third_inner_square, [])]))
    True
    """
    return _holey.Union(
            _operands.MultipolygonOperand(first),
            _operands.MultipolygonOperand(second),
            _get_context() if context is None else context).compute()
