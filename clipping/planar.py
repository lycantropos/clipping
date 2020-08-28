"""
Boolean operations on multisegments/multiregions/multipolygons in the plane.

Based on algorithm by F. Martinez et al.

Reference:
    https://doi.org/10.1016/j.advengsoft.2013.04.004
    http://www4.ujaen.es/~fmartin/bool_op.html

########
Glossary
########

**Point** --- pair of real numbers (called *point's coordinates*).

**Multipoint** --- possibly empty sequence of distinct points.

**Segment** (or **line segment**) --- pair of unequal points
(called *segment's endpoints*).

**Multisegment** --- possibly empty sequence of segments
such that any pair of them do not cross/overlap each other.

**Contour** --- sequence of points (called *contour's vertices*)
such that line segments formed by pairs of consecutive points
(including the last-first point pair)
do not overlap each other.

**Region** --- contour with points that lie within it.

**Multiregion** --- possibly empty sequence of regions such
that intersection of distinct regions is a discrete points set.

**Polygon** --- pair of region (called *polygon's border*)
and multiregion which lies within the border (called *polygon's holes*).

**Multipolygon** --- possibly empty sequence of non-overlapping polygons.

**Mix** --- triplet of disjoint/touching multipoint, multisegment
and multipolygon.
"""
from itertools import groupby as _groupby
from typing import List

from .core import (holeless as _holeless,
                   holey as _holey,
                   linear as _linear,
                   mixed as _mixed)
from .hints import (HolelessMix,
                    Mix,
                    Multipolygon,
                    Multiregion,
                    Multisegment,
                    Segment)


def segments_to_multisegment(segments: List[Segment],
                             *,
                             accurate: bool = True) -> Multisegment:
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: multisegment from segments.

    >>> segments_to_multisegment([])
    []
    >>> segments_to_multisegment([((0, 0), (1, 0)), ((0, 1), (1, 0))])
    [((0, 0), (1, 0)), ((0, 1), (1, 0))]
    >>> segments_to_multisegment([((0, 0), (2, 0)), ((1, 0), (3, 0))])
    [((0, 0), (1, 0)), ((1, 0), (2, 0)), ((2, 0), (3, 0))]
    """
    return sorted(segment
                  for segment, _ in _groupby(_linear.merge_segments(segments,
                                                                    accurate)))


def complete_intersect_multisegments(left: Multisegment,
                                     right: Multisegment,
                                     *,
                                     accurate: bool = True) -> Mix:
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: intersection of operands.

    >>> complete_intersect_multisegments([], [])
    ([], [], [])
    >>> complete_intersect_multisegments([((0, 0), (1, 0)), ((0, 1), (1, 0))],
    ...                                  [])
    ([], [], [])
    >>> complete_intersect_multisegments([],
    ...                                  [((0, 0), (1, 0)), ((0, 1), (1, 0))])
    ([], [], [])
    >>> complete_intersect_multisegments([((0, 0), (1, 0)), ((0, 1), (1, 0))],
    ...                                  [((0, 0), (1, 0)), ((0, 1), (1, 0))])
    ([], [((0, 0), (1, 0)), ((0, 1), (1, 0))], [])
    >>> complete_intersect_multisegments([((0, 0), (1, 0)), ((0, 1), (1, 1))],
    ...                                  [((0, 0), (2, 0)), ((0, 0), (2, 2))])
    ([(1, 1)], [((0, 0), (1, 0))], [])
    """
    return _linear.CompleteIntersection(left, right, accurate).compute()


def intersect_multisegments(left: Multisegment,
                            right: Multisegment,
                            *,
                            accurate: bool = True) -> Multisegment:
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: intersection of operands.

    >>> intersect_multisegments([], [])
    []
    >>> intersect_multisegments([((0, 0), (1, 0)), ((0, 1), (1, 0))], [])
    []
    >>> intersect_multisegments([], [((0, 0), (1, 0)), ((0, 1), (1, 0))])
    []
    >>> intersect_multisegments([((0, 0), (1, 0)), ((0, 1), (1, 0))],
    ...                         [((0, 0), (1, 0)), ((0, 1), (1, 0))])
    [((0, 0), (1, 0)), ((0, 1), (1, 0))]
    >>> intersect_multisegments([((0, 0), (1, 0)), ((0, 1), (1, 1))],
    ...                         [((0, 0), (2, 0)), ((0, 0), (2, 2))])
    [((0, 0), (1, 0))]
    """
    return _linear.Intersection(left, right, accurate).compute()


def subtract_multisegments(minuend: Multisegment,
                           subtrahend: Multisegment,
                           *,
                           accurate: bool = True) -> Multisegment:
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: difference between minuend and subtrahend.

    >>> subtract_multisegments([], [])
    []
    >>> subtract_multisegments([((0, 0), (1, 0)), ((0, 1), (1, 0))], [])
    [((0, 0), (1, 0)), ((0, 1), (1, 0))]
    >>> subtract_multisegments([], [((0, 0), (1, 0)), ((0, 1), (1, 0))])
    []
    >>> subtract_multisegments([((0, 0), (1, 0)), ((0, 1), (1, 0))],
    ...                        [((0, 0), (1, 0)), ((0, 1), (1, 0))])
    []
    >>> subtract_multisegments([((0, 0), (1, 0)), ((0, 1), (1, 1))],
    ...                        [((0, 0), (2, 0)), ((0, 0), (2, 2))])
    [((0, 1), (1, 1))]
    """
    return _linear.Difference(minuend, subtrahend, accurate).compute()


def symmetric_subtract_multisegments(left: Multisegment,
                                     right: Multisegment,
                                     *,
                                     accurate: bool = True) -> Multisegment:
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: symmetric difference of operands.

    >>> symmetric_subtract_multisegments([], [])
    []
    >>> symmetric_subtract_multisegments([((0, 0), (1, 0)), ((0, 1), (1, 0))],
    ...                                  [])
    [((0, 0), (1, 0)), ((0, 1), (1, 0))]
    >>> symmetric_subtract_multisegments([],
    ...                                  [((0, 0), (1, 0)), ((0, 1), (1, 0))])
    [((0, 0), (1, 0)), ((0, 1), (1, 0))]
    >>> symmetric_subtract_multisegments([((0, 0), (1, 0)), ((0, 1), (1, 0))],
    ...                                  [((0, 0), (1, 0)), ((0, 1), (1, 0))])
    []
    >>> symmetric_subtract_multisegments([((0, 0), (1, 0)), ((0, 1), (1, 1))],
    ...                                  [((0, 0), (2, 0)), ((0, 0), (2, 2))])
    [((0, 0), (1, 1)), ((0, 1), (1, 1)), ((1, 0), (2, 0)), ((1, 1), (2, 2))]
    """
    return _linear.SymmetricDifference(left, right, accurate).compute()


def unite_multisegments(left: Multisegment,
                        right: Multisegment,
                        *,
                        accurate: bool = True) -> Multisegment:
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: union of operands.

    >>> unite_multisegments([], [])
    []
    >>> unite_multisegments([((0, 0), (1, 0)), ((0, 1), (1, 0))], [])
    [((0, 0), (1, 0)), ((0, 1), (1, 0))]
    >>> unite_multisegments([], [((0, 0), (1, 0)), ((0, 1), (1, 0))])
    [((0, 0), (1, 0)), ((0, 1), (1, 0))]
    >>> unite_multisegments([((0, 0), (1, 0)), ((0, 1), (1, 0))],
    ...                     [((0, 0), (1, 0)), ((0, 1), (1, 0))])
    [((0, 0), (1, 0)), ((0, 1), (1, 0))]
    >>> unite_multisegments([((0, 0), (1, 0)), ((0, 1), (1, 1))],
    ...                     [((0, 0), (2, 0)), ((0, 0), (2, 2))])
    [((0, 0), (1, 0)), ((0, 0), (1, 1)), ((0, 1), (1, 1)), ((1, 0), (2, 0)),\
 ((1, 1), (2, 2))]
    """
    return _linear.Union(left, right, accurate).compute()


def intersect_multisegment_with_multipolygon(multisegment: Multisegment,
                                             multipolygon: Multipolygon,
                                             *,
                                             accurate: bool = True
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
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
    return _mixed.Intersection(multisegment, multipolygon, accurate).compute()


def complete_intersect_multisegment_with_multipolygon(
        multisegment: Multisegment,
        multipolygon: Multipolygon,
        *,
        accurate: bool = True) -> Mix:
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
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
                                       accurate).compute()


def subtract_multipolygon_from_multisegment(multisegment: Multisegment,
                                            multipolygon: Multipolygon,
                                            *,
                                            accurate: bool = True
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
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
    return _mixed.Difference(multisegment, multipolygon, accurate).compute()


def complete_intersect_multiregions(left: Multiregion,
                                    right: Multiregion,
                                    *,
                                    accurate: bool = True) -> HolelessMix:
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
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
    return _holeless.CompleteIntersection(left, right, accurate).compute()


def intersect_multiregions(left: Multiregion,
                           right: Multiregion,
                           *,
                           accurate: bool = True) -> Multiregion:
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
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
    return _holeless.Intersection(left, right, accurate).compute()


def complete_intersect_multipolygons(left: Multipolygon,
                                     right: Multipolygon,
                                     *,
                                     accurate: bool = True) -> Mix:
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
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
    return _holey.CompleteIntersection(left, right, accurate).compute()


def intersect_multipolygons(left: Multipolygon,
                            right: Multipolygon,
                            *,
                            accurate: bool = True) -> Multipolygon:
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
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
    return _holey.Intersection(left, right, accurate).compute()


def subtract_multipolygons(minuend: Multipolygon,
                           subtrahend: Multipolygon,
                           *,
                           accurate: bool = True) -> Multipolygon:
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
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
    return _holey.Difference(minuend, subtrahend, accurate).compute()


def symmetric_subtract_multipolygons(left: Multipolygon,
                                     right: Multipolygon,
                                     *,
                                     accurate: bool = True) -> Multipolygon:
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
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
    return _holey.SymmetricDifference(left, right, accurate).compute()


def unite_multipolygons(left: Multipolygon,
                        right: Multipolygon,
                        *,
                        accurate: bool = True) -> Multipolygon:
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
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
    return _holey.Union(left, right, accurate).compute()
