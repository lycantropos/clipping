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

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Contour, Multipolygon, Multisegment, Point, Polygon, Segment = (
    ...     context.contour_cls, context.multipolygon_cls,
    ...     context.multisegment_cls, context.point_cls, context.polygon_cls,
    ...     context.segment_cls)
    >>> intersect_multisegment_with_multipolygon(Multisegment([]),
    ...                                          Multipolygon([]))
    Multisegment([])
    >>> intersect_multisegment_with_multipolygon(
    ...     Multisegment([]),
    ...     Multipolygon([Polygon(Contour([Point(0, 0), Point(1, 0),
    ...                                    Point(0, 1)]), [])]))
    Multisegment([])
    >>> intersect_multisegment_with_multipolygon(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]),
    ...     Multipolygon([]))
    Multisegment([])
    >>> intersect_multisegment_with_multipolygon(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]),
    ...     Multipolygon([Polygon(Contour([Point(0, 0), Point(1, 0),
    ...                                    Point(0, 1)]), [])]))
    Multisegment([Segment(Point(0, 0), Point(1, 0)),\
 Segment(Point(0, 1), Point(1, 0))])
    >>> intersect_multisegment_with_multipolygon(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(1, 1), Point(2, 2))]),
    ...     Multipolygon([Polygon(Contour([Point(0, 0), Point(1, 0),
    ...                                    Point(1, 1), Point(0, 1)]), [])]))
    Multisegment([Segment(Point(0, 0), Point(1, 0))])
    """
    context = get_context()
    return _raw.to_multisegment(
            _mixed.Intersection(_raw.from_multisegment(multisegment),
                                _raw.from_multipolygon(multipolygon),
                                context=context).compute(),
            context=context)


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

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Contour, Multipolygon, Multisegment, Point, Polygon, Segment = (
    ...     context.contour_cls, context.multipolygon_cls,
    ...     context.multisegment_cls, context.point_cls, context.polygon_cls,
    ...     context.segment_cls)
    >>> complete_intersect_multisegment_with_multipolygon(Multisegment([]),
    ...                                                   Multipolygon([]))
    (Multipoint([]), Multisegment([]), Multipolygon([]))
    >>> complete_intersect_multisegment_with_multipolygon(
    ...     Multisegment([]),
    ...     Multipolygon([Polygon(Contour([Point(0, 0), Point(1, 0),
    ...                                    Point(0, 1)]), [])]))
    (Multipoint([]), Multisegment([]), Multipolygon([]))
    >>> complete_intersect_multisegment_with_multipolygon(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]),
    ...     Multipolygon([]))
    (Multipoint([]), Multisegment([]), Multipolygon([]))
    >>> complete_intersect_multisegment_with_multipolygon(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]),
    ...     Multipolygon([Polygon(Contour([Point(0, 0), Point(1, 0),
    ...                                    Point(0, 1)]), [])]))
    (Multipoint([]), Multisegment([Segment(Point(0, 0), Point(1, 0)),\
 Segment(Point(0, 1), Point(1, 0))]), Multipolygon([]))
    >>> complete_intersect_multisegment_with_multipolygon(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(1, 1), Point(2, 2))]),
    ...     Multipolygon([Polygon(Contour([Point(0, 0), Point(1, 0),
    ...                                    Point(1, 1), Point(0, 1)]), [])]))
    (Multipoint([Point(1, 1)]),\
 Multisegment([Segment(Point(0, 0), Point(1, 0))]), Multipolygon([]))
    """
    context = get_context()
    return _raw.to_mix(
            _mixed.CompleteIntersection(_raw.from_multisegment(multisegment),
                                        _raw.from_multipolygon(multipolygon),
                                        context=context).compute(),
            context=context)


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

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Contour, Multipolygon, Multisegment, Point, Polygon, Segment = (
    ...     context.contour_cls, context.multipolygon_cls,
    ...     context.multisegment_cls, context.point_cls, context.polygon_cls,
    ...     context.segment_cls)
    >>> subtract_multipolygon_from_multisegment(Multisegment([]),
    ...                                         Multipolygon([]))
    Multisegment([])
    >>> subtract_multipolygon_from_multisegment(
    ...     Multisegment([]),
    ...     Multipolygon([Polygon(Contour([Point(0, 0), Point(1, 0),
    ...                                    Point(0, 1)]), [])]))
    Multisegment([])
    >>> subtract_multipolygon_from_multisegment(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]),
    ...     Multipolygon([]))
    Multisegment([Segment(Point(0, 0), Point(1, 0)),\
 Segment(Point(0, 1), Point(1, 0))])
    >>> subtract_multipolygon_from_multisegment(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(0, 1), Point(1, 0))]),
    ...     Multipolygon([Polygon(Contour([Point(0, 0), Point(1, 0),
    ...                                    Point(0, 1)]), [])]))
    Multisegment([])
    >>> subtract_multipolygon_from_multisegment(
    ...     Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                   Segment(Point(1, 1), Point(2, 2))]),
    ...     Multipolygon([Polygon(Contour([Point(0, 0), Point(1, 0),
    ...                                    Point(1, 1), Point(0, 1)]), [])]))
    Multisegment([Segment(Point(1, 1), Point(2, 2))])
    """
    context = get_context()
    return _raw.to_multisegment(
            _mixed.Difference(_raw.from_multisegment(multisegment),
                              _raw.from_multipolygon(multipolygon),
                              context=context).compute(),
            context=context)


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

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Contour, Point = context.contour_cls, context.point_cls
    >>> lower_left_square = Contour([Point(0, 0), Point(1, 0), Point(1, 1),
    ...                              Point(0, 1)])
    >>> lower_right_square = Contour([Point(1, 0), Point(2, 0), Point(2, 1),
    ...                               Point(1, 1)])
    >>> upper_left_square = Contour([Point(0, 1), Point(1, 1), Point(1, 2),
    ...                              Point(0, 2)])
    >>> upper_right_square = Contour([Point(1, 1), Point(2, 1), Point(2, 2),
    ...                               Point(1, 2)])
    >>> complete_intersect_multiregions([], [])
    (Multipoint([]), Multisegment([]), [])
    >>> complete_intersect_multiregions([lower_left_square], [])
    (Multipoint([]), Multisegment([]), [])
    >>> complete_intersect_multiregions([], [lower_left_square])
    (Multipoint([]), Multisegment([]), [])
    >>> complete_intersect_multiregions([lower_left_square],
    ...                                 [lower_left_square])
    (Multipoint([]), Multisegment([]),\
 [Contour([Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)])])
    >>> complete_intersect_multiregions([lower_left_square],
    ...                                 [lower_right_square])
    (Multipoint([]), Multisegment([Segment(Point(1, 0), Point(1, 1))]), [])
    >>> complete_intersect_multiregions([lower_left_square],
    ...                                 [upper_left_square])
    (Multipoint([]), Multisegment([Segment(Point(0, 1), Point(1, 1))]), [])
    >>> complete_intersect_multiregions([lower_left_square],
    ...                                 [upper_right_square])
    (Multipoint([Point(1, 1)]), Multisegment([]), [])
    >>> complete_intersect_multiregions([lower_left_square,
    ...                                  upper_right_square],
    ...                                 [upper_left_square,
    ...                                  lower_right_square])
    (Multipoint([]),\
 Multisegment([Segment(Point(0, 1), Point(1, 1)),\
 Segment(Point(1, 0), Point(1, 1)), Segment(Point(1, 1), Point(2, 1)),\
 Segment(Point(1, 1), Point(1, 2))]), [])
    >>> complete_intersect_multiregions([lower_left_square,
    ...                                  upper_right_square],
    ...                                 [lower_left_square,
    ...                                  upper_right_square])
    (Multipoint([]), Multisegment([]),\
 [Contour([Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]),\
 Contour([Point(1, 1), Point(2, 1), Point(2, 2), Point(1, 2)])])
    """
    context = get_context()
    return _raw.to_holeless_mix(
            _holeless.CompleteIntersection(_raw.from_multiregion(left),
                                           _raw.from_multiregion(right),
                                           context=context).compute(),
            context=context)


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

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Contour, Point = context.contour_cls, context.point_cls
    >>> lower_left_square = Contour([Point(0, 0), Point(1, 0), Point(1, 1),
    ...                              Point(0, 1)])
    >>> lower_right_square = Contour([Point(1, 0), Point(2, 0), Point(2, 1),
    ...                               Point(1, 1)])
    >>> upper_left_square = Contour([Point(0, 1), Point(1, 1), Point(1, 2),
    ...                              Point(0, 2)])
    >>> upper_right_square = Contour([Point(1, 1), Point(2, 1), Point(2, 2),
    ...                               Point(1, 2)])
    >>> intersect_multiregions([], [])
    []
    >>> intersect_multiregions([lower_left_square], [])
    []
    >>> intersect_multiregions([], [lower_left_square])
    []
    >>> intersect_multiregions([lower_left_square], [lower_left_square])
    [Contour([Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)])]
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
    [Contour([Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]),\
 Contour([Point(1, 1), Point(2, 1), Point(2, 2), Point(1, 2)])]
    """
    return _raw.to_multiregion(
            _holeless.Intersection(_raw.from_multiregion(left),
                                   _raw.from_multiregion(right),
                                   context=get_context()).compute(),
            context=get_context())


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

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Contour, Multipolygon, Point, Polygon = (context.contour_cls,
    ...                                          context.multipolygon_cls,
    ...                                          context.point_cls,
    ...                                          context.polygon_cls)
    >>> lower_left_square = Contour([Point(0, 0), Point(3, 0), Point(3, 3),
    ...                              Point(0, 3)])
    >>> lower_left_triangle = Contour([Point(2, 1), Point(2, 2), Point(1, 2)])
    >>> lower_right_square = Contour([Point(3, 0), Point(6, 0), Point(6, 3),
    ...                               Point(3, 3)])
    >>> lower_right_triangle = Contour([Point(4, 1), Point(5, 2), Point(4, 2)])
    >>> upper_left_square = Contour([Point(0, 3), Point(3, 3), Point(3, 6),
    ...                              Point(0, 6)])
    >>> upper_left_triangle = Contour([Point(1, 4), Point(2, 4), Point(2, 5)])
    >>> upper_right_square = Contour([Point(3, 3), Point(6, 3), Point(6, 6),
    ...                               Point(3, 6)])
    >>> upper_right_triangle = Contour([Point(4, 4), Point(5, 4), Point(4, 5)])
    >>> complete_intersect_multipolygons(Multipolygon([]), Multipolygon([]))
    (Multipoint([]), Multisegment([]), Multipolygon([]))
    >>> complete_intersect_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]),
    ...     Multipolygon([]))
    (Multipoint([]), Multisegment([]), Multipolygon([]))
    >>> complete_intersect_multipolygons(
    ...     Multipolygon([]),
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]))
    (Multipoint([]), Multisegment([]), Multipolygon([]))
    >>> complete_intersect_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]),
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]))
    (Multipoint([]), Multisegment([]),\
 Multipolygon([Polygon(Contour([Point(0, 0), Point(3, 0), Point(3, 3),\
 Point(0, 3)]), [Contour([Point(2, 2), Point(2, 1), Point(1, 2)])])]))
    >>> complete_intersect_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]),
    ...     Multipolygon([Polygon(lower_right_square,
    ...                           [lower_right_triangle])]))
    (Multipoint([]), Multisegment([Segment(Point(3, 0), Point(3, 3))]),\
 Multipolygon([]))
    >>> complete_intersect_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]),
    ...     Multipolygon([Polygon(upper_left_square, [upper_left_triangle])]))
    (Multipoint([]), Multisegment([Segment(Point(0, 3), Point(3, 3))]),\
 Multipolygon([]))
    >>> complete_intersect_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]),
    ...     Multipolygon([Polygon(upper_right_square,
    ...                           [upper_right_triangle])]))
    (Multipoint([Point(3, 3)]), Multisegment([]), Multipolygon([]))
    >>> complete_intersect_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle]),
    ...                   Polygon(upper_right_square,
    ...                           [upper_right_triangle])]),
    ...     Multipolygon([Polygon(upper_left_square, [upper_left_triangle]),
    ...                   Polygon(lower_right_square,
    ...                           [lower_right_triangle])]))
    (Multipoint([]), Multisegment([Segment(Point(0, 3), Point(3, 3)),\
 Segment(Point(3, 0), Point(3, 3)), Segment(Point(3, 3), Point(6, 3)),\
 Segment(Point(3, 3), Point(3, 6))]), Multipolygon([]))
    >>> complete_intersect_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle]),
    ...                   Polygon(upper_right_square,
    ...                           [upper_right_triangle])]),
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle]),
    ...                   Polygon(upper_right_square,
    ...                           [upper_right_triangle])]))
    (Multipoint([]), Multisegment([]),\
 Multipolygon([Polygon(Contour([Point(0, 0), Point(3, 0), Point(3, 3),\
 Point(0, 3)]), [Contour([Point(2, 2), Point(2, 1), Point(1, 2)])]),\
 Polygon(Contour([Point(3, 3), Point(6, 3), Point(6, 6), Point(3, 6)]),\
 [Contour([Point(4, 5), Point(5, 4), Point(4, 4)])])]))
    """
    context = get_context()
    return _raw.to_mix(
            _holey.CompleteIntersection(_raw.from_multipolygon(left),
                                        _raw.from_multipolygon(right),
                                        context=context).compute(),
            context=context)


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

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Contour, Multipolygon, Point, Polygon = (context.contour_cls,
    ...                                          context.multipolygon_cls,
    ...                                          context.point_cls,
    ...                                          context.polygon_cls)
    >>> lower_left_square = Contour([Point(0, 0), Point(3, 0), Point(3, 3),
    ...                              Point(0, 3)])
    >>> lower_left_triangle = Contour([Point(2, 1), Point(2, 2), Point(1, 2)])
    >>> lower_right_square = Contour([Point(3, 0), Point(6, 0), Point(6, 3),
    ...                               Point(3, 3)])
    >>> lower_right_triangle = Contour([Point(4, 1), Point(5, 2), Point(4, 2)])
    >>> upper_left_square = Contour([Point(0, 3), Point(3, 3), Point(3, 6),
    ...                              Point(0, 6)])
    >>> upper_left_triangle = Contour([Point(1, 4), Point(2, 4), Point(2, 5)])
    >>> upper_right_square = Contour([Point(3, 3), Point(6, 3), Point(6, 6),
    ...                               Point(3, 6)])
    >>> upper_right_triangle = Contour([Point(4, 4), Point(5, 4), Point(4, 5)])
    >>> intersect_multipolygons(Multipolygon([]), Multipolygon([]))
    Multipolygon([])
    >>> intersect_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]),
    ...     Multipolygon([]))
    Multipolygon([])
    >>> intersect_multipolygons(
    ...     Multipolygon([]),
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]))
    Multipolygon([])
    >>> intersect_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]),
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]))
    Multipolygon([Polygon(Contour([Point(0, 0), Point(3, 0), Point(3, 3),\
 Point(0, 3)]), [Contour([Point(2, 2), Point(2, 1), Point(1, 2)])])])
    >>> intersect_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]),
    ...     Multipolygon([Polygon(lower_right_square,
    ...                           [lower_right_triangle])]))
    Multipolygon([])
    >>> intersect_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]),
    ...     Multipolygon([Polygon(upper_left_square, [upper_left_triangle])]))
    Multipolygon([])
    >>> intersect_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]),
    ...     Multipolygon([Polygon(upper_right_square,
    ...                           [upper_right_triangle])]))
    Multipolygon([])
    >>> intersect_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle]),
    ...                   Polygon(upper_right_square,
    ...                           [upper_right_triangle])]),
    ...     Multipolygon([Polygon(upper_left_square, [upper_left_triangle]),
    ...                   Polygon(lower_right_square,
    ...                           [lower_right_triangle])]))
    Multipolygon([])
    >>> intersect_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle]),
    ...                   Polygon(upper_right_square,
    ...                           [upper_right_triangle])]),
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle]),
    ...                   Polygon(upper_right_square,
    ...                           [upper_right_triangle])]))
    Multipolygon([Polygon(Contour([Point(0, 0), Point(3, 0), Point(3, 3),\
 Point(0, 3)]), [Contour([Point(2, 2), Point(2, 1), Point(1, 2)])]),\
 Polygon(Contour([Point(3, 3), Point(6, 3), Point(6, 6), Point(3, 6)]),\
 [Contour([Point(4, 5), Point(5, 4), Point(4, 4)])])])
    """
    context = get_context()
    return _raw.to_multipolygon(
            _holey.Intersection(_raw.from_multipolygon(left),
                                _raw.from_multipolygon(right),
                                context=context).compute(),
            context=context)


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

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Contour, Multipolygon, Point, Polygon = (context.contour_cls,
    ...                                          context.multipolygon_cls,
    ...                                          context.point_cls,
    ...                                          context.polygon_cls)
    >>> lower_left_square = Contour([Point(0, 0), Point(3, 0), Point(3, 3),
    ...                              Point(0, 3)])
    >>> lower_left_triangle = Contour([Point(2, 1), Point(2, 2), Point(1, 2)])
    >>> lower_right_square = Contour([Point(3, 0), Point(6, 0), Point(6, 3),
    ...                               Point(3, 3)])
    >>> lower_right_triangle = Contour([Point(4, 1), Point(5, 2), Point(4, 2)])
    >>> upper_left_square = Contour([Point(0, 3), Point(3, 3), Point(3, 6),
    ...                              Point(0, 6)])
    >>> upper_left_triangle = Contour([Point(1, 4), Point(2, 4), Point(2, 5)])
    >>> upper_right_square = Contour([Point(3, 3), Point(6, 3), Point(6, 6),
    ...                               Point(3, 6)])
    >>> upper_right_triangle = Contour([Point(4, 4), Point(5, 4), Point(4, 5)])
    >>> subtract_multipolygons(Multipolygon([]), Multipolygon([]))
    Multipolygon([])
    >>> subtract_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]),
    ...     Multipolygon([]))
    Multipolygon([Polygon(Contour([Point(0, 0), Point(3, 0), Point(3, 3),\
 Point(0, 3)]), [Contour([Point(2, 1), Point(2, 2), Point(1, 2)])])])
    >>> subtract_multipolygons(
    ...     Multipolygon([]),
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]))
    Multipolygon([])
    >>> subtract_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]),
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]))
    Multipolygon([])
    >>> subtract_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]),
    ...     Multipolygon([Polygon(lower_right_square,
    ...                           [lower_right_triangle])]))
    Multipolygon([Polygon(Contour([Point(0, 0), Point(3, 0), Point(3, 3),\
 Point(0, 3)]), [Contour([Point(2, 2), Point(2, 1), Point(1, 2)])])])
    >>> subtract_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]),
    ...     Multipolygon([Polygon(upper_left_square, [upper_left_triangle])]))
    Multipolygon([Polygon(Contour([Point(0, 0), Point(3, 0), Point(3, 3),\
 Point(0, 3)]), [Contour([Point(2, 2), Point(2, 1), Point(1, 2)])])])
    >>> subtract_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle])]),
    ...     Multipolygon([Polygon(upper_right_square,
    ...                           [upper_right_triangle])]))
    Multipolygon([Polygon(Contour([Point(0, 0), Point(3, 0), Point(3, 3),\
 Point(0, 3)]), [Contour([Point(2, 1), Point(2, 2), Point(1, 2)])])])
    >>> subtract_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle]),
    ...                   Polygon(upper_right_square,
    ...                           [upper_right_triangle])]),
    ...     Multipolygon([Polygon(upper_left_square, [upper_left_triangle]),
    ...                   Polygon(lower_right_square,
    ...                           [lower_right_triangle])]))
    Multipolygon([Polygon(Contour([Point(0, 0), Point(3, 0), Point(3, 3),\
 Point(0, 3)]), [Contour([Point(2, 2), Point(2, 1), Point(1, 2)])]),\
 Polygon(Contour([Point(3, 3), Point(6, 3), Point(6, 6), Point(3, 6)]),\
 [Contour([Point(4, 5), Point(5, 4), Point(4, 4)])])])
    >>> subtract_multipolygons(
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle]),
    ...                   Polygon(upper_right_square,
    ...                           [upper_right_triangle])]),
    ...     Multipolygon([Polygon(lower_left_square, [lower_left_triangle]),
    ...                   Polygon(upper_right_square,
    ...                           [upper_right_triangle])]))
    Multipolygon([])
    """
    context = get_context()
    return _raw.to_multipolygon(
            _holey.Difference(_raw.from_multipolygon(minuend),
                              _raw.from_multipolygon(subtrahend),
                              context=context).compute(),
            context=context)


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
