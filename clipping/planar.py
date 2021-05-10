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
                   mixed as _mixed)
from .hints import Multiregion as _Multiregion


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
    :param context: geometric context
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
    :param context: geometric context
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
            first, second,
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
    :param context: geometric context
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
            first, second,
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
    :param context: geometric context
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
    return _linear.Difference(
            minuend, subtrahend,
            _get_context() if context is None else context).compute()


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
    :param context: geometric context
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
            first, second,
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
    :param context: geometric context
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
    return _linear.Union(
            first, second,
            _get_context() if context is None else context).compute()


def intersect_multisegment_with_multipolygon(
        multisegment: _Multisegment,
        multipolygon: _Multipolygon,
        *,
        context: _Optional[_Context] = None) -> _Multisegment:
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
    :param context: geometric context
    :returns: intersection of multisegment with multipolygon.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> (intersect_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]),
    ...      Multipolygon([Polygon(Contour([Point(0, 0), Point(1, 0),
    ...                                     Point(0, 1)]), [])]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    True
    >>> (intersect_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(1, 1), Point(2, 2))]),
    ...      Multipolygon([Polygon(Contour([Point(0, 0), Point(1, 0),
    ...                                     Point(1, 1), Point(0, 1)]), [])]))
    ...  == Segment(Point(0, 0), Point(1, 0)))
    True
    """
    return _mixed.Intersection(
            multisegment, multipolygon,
            _get_context() if context is None else context).compute()


def complete_intersect_multisegment_with_multipolygon(
        multisegment: _Multisegment,
        multipolygon: _Multipolygon,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Mix, _Multipoint, _Multisegment, _Segment]:
    """
    Returns intersection of multisegment with multipolygon considering cases
    with geometries touching each other in points/segments.

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
    :param context: geometric context
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
    >>> (complete_intersect_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]),
    ...      Multipolygon([Polygon(Contour([Point(0, 0), Point(1, 0),
    ...                                     Point(0, 1)]), [])]))
    ...  == Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    True
    >>> (complete_intersect_multisegment_with_multipolygon(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(1, 1), Point(2, 2))]),
    ...      Multipolygon([Polygon(Contour([Point(0, 0), Point(1, 0),
    ...                                     Point(1, 1), Point(0, 1)]), [])]))
    ...  == Mix(Multipoint([Point(1, 1)]), Segment(Point(0, 0), Point(1, 0)),
    ...         EMPTY))
    True
    """
    return _mixed.CompleteIntersection(
            multisegment, multipolygon,
            _get_context() if context is None else context).compute()


def subtract_multipolygon_from_multisegment(multisegment: _Multisegment,
                                            multipolygon: _Multipolygon,
                                            *,
                                            context: _Optional[_Context] = None
                                            ) -> _Multisegment:
    """
    Returns difference of multisegment with multipolygon.

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

    :param multisegment: multisegment to subtract from.
    :param multipolygon: multipolygon to subtract.
    :param context: geometric context
    :returns: difference of multisegment with multipolygon.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> EMPTY = context.empty
    >>> Contour = context.contour_cls
    >>> Multipoint = context.multipoint_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> (subtract_multipolygon_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(0, 1), Point(1, 0))]),
    ...      Multipolygon([Polygon(Contour([Point(0, 0), Point(1, 0),
    ...                                     Point(0, 1)]), [])]))
    ...  is EMPTY)
    True
    >>> (subtract_multipolygon_from_multisegment(
    ...      Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                    Segment(Point(1, 1), Point(2, 2))]),
    ...      Multipolygon([Polygon(Contour([Point(0, 0), Point(1, 0),
    ...                                     Point(1, 1), Point(0, 1)]), [])]))
    ...  == Segment(Point(1, 1), Point(2, 2)))
    True
    """
    return _mixed.Difference(
            multisegment, multipolygon,
            _get_context() if context is None else context).compute()


def complete_intersect_multiregions(first: _Multiregion,
                                    second: _Multiregion,
                                    *,
                                    context: _Optional[_Context] = None
                                    ) -> _Union[_Empty, _Mix, _Multipoint,
                                                _Multipolygon, _Multisegment,
                                                _Polygon, _Segment]:
    """
    Returns intersection of multiregions considering cases
    with regions touching each other in points/segments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = left_edges_count + right_edges_count``,
    ``first_edges_count = sum(len(region.vertices) for region in first)``,
    ``second_edges_count = sum(len(region.vertices) for region in second)``,
    ``intersections_count`` --- number of intersections between multiregions
    edges.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context
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
            first, second,
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
    ``edges_count = left_edges_count + right_edges_count``,
    ``first_edges_count = sum(len(region.vertices) for region in first)``,
    ``second_edges_count = sum(len(region.vertices) for region in second)``,
    ``intersections_count`` --- number of intersections between multiregions
    edges.

    :param first: first operand.
    :param second: second operand.
    :param context: geometric context
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
            first, second,
            _get_context() if context is None else context).compute()


def complete_intersect_polygon_with_multipolygon(
        polygon: _Polygon,
        multipolygon: _Multipolygon,
        *,
        context: _Optional[_Context] = None
) -> _Union[_Empty, _Mix, _Multipoint, _Multipolygon, _Multisegment, _Polygon]:
    """
    Returns intersection of polygon with multipolygon considering cases
    with polygons touching each other in points/segments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = left_edges_count + right_edges_count``,
    ``first_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in first.polygons)``,
    ``second_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in second.polygons)``,
    ``intersections_count`` --- number of intersections between multipolygons
    edges.

    :param polygon: first operand.
    :param multipolygon: second operand.
    :param context: geometric context
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
    ...      Multipolygon([Polygon(first_square, [first_inner_square]),
    ...                    Polygon(third_square, [third_inner_square])]))
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
    ...                    Polygon(second_square, [])]))
    ...  == Mix(EMPTY, Segment(Point(4, 0), Point(4, 4)),
    ...         Polygon(first_inner_square, [])))
    True
    >>> (complete_intersect_polygon_with_multipolygon(
    ...      Polygon(first_square, []),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Mix(Multipoint([Point(4, 4)]), EMPTY,
    ...         Polygon(first_inner_square, [])))
    True
    """
    return _holey.CompleteIntersection(
            _holey.PolygonOperand(polygon),
            _holey.MultipolygonOperand(multipolygon),
            _get_context() if context is None else context).compute()


def complete_intersect_multipolygons(first: _Multipolygon,
                                     second: _Multipolygon,
                                     *,
                                     context: _Optional[_Context] = None
                                     ) -> _Union[_Empty, _Mix, _Multipoint,
                                                 _Multipolygon, _Multisegment,
                                                 _Polygon]:
    """
    Returns intersection of multipolygons considering cases
    with polygons touching each other in points/segments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = left_edges_count + right_edges_count``,
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
    :param context: geometric context
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
    >>> (complete_intersect_multipolygons(
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(second_square, []),
    ...                    Polygon(fourth_square, [])]))
    ...  is EMPTY)
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
    ...      Multipolygon([Polygon(first_square, [first_inner_square]),
    ...                    Polygon(third_square, [third_inner_square])]))
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
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(second_inner_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_square, [])]))
    ...  == Mix(EMPTY, Segment(Point(4, 0), Point(4, 4)),
    ...         Multipolygon([Polygon(first_inner_square, []),
    ...                       Polygon(second_inner_square, [])])))
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
    ...                    Polygon(third_square, [])]),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  == Multipolygon([Polygon(first_square, []),
    ...                   Polygon(third_square, [])]))
    True
    """
    return _holey.CompleteIntersection(
            _holey.MultipolygonOperand(first),
            _holey.MultipolygonOperand(second),
            _get_context() if context is None else context).compute()


def intersect_multipolygons(first: _Multipolygon,
                            second: _Multipolygon,
                            *,
                            context: _Optional[_Context] = None
                            ) -> _Multipolygon:
    """
    Returns intersection of multipolygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = left_edges_count + right_edges_count``,
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
    :param context: geometric context
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
    ...          Multipolygon([Polygon(first_square, [first_inner_square]),
    ...                        Polygon(third_square, [third_inner_square])]))
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
            _holey.MultipolygonOperand(first),
            _holey.MultipolygonOperand(second),
            _get_context() if context is None else context).compute()


def subtract_multipolygons(minuend: _Multipolygon,
                           subtrahend: _Multipolygon,
                           *,
                           context: _Optional[_Context] = None
                           ) -> _Multipolygon:
    """
    Returns difference of multipolygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = left_edges_count + right_edges_count``,
    ``first_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in first.polygons)``,
    ``second_edges_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in second.polygons)``,
    ``intersections_count`` --- number of intersections between multipolygons
    edges.

    :param minuend: multipolygon to subtract from.
    :param subtrahend: multipolygon to subtract.
    :param context: geometric context
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
    ...                                        Point(3, 3), Point(3, 1)])
    >>> clockwise_second_inner_square = Contour([Point(5, 1), Point(5, 3),
    ...                                         Point(7, 3), Point(7, 1)])
    >>> clockwise_third_inner_square = Contour([Point(5, 5), Point(5, 7),
    ...                                        Point(7, 7), Point(7, 5)])
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
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_square, [])]),
    ...          Multipolygon([Polygon(second_square, []),
    ...                        Polygon(fourth_square, [])]))
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
    ...          Multipolygon([Polygon(first_square, [first_inner_square]),
    ...                        Polygon(third_square, [third_inner_square])]))
    ... == Multipolygon([Polygon(first_inner_square, []),
    ...                  Polygon(third_inner_square, [])]))
    True
    >>> (subtract_multipolygons(
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
    return _holey.Difference(
            _holey.MultipolygonOperand(minuend),
            _holey.MultipolygonOperand(subtrahend),
            _get_context() if context is None else context).compute()


def symmetric_subtract_multipolygons(first: _Multipolygon,
                                     second: _Multipolygon,
                                     *,
                                     context: _Optional[_Context] = None
                                     ) -> _Multipolygon:
    """
    Returns symmetric difference of multipolygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = left_edges_count + right_edges_count``,
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
    :param context: geometric context
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
    ...                                        Point(3, 3), Point(3, 1)])
    >>> clockwise_second_inner_square = Contour([Point(5, 1), Point(5, 3),
    ...                                         Point(7, 3), Point(7, 1)])
    >>> clockwise_third_inner_square = Contour([Point(5, 5), Point(5, 7),
    ...                                        Point(7, 7), Point(7, 5)])
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
            _holey.MultipolygonOperand(first),
            _holey.MultipolygonOperand(second),
            _get_context() if context is None else context).compute()


def unite_multipolygons(first: _Multipolygon,
                        second: _Multipolygon,
                        *,
                        context: _Optional[_Context] = None) -> _Multipolygon:
    """
    Returns union of multipolygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = left_edges_count + right_edges_count``,
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
    :param context: geometric context
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
    ...          Multipolygon([Polygon(first_square, [first_inner_square]),
    ...                        Polygon(third_square, [third_inner_square])]))
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
            _holey.MultipolygonOperand(first),
            _holey.MultipolygonOperand(second),
            _get_context() if context is None else context).compute()
