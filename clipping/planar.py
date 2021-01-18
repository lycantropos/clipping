"""
Boolean operations on multisegments/multiregions/multipolygons in the plane.

Based on algorithm by F. Martinez et al.

Reference:
    https://doi.org/10.1016/j.advengsoft.2013.04.004
    http://www4.ujaen.es/~fmartin/bool_op.html

########
Glossary
########

**Region** --- contour with points that lie within it.

**Multiregion** --- possibly empty sequence of regions such
that intersection of distinct regions is a discrete points set.

**Mix** --- triplet of disjoint/touching multipoint, multisegment
and multipolygon.

**Holeless mix** --- triplet of disjoint/touching multipoint, multisegment
and multiregion.
"""
from itertools import groupby as _groupby
from typing import Sequence

from ground.base import get_context
from ground.hints import (Multipolygon,
                          Multisegment,
                          Segment)

from .core import (holeless as _holeless,
                   holey as _holey,
                   linear as _linear,
                   mixed as _mixed,
                   raw as _raw)
from .hints import (HolelessMix,
                    Mix,
                    Multiregion)


def segments_to_multisegment(segments: Sequence[Segment]) -> Multisegment:
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
    :returns: multisegment from segments.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Point, Segment = context.point_cls, context.segment_cls
    >>> segments_to_multisegment([])
    Multisegment([])
    >>> segments_to_multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                           Segment(Point(0, 1), Point(1, 0))])
    Multisegment([Segment(Point(0, 0), Point(1, 0)), Segment(Point(0, 1),\
 Point(1, 0))])
    >>> segments_to_multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                           Segment(Point(1, 0), Point(3, 0))])
    Multisegment([Segment(Point(0, 0), Point(1, 0)),\
 Segment(Point(1, 0), Point(2, 0)), Segment(Point(2, 0), Point(3, 0))])
    """
    context = get_context()
    return _raw.to_multisegment(
            sorted(segment
                   for segment, _ in _groupby(_linear.merge_segments(
                    _raw.from_segments(segments),
                    context=context))),
            context=context)


def complete_intersect_multisegments(left: Multisegment,
                                     right: Multisegment) -> Mix:
    """
    Returns intersection of multisegments considering cases
    with segments touching each other in points.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = segments_count + intersections_count``,
    ``segments_count = len(left) + len(right)``,
    ``intersections_count`` --- number of intersections between multisegments.

    :param left: left operand.
    :param right: right operand.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Multisegment, Point, Segment = (context.multisegment_cls,
    ...                                 context.point_cls, context.segment_cls)
    >>> complete_intersect_multisegments(Multisegment([]), Multisegment([]))
    (Multipoint([]), Multisegment([]), Multipolygon([]))
    >>> complete_intersect_multisegments(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]),
    ...     Multisegment([]))
    (Multipoint([]), Multisegment([]), Multipolygon([]))
    >>> complete_intersect_multisegments(
    ...     Multisegment([]),
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    (Multipoint([]), Multisegment([]), Multipolygon([]))
    >>> complete_intersect_multisegments(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]),
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    (Multipoint([]), Multisegment([Segment(Point(0, 0), Point(1, 0)),\
 Segment(Point(0, 1), Point(1, 0))]), Multipolygon([]))
    >>> complete_intersect_multisegments(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 1))]),
    ...     Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                   Segment(Point(0, 0), Point(2, 2))]))
    (Multipoint([Point(1, 1)]),\
 Multisegment([Segment(Point(0, 0), Point(1, 0))]), Multipolygon([]))
    """
    context = get_context()
    return _raw.to_mix(
            _linear.CompleteIntersection(_raw.from_multisegment(left),
                                         _raw.from_multisegment(right),
                                         context=context).compute(),
            context=context)


def intersect_multisegments(left: Multisegment,
                            right: Multisegment) -> Multisegment:
    """
    Returns intersection of multisegments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = segments_count + intersections_count``,
    ``segments_count = len(left) + len(right)``,
    ``intersections_count`` --- number of intersections between multisegments.

    :param left: left operand.
    :param right: right operand.
    :returns: intersection of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Multisegment, Point, Segment = (context.multisegment_cls,
    ...                                 context.point_cls, context.segment_cls)
    >>> intersect_multisegments(Multisegment([]), Multisegment([]))
    Multisegment([])
    >>> intersect_multisegments(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]),
    ...     Multisegment([]))
    Multisegment([])
    >>> intersect_multisegments(
    ...     Multisegment([]),
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    Multisegment([])
    >>> intersect_multisegments(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]),
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    Multisegment([Segment(Point(0, 0), Point(1, 0)),\
 Segment(Point(0, 1), Point(1, 0))])
    >>> intersect_multisegments(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 1))]),
    ...     Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                   Segment(Point(0, 0), Point(2, 2))]))
    Multisegment([Segment(Point(0, 0), Point(1, 0))])
    """
    context = get_context()
    return _raw.to_multisegment(
            _linear.Intersection(_raw.from_multisegment(left),
                                 _raw.from_multisegment(right),
                                 context=context).compute(),
            context=context)


def subtract_multisegments(minuend: Multisegment,
                           subtrahend: Multisegment) -> Multisegment:
    """
    Returns difference of multisegments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = segments_count + intersections_count``,
    ``segments_count = len(left) + len(right)``,
    ``intersections_count`` --- number of intersections between multisegments.

    :param minuend: multisegment to subtract from.
    :param subtrahend: multisegment to subtract.
    :returns: difference between minuend and subtrahend.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Multisegment, Point, Segment = (context.multisegment_cls,
    ...                                 context.point_cls, context.segment_cls)
    >>> subtract_multisegments(Multisegment([]), Multisegment([]))
    Multisegment([])
    >>> subtract_multisegments(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]),
    ...     Multisegment([]))
    Multisegment([Segment(Point(0, 0), Point(1, 0)),\
 Segment(Point(0, 1), Point(1, 0))])
    >>> subtract_multisegments(
    ...     Multisegment([]),
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    Multisegment([])
    >>> subtract_multisegments(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]),
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    Multisegment([])
    >>> subtract_multisegments(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 1))]),
    ...     Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                   Segment(Point(0, 0), Point(2, 2))]))
    Multisegment([Segment(Point(0, 1), Point(1, 1))])
    """
    context = get_context()
    return _raw.to_multisegment(
            _linear.Difference(_raw.from_multisegment(minuend),
                               _raw.from_multisegment(subtrahend),
                               context=context).compute(),
            context=context)


def symmetric_subtract_multisegments(left: Multisegment,
                                     right: Multisegment) -> Multisegment:
    """
    Returns symmetric difference of multisegments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = segments_count + intersections_count``,
    ``segments_count = len(left) + len(right)``,
    ``intersections_count`` --- number of intersections between multisegments.

    :param left: left operand.
    :param right: right operand.
    :returns: symmetric difference of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Multisegment, Point, Segment = (context.multisegment_cls,
    ...                                 context.point_cls, context.segment_cls)
    >>> symmetric_subtract_multisegments(Multisegment([]), Multisegment([]))
    Multisegment([])
    >>> symmetric_subtract_multisegments(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]),
    ...     Multisegment([]))
    Multisegment([Segment(Point(0, 0), Point(1, 0)),\
 Segment(Point(0, 1), Point(1, 0))])
    >>> symmetric_subtract_multisegments(
    ...     Multisegment([]),
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    Multisegment([Segment(Point(0, 0), Point(1, 0)),\
 Segment(Point(0, 1), Point(1, 0))])
    >>> symmetric_subtract_multisegments(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]),
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]))
    Multisegment([])
    >>> symmetric_subtract_multisegments(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 1))]),
    ...     Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                   Segment(Point(0, 0), Point(2, 2))]))
    Multisegment([Segment(Point(0, 0), Point(1, 1)),\
 Segment(Point(0, 1), Point(1, 1)), Segment(Point(1, 0), Point(2, 0)),\
 Segment(Point(1, 1), Point(2, 2))])
    """
    context = get_context()
    return _raw.to_multisegment(
            _linear.SymmetricDifference(_raw.from_multisegment(left),
                                        _raw.from_multisegment(right),
                                        context=context).compute(),
            context=context)


def unite_multisegments(left: Multisegment,
                        right: Multisegment) -> Multisegment:
    """
    Returns union of multisegments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = segments_count + intersections_count``,
    ``segments_count = len(left) + len(right)``,
    ``intersections_count`` --- number of intersections between multisegments.

    :param left: left operand.
    :param right: right operand.
    :returns: union of operands.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Multisegment, Point, Segment = (context.multisegment_cls,
    ...                                 context.point_cls, context.segment_cls)
    >>> unite_multisegments(Multisegment([]), Multisegment([]))
    Multisegment([])
    >>> unite_multisegments(Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                                   Segment(Point(0, 1), Point(1, 0))]),
    ...                     Multisegment([]))
    Multisegment([Segment(Point(0, 0), Point(1, 0)),\
 Segment(Point(0, 1), Point(1, 0))])
    >>> unite_multisegments(Multisegment([]),
    ...                     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                                   Segment(Point(0, 1), Point(1, 0))]))
    Multisegment([Segment(Point(0, 0), Point(1, 0)),\
 Segment(Point(0, 1), Point(1, 0))])
    >>> unite_multisegments(Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                                   Segment(Point(0, 1), Point(1, 0))]),
    ...                     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                                   Segment(Point(0, 1), Point(1, 0))]))
    Multisegment([Segment(Point(0, 0), Point(1, 0)),\
 Segment(Point(0, 1), Point(1, 0))])
    >>> unite_multisegments(Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                                   Segment(Point(0, 1), Point(1, 1))]),
    ...                     Multisegment([Segment(Point(0, 0), Point(2, 0)),
    ...                                   Segment(Point(0, 0), Point(2, 2))]))
    Multisegment([Segment(Point(0, 0), Point(1, 0)),\
 Segment(Point(0, 0), Point(1, 1)), Segment(Point(0, 1), Point(1, 1)),\
 Segment(Point(1, 0), Point(2, 0)), Segment(Point(1, 1), Point(2, 2))])
    """
    context = get_context()
    return _raw.to_multisegment(_linear.Union(_raw.from_multisegment(left),
                                              _raw.from_multisegment(right),
                                              context=context).compute(),
                                context=context)


def intersect_multisegment_with_multipolygon(multisegment: Multisegment,
                                             multipolygon: Multipolygon
                                             ) -> Multisegment:
    """
    Returns intersection of multisegment with multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = len(multisegment) + multipolygon_edges_count``,
    ``multipolygon_edges_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in multipolygon)``,
    ``intersections_count`` --- number of intersections between multisegment
    and multipolygon edges.

    :param multisegment: multisegment to intersect with.
    :param multipolygon: multipolygon to intersect with.
    :returns: intersection of multisegment with multipolygon.

    >>> intersect_multisegment_with_multipolygon([], [])
    []
    >>> intersect_multisegment_with_multipolygon(
    ...         [], [([(0, 0), (1, 0), (0, 1)], [])])
    []
    >>> intersect_multisegment_with_multipolygon(
    ...         [((0, 0), (1, 0)), ((0, 1), (1, 0))], [])
    []
    >>> intersect_multisegment_with_multipolygon(
    ...         [((0, 0), (1, 0)), ((0, 1), (1, 0))],
    ...         [([(0, 0), (1, 0), (0, 1)], [])])
    [((0, 0), (1, 0)), ((0, 1), (1, 0))]
    >>> intersect_multisegment_with_multipolygon(
    ...         [((0, 0), (1, 0)), ((1, 1), (2, 2))],
    ...         [([(0, 0), (1, 0), (1, 1), (0, 1)], [])])
    [((0, 0), (1, 0))]
    """
    return _mixed.Intersection(multisegment, multipolygon,
                               context=get_context()).compute()


def complete_intersect_multisegment_with_multipolygon(
        multisegment: Multisegment,
        multipolygon: Multipolygon) -> Mix:
    """
    Returns intersection of multisegment with multipolygon considering cases
    with geometries touching each other in points/segments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = len(multisegment) + multipolygon_edges_count``,
    ``multipolygon_edges_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in multipolygon)``,
    ``intersections_count`` --- number of intersections between multisegment
    and multipolygon edges.

    :param multisegment: multisegment to intersect with.
    :param multipolygon: multipolygon to intersect with.
    :returns: intersection of multisegment with multipolygon.

    >>> complete_intersect_multisegment_with_multipolygon([], [])
    ([], [], [])
    >>> complete_intersect_multisegment_with_multipolygon(
    ...         [], [([(0, 0), (1, 0), (0, 1)], [])])
    ([], [], [])
    >>> complete_intersect_multisegment_with_multipolygon(
    ...         [((0, 0), (1, 0)), ((0, 1), (1, 0))], [])
    ([], [], [])
    >>> complete_intersect_multisegment_with_multipolygon(
    ...         [((0, 0), (1, 0)), ((0, 1), (1, 0))],
    ...         [([(0, 0), (1, 0), (0, 1)], [])])
    ([], [((0, 0), (1, 0)), ((0, 1), (1, 0))], [])
    >>> complete_intersect_multisegment_with_multipolygon(
    ...         [((0, 0), (1, 0)), ((1, 1), (2, 2))],
    ...         [([(0, 0), (1, 0), (1, 1), (0, 1)], [])])
    ([(1, 1)], [((0, 0), (1, 0))], [])
    """
    return _mixed.CompleteIntersection(multisegment, multipolygon,
                                       context=get_context()).compute()


def subtract_multipolygon_from_multisegment(multisegment: Multisegment,
                                            multipolygon: Multipolygon
                                            ) -> Multisegment:
    """
    Returns difference of multisegment with multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = start_segments_count + intersections_count``,
    ``start_segments_count = len(multisegment) + multipolygon_edges_count``,
    ``multipolygon_edges_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in multipolygon)``,
    ``intersections_count`` --- number of intersections between multisegment
    and multipolygon edges.

    :param multisegment: multisegment to subtract from.
    :param multipolygon: multipolygon to subtract.
    :returns: difference of multisegment with multipolygon.

    >>> subtract_multipolygon_from_multisegment([], [])
    []
    >>> subtract_multipolygon_from_multisegment(
    ...         [], [([(0, 0), (1, 0), (0, 1)], [])])
    []
    >>> subtract_multipolygon_from_multisegment(
    ...         [((0, 0), (1, 0)), ((0, 1), (1, 0))], [])
    [((0, 0), (1, 0)), ((0, 1), (1, 0))]
    >>> subtract_multipolygon_from_multisegment(
    ...         [((0, 0), (1, 0)), ((0, 1), (1, 0))],
    ...         [([(0, 0), (1, 0), (0, 1)], [])])
    []
    >>> subtract_multipolygon_from_multisegment(
    ...         [((0, 0), (1, 0)), ((1, 1), (2, 2))],
    ...         [([(0, 0), (1, 0), (1, 1), (0, 1)], [])])
    [((1, 1), (2, 2))]
    """
    return _mixed.Difference(multisegment, multipolygon,
                             context=get_context()).compute()


def complete_intersect_multiregions(left: Multiregion,
                                    right: Multiregion) -> HolelessMix:
    """
    Returns intersection of multiregions considering cases
    with regions touching each other in points/segments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = left_edges_count + right_edges_count``,
    ``left_edges_count = sum(map(len, left))``,
    ``right_edges_count = sum(map(len, right))``,
    ``intersections_count`` --- number of intersections between multiregions
    edges.

    :param left: left operand.
    :param right: right operand.
    :returns: intersection of operands.

    >>> lower_left_square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> lower_right_square = [(1, 0), (2, 0), (2, 1), (1, 1)]
    >>> upper_left_square = [(0, 1), (1, 1), (1, 2), (0, 2)]
    >>> upper_right_square = [(1, 1), (2, 1), (2, 2), (1, 2)]
    >>> complete_intersect_multiregions([], [])
    ([], [], [])
    >>> complete_intersect_multiregions([lower_left_square], [])
    ([], [], [])
    >>> complete_intersect_multiregions([], [lower_left_square])
    ([], [], [])
    >>> complete_intersect_multiregions([lower_left_square],
    ...                                 [lower_left_square])
    ([], [], [[(0, 0), (1, 0), (1, 1), (0, 1)]])
    >>> complete_intersect_multiregions([lower_left_square],
    ...                                 [lower_right_square])
    ([], [((1, 0), (1, 1))], [])
    >>> complete_intersect_multiregions([lower_left_square],
    ...                                 [upper_left_square])
    ([], [((0, 1), (1, 1))], [])
    >>> complete_intersect_multiregions([lower_left_square],
    ...                                 [upper_right_square])
    ([(1, 1)], [], [])
    >>> complete_intersect_multiregions([lower_left_square,
    ...                                  upper_right_square],
    ...                                 [upper_left_square,
    ...                                  lower_right_square])
    ([],\
 [((0, 1), (1, 1)), ((1, 0), (1, 1)), ((1, 1), (2, 1)), ((1, 1), (1, 2))], [])
    >>> complete_intersect_multiregions([lower_left_square,
    ...                                  upper_right_square],
    ...                                 [lower_left_square,
    ...                                  upper_right_square])
    ([], [],\
 [[(0, 0), (1, 0), (1, 1), (0, 1)], [(1, 1), (2, 1), (2, 2), (1, 2)]])
    """
    return _holeless.CompleteIntersection(left, right,
                                          context=get_context()).compute()


def intersect_multiregions(left: Multiregion,
                           right: Multiregion) -> Multiregion:
    """
    Returns intersection of multiregions.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = left_edges_count + right_edges_count``,
    ``left_edges_count = sum(map(len, left))``,
    ``right_edges_count = sum(map(len, right))``,
    ``intersections_count`` --- number of intersections between multiregions
    edges.

    :param left: left operand.
    :param right: right operand.
    :returns: intersection of operands.

    >>> lower_left_square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> lower_right_square = [(1, 0), (2, 0), (2, 1), (1, 1)]
    >>> upper_left_square = [(0, 1), (1, 1), (1, 2), (0, 2)]
    >>> upper_right_square = [(1, 1), (2, 1), (2, 2), (1, 2)]
    >>> intersect_multiregions([], [])
    []
    >>> intersect_multiregions([lower_left_square], [])
    []
    >>> intersect_multiregions([], [lower_left_square])
    []
    >>> intersect_multiregions([lower_left_square], [lower_left_square])
    [[(0, 0), (1, 0), (1, 1), (0, 1)]]
    >>> intersect_multiregions([lower_left_square], [lower_right_square])
    []
    >>> intersect_multiregions([lower_left_square], [upper_left_square])
    []
    >>> intersect_multiregions([lower_left_square], [upper_right_square])
    []
    >>> intersect_multiregions([lower_left_square, upper_right_square],
    ...                        [upper_left_square, lower_right_square])
    []
    >>> intersect_multiregions([lower_left_square, upper_right_square],
    ...                        [lower_left_square, upper_right_square])
    [[(0, 0), (1, 0), (1, 1), (0, 1)], [(1, 1), (2, 1), (2, 2), (1, 2)]]
    """
    return _holeless.Intersection(left, right, context=get_context()).compute()


def complete_intersect_multipolygons(left: Multipolygon,
                                     right: Multipolygon) -> Mix:
    """
    Returns intersection of multipolygons considering cases
    with polygons touching each other in points/segments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = left_edges_count + right_edges_count``,
    ``left_edges_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in left)``,
    ``right_edges_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in right)``,
    ``intersections_count`` --- number of intersections between multipolygons
    edges.

    :param left: left operand.
    :param right: right operand.
    :returns: intersection of operands.

    >>> lower_left_square = [(0, 0), (3, 0), (3, 3), (0, 3)]
    >>> lower_left_triangle = [(2, 1), (2, 2), (1, 2)]
    >>> lower_right_square = [(3, 0), (6, 0), (6, 3), (3, 3)]
    >>> lower_right_triangle = [(4, 1), (5, 2), (4, 2)]
    >>> upper_left_square = [(0, 3), (3, 3), (3, 6), (0, 6)]
    >>> upper_left_triangle = [(1, 4), (2, 4), (2, 5)]
    >>> upper_right_square = [(3, 3), (6, 3), (6, 6), (3, 6)]
    >>> upper_right_triangle = [(4, 4), (5, 4), (4, 5)]
    >>> complete_intersect_multipolygons([], [])
    ([], [], [])
    >>> complete_intersect_multipolygons([(lower_left_square,
    ...                                    [lower_left_triangle])], [])
    ([], [], [])
    >>> complete_intersect_multipolygons([], [(lower_left_square,
    ...                                        [lower_left_triangle])])
    ([], [], [])
    >>> complete_intersect_multipolygons([(lower_left_square,
    ...                                    [lower_left_triangle])],
    ...                                  [(lower_left_square,
    ...                                    [lower_left_triangle])])
    ([], [], [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 2), (2, 1), (1, 2)]])])
    >>> complete_intersect_multipolygons([(lower_left_square,
    ...                                    [lower_left_triangle])],
    ...                                  [(lower_right_square,
    ...                                    [lower_right_triangle])])
    ([], [((3, 0), (3, 3))], [])
    >>> complete_intersect_multipolygons([(lower_left_square,
    ...                                    [lower_left_triangle])],
    ...                                  [(upper_left_square,
    ...                                    [upper_left_triangle])])
    ([], [((0, 3), (3, 3))], [])
    >>> complete_intersect_multipolygons([(lower_left_square,
    ...                                    [lower_left_triangle])],
    ...                                  [(upper_right_square,
    ...                                    [upper_right_triangle])])
    ([(3, 3)], [], [])
    >>> complete_intersect_multipolygons([(lower_left_square,
    ...                                    [lower_left_triangle]),
    ...                                   (upper_right_square,
    ...                                    [upper_right_triangle])],
    ...                                  [(upper_left_square,
    ...                                    [upper_left_triangle]),
    ...                                   (lower_right_square,
    ...                                    [lower_right_triangle])])
    ([],\
 [((0, 3), (3, 3)), ((3, 0), (3, 3)), ((3, 3), (6, 3)), ((3, 3), (3, 6))], [])
    >>> complete_intersect_multipolygons([(lower_left_square,
    ...                                    [lower_left_triangle]),
    ...                                   (upper_right_square,
    ...                                    [upper_right_triangle])],
    ...                                  [(lower_left_square,
    ...                                    [lower_left_triangle]),
    ...                                   (upper_right_square,
    ...                                    [upper_right_triangle])])
    ([], [],\
 [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 2), (2, 1), (1, 2)]]),\
 ([(3, 3), (6, 3), (6, 6), (3, 6)], [[(4, 5), (5, 4), (4, 4)]])])
    """
    return _holey.CompleteIntersection(left, right,
                                       context=get_context()).compute()


def intersect_multipolygons(left: Multipolygon,
                            right: Multipolygon) -> Multipolygon:
    """
    Returns intersection of multipolygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = left_edges_count + right_edges_count``,
    ``left_edges_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in left)``,
    ``right_edges_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in right)``,
    ``intersections_count`` --- number of intersections between multipolygons
    edges.

    :param left: left operand.
    :param right: right operand.
    :returns: intersection of operands.

    >>> lower_left_square = [(0, 0), (3, 0), (3, 3), (0, 3)]
    >>> lower_left_triangle = [(2, 1), (2, 2), (1, 2)]
    >>> lower_right_square = [(3, 0), (6, 0), (6, 3), (3, 3)]
    >>> lower_right_triangle = [(4, 1), (5, 2), (4, 2)]
    >>> upper_left_square = [(0, 3), (3, 3), (3, 6), (0, 6)]
    >>> upper_left_triangle = [(1, 4), (2, 4), (2, 5)]
    >>> upper_right_square = [(3, 3), (6, 3), (6, 6), (3, 6)]
    >>> upper_right_triangle = [(4, 4), (5, 4), (4, 5)]
    >>> intersect_multipolygons([], [])
    []
    >>> intersect_multipolygons([(lower_left_square, [lower_left_triangle])],
    ...                         [])
    []
    >>> intersect_multipolygons([], [(lower_left_square,
    ...                               [lower_left_triangle])])
    []
    >>> intersect_multipolygons([(lower_left_square, [lower_left_triangle])],
    ...                         [(lower_left_square, [lower_left_triangle])])
    [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 2), (2, 1), (1, 2)]])]
    >>> intersect_multipolygons([(lower_left_square, [lower_left_triangle])],
    ...                         [(lower_right_square, [lower_right_triangle])])
    []
    >>> intersect_multipolygons([(lower_left_square, [lower_left_triangle])],
    ...                         [(upper_left_square, [upper_left_triangle])])
    []
    >>> intersect_multipolygons([(lower_left_square, [lower_left_triangle])],
    ...                         [(upper_right_square, [upper_right_triangle])])
    []
    >>> intersect_multipolygons([(lower_left_square, [lower_left_triangle]),
    ...                          (upper_right_square, [upper_right_triangle])],
    ...                         [(upper_left_square, [upper_left_triangle]),
    ...                          (lower_right_square, [lower_right_triangle])])
    []
    >>> intersect_multipolygons([(lower_left_square, [lower_left_triangle]),
    ...                          (upper_right_square, [upper_right_triangle])],
    ...                         [(lower_left_square, [lower_left_triangle]),
    ...                          (upper_right_square, [upper_right_triangle])])
    [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 2), (2, 1), (1, 2)]]),\
 ([(3, 3), (6, 3), (6, 6), (3, 6)], [[(4, 5), (5, 4), (4, 4)]])]
    """
    return _holey.Intersection(left, right, context=get_context()).compute()


def subtract_multipolygons(minuend: Multipolygon,
                           subtrahend: Multipolygon) -> Multipolygon:
    """
    Returns difference of multipolygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = left_edges_count + right_edges_count``,
    ``left_edges_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in left)``,
    ``right_edges_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in right)``,
    ``intersections_count`` --- number of intersections between multipolygons
    edges.

    :param minuend: multipolygon to subtract from.
    :param subtrahend: multipolygon to subtract.
    :returns: difference between minuend and subtrahend.

    >>> lower_left_square = [(0, 0), (3, 0), (3, 3), (0, 3)]
    >>> lower_left_triangle = [(2, 1), (2, 2), (1, 2)]
    >>> lower_right_square = [(3, 0), (6, 0), (6, 3), (3, 3)]
    >>> lower_right_triangle = [(4, 1), (5, 2), (4, 2)]
    >>> upper_left_square = [(0, 3), (3, 3), (3, 6), (0, 6)]
    >>> upper_left_triangle = [(1, 4), (2, 4), (2, 5)]
    >>> upper_right_square = [(3, 3), (6, 3), (6, 6), (3, 6)]
    >>> upper_right_triangle = [(4, 4), (5, 4), (4, 5)]
    >>> subtract_multipolygons([], [])
    []
    >>> subtract_multipolygons([(lower_left_square, [lower_left_triangle])],
    ...                        [])
    [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 1), (2, 2), (1, 2)]])]
    >>> subtract_multipolygons([], [(lower_left_square,
    ...                              [lower_left_triangle])])
    []
    >>> subtract_multipolygons([(lower_left_square, [lower_left_triangle])],
    ...                        [(lower_left_square, [lower_left_triangle])])
    []
    >>> subtract_multipolygons([(lower_left_square, [lower_left_triangle])],
    ...                        [(lower_right_square, [lower_right_triangle])])
    [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 2), (2, 1), (1, 2)]])]
    >>> subtract_multipolygons([(lower_left_square, [lower_left_triangle])],
    ...                        [(upper_left_square, [upper_left_triangle])])
    [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 2), (2, 1), (1, 2)]])]
    >>> subtract_multipolygons([(lower_left_square, [lower_left_triangle])],
    ...                        [(upper_right_square, [upper_right_triangle])])
    [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 1), (2, 2), (1, 2)]])]
    >>> subtract_multipolygons([(lower_left_square, [lower_left_triangle]),
    ...                         (upper_right_square, [upper_right_triangle])],
    ...                        [(upper_left_square, [upper_left_triangle]),
    ...                         (lower_right_square, [lower_right_triangle])])
    [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 2), (2, 1), (1, 2)]]),\
 ([(3, 3), (6, 3), (6, 6), (3, 6)], [[(4, 5), (5, 4), (4, 4)]])]
    >>> subtract_multipolygons([(lower_left_square, [lower_left_triangle]),
    ...                         (upper_right_square, [upper_right_triangle])],
    ...                        [(lower_left_square, [lower_left_triangle]),
    ...                         (upper_right_square, [upper_right_triangle])])
    []
    """
    return _holey.Difference(minuend, subtrahend,
                             context=get_context()).compute()


def symmetric_subtract_multipolygons(left: Multipolygon,
                                     right: Multipolygon) -> Multipolygon:
    """
    Returns symmetric difference of multipolygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = left_edges_count + right_edges_count``,
    ``left_edges_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in left)``,
    ``right_edges_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in right)``,
    ``intersections_count`` --- number of intersections between multipolygons
    edges.

    :param left: left operand.
    :param right: right operand.
    :returns: symmetric difference of operands.

    >>> lower_left_square = [(0, 0), (3, 0), (3, 3), (0, 3)]
    >>> lower_left_triangle = [(2, 1), (2, 2), (1, 2)]
    >>> lower_right_square = [(3, 0), (6, 0), (6, 3), (3, 3)]
    >>> lower_right_triangle = [(4, 1), (5, 2), (4, 2)]
    >>> upper_left_square = [(0, 3), (3, 3), (3, 6), (0, 6)]
    >>> upper_left_triangle = [(1, 4), (2, 4), (2, 5)]
    >>> upper_right_square = [(3, 3), (6, 3), (6, 6), (3, 6)]
    >>> upper_right_triangle = [(4, 4), (5, 4), (4, 5)]
    >>> symmetric_subtract_multipolygons([], [])
    []
    >>> symmetric_subtract_multipolygons([(lower_left_square,
    ...                                   [lower_left_triangle])], [])
    [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 1), (2, 2), (1, 2)]])]
    >>> symmetric_subtract_multipolygons([], [(lower_left_square,
    ...                                       [lower_left_triangle])])
    [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 1), (2, 2), (1, 2)]])]
    >>> symmetric_subtract_multipolygons([(lower_left_square,
    ...                                    [lower_left_triangle])],
    ...                                  [(lower_left_square,
    ...                                    [lower_left_triangle])])
    []
    >>> symmetric_subtract_multipolygons([(lower_left_square,
    ...                                    [lower_left_triangle])],
    ...                                  [(lower_right_square,
    ...                                    [lower_right_triangle])])
    [([(0, 0), (6, 0), (6, 3), (0, 3)], [[(2, 2), (2, 1), (1, 2)],\
 [(4, 2), (5, 2), (4, 1)]])]
    >>> symmetric_subtract_multipolygons([(lower_left_square,
    ...                                    [lower_left_triangle])],
    ...                                  [(upper_left_square,
    ...                                    [upper_left_triangle])])
    [([(0, 0), (3, 0), (3, 6), (0, 6)], [[(2, 2), (2, 1), (1, 2)],\
 [(2, 5), (2, 4), (1, 4)]])]
    >>> symmetric_subtract_multipolygons([(lower_left_square,
    ...                                    [lower_left_triangle])],
    ...                                  [(upper_right_square,
    ...                                    [upper_right_triangle])])
    [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 2), (2, 1), (1, 2)]]),\
 ([(3, 3), (6, 3), (6, 6), (3, 6)], [[(4, 5), (5, 4), (4, 4)]])]
    >>> symmetric_subtract_multipolygons([(lower_left_square,
    ...                                    [lower_left_triangle]),
    ...                                   (upper_right_square,
    ...                                    [upper_right_triangle])],
    ...                                  [(upper_left_square,
    ...                                    [upper_left_triangle]),
    ...                                   (lower_right_square,
    ...                                    [lower_right_triangle])])
    [([(0, 0), (6, 0), (6, 6), (0, 6)], [[(2, 2), (2, 1), (1, 2)],\
 [(2, 5), (2, 4), (1, 4)], [(4, 2), (5, 2), (4, 1)],\
 [(4, 5), (5, 4), (4, 4)]])]
    >>> symmetric_subtract_multipolygons([(lower_left_square,
    ...                                    [lower_left_triangle]),
    ...                                   (upper_right_square,
    ...                                    [upper_right_triangle])],
    ...                                  [(lower_left_square,
    ...                                    [lower_left_triangle]),
    ...                                   (upper_right_square,
    ...                                    [upper_right_triangle])])
    []
    """
    return _holey.SymmetricDifference(left, right,
                                      context=get_context()).compute()


def unite_multipolygons(left: Multipolygon,
                        right: Multipolygon) -> Multipolygon:
    """
    Returns union of multipolygons.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = edges_count + intersections_count``,
    ``edges_count = left_edges_count + right_edges_count``,
    ``left_edges_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in left)``,
    ``right_edges_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in right)``,
    ``intersections_count`` --- number of intersections between multipolygons
    edges.

    :param left: left operand.
    :param right: right operand.
    :returns: union of operands.

    >>> lower_left_square = [(0, 0), (3, 0), (3, 3), (0, 3)]
    >>> lower_left_triangle = [(2, 1), (2, 2), (1, 2)]
    >>> lower_right_square = [(3, 0), (6, 0), (6, 3), (3, 3)]
    >>> lower_right_triangle = [(4, 1), (5, 2), (4, 2)]
    >>> upper_left_square = [(0, 3), (3, 3), (3, 6), (0, 6)]
    >>> upper_left_triangle = [(1, 4), (2, 4), (2, 5)]
    >>> upper_right_square = [(3, 3), (6, 3), (6, 6), (3, 6)]
    >>> upper_right_triangle = [(4, 4), (5, 4), (4, 5)]
    >>> unite_multipolygons([], [])
    []
    >>> unite_multipolygons([(lower_left_square, [lower_left_triangle])], [])
    [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 1), (2, 2), (1, 2)]])]
    >>> unite_multipolygons([], [(lower_left_square, [lower_left_triangle])])
    [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 1), (2, 2), (1, 2)]])]
    >>> unite_multipolygons([(lower_left_square, [lower_left_triangle])],
    ...                     [(lower_left_square, [lower_left_triangle])])
    [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 2), (2, 1), (1, 2)]])]
    >>> unite_multipolygons([(lower_left_square, [lower_left_triangle])],
    ...                     [(lower_right_square, [lower_right_triangle])])
    [([(0, 0), (6, 0), (6, 3), (0, 3)], [[(2, 2), (2, 1), (1, 2)],\
 [(4, 2), (5, 2), (4, 1)]])]
    >>> unite_multipolygons([(lower_left_square, [lower_left_triangle])],
    ...                     [(upper_left_square, [upper_left_triangle])])
    [([(0, 0), (3, 0), (3, 6), (0, 6)], [[(2, 2), (2, 1), (1, 2)],\
 [(2, 5), (2, 4), (1, 4)]])]
    >>> unite_multipolygons([(lower_left_square, [lower_left_triangle])],
    ...                     [(upper_right_square, [upper_right_triangle])])
    [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 2), (2, 1), (1, 2)]]),\
 ([(3, 3), (6, 3), (6, 6), (3, 6)], [[(4, 5), (5, 4), (4, 4)]])]
    >>> unite_multipolygons([(lower_left_square, [lower_left_triangle]),
    ...                      (upper_right_square, [upper_right_triangle])],
    ...                     [(upper_left_square, [upper_left_triangle]),
    ...                      (lower_right_square, [lower_right_triangle])])
    [([(0, 0), (6, 0), (6, 6), (0, 6)], [[(2, 2), (2, 1), (1, 2)],\
 [(2, 5), (2, 4), (1, 4)], [(4, 2), (5, 2), (4, 1)],\
 [(4, 5), (5, 4), (4, 4)]])]
    >>> unite_multipolygons([(lower_left_square, [lower_left_triangle]),
    ...                      (upper_right_square, [upper_right_triangle])],
    ...                     [(lower_left_square, [lower_left_triangle]),
    ...                      (upper_right_square, [upper_right_triangle])])
    [([(0, 0), (3, 0), (3, 3), (0, 3)], [[(2, 2), (2, 1), (1, 2)]]),\
 ([(3, 3), (6, 3), (6, 6), (3, 6)], [[(4, 5), (5, 4), (4, 4)]])]
    """
    return _holey.Union(left, right,
                        context=get_context()).compute()
