"""
Boolean operations on multisegments/polygons/multipolygons in the plane.

Based on algorithm by F. Martinez et al.

Reference:
    https://doi.org/10.1016/j.advengsoft.2013.04.004
    http://www4.ujaen.es/~fmartin/bool_op.html

########
Glossary
########

**Point** --- pair of real numbers (called *point's coordinates*).

**Segment** (or **line segment**) --- pair of unequal points
(called *segment's endpoints*).

**Contour** --- sequence of points (called *contour's vertices*)
such that line segments formed by pairs of consecutive points
(including the last-first point pair)
do not overlap each other.

**Polygon** --- pair of contour (called *polygon's border*)
and possibly empty sequence of non-overlapping contours
which lie within the border (called *polygon's holes*).

**Multipoint** --- possibly empty sequence of distinct points.

**Multisegment** --- possibly empty sequence of segments
such that any pair of them do not cross/overlap each other.

**Multipolygon** --- possibly empty sequence of non-overlapping polygons.

**Mix** --- triplet of disjoint/touching multipoint, multisegment
and multipolygon.
"""

from .core import (linear as _linear,
                   mixed as _mixed,
                   shaped as _shaped)
from .hints import (Mix,
                    Multipolygon,
                    Multisegment)


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
                                             accurate: bool = True) -> Mix:
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
    ([], [], [])
    >>> intersect_multisegment_with_multipolygon(
    ...         [], [([(0, 0), (1, 0), (0, 1)], [])])
    ([], [], [])
    >>> intersect_multisegment_with_multipolygon(
    ...         [((0, 0), (1, 0)), ((0, 1), (1, 0))], [])
    ([], [], [])
    >>> intersect_multisegment_with_multipolygon(
    ...         [((0, 0), (1, 0)), ((0, 1), (1, 0))],
    ...         [([(0, 0), (1, 0), (0, 1)], [])])
    ([], [((0, 0), (1, 0)), ((0, 1), (1, 0))], [])
    >>> intersect_multisegment_with_multipolygon(
    ...         [((0, 0), (1, 0)), ((1, 1), (2, 2))],
    ...         [([(0, 0), (1, 0), (1, 1), (0, 1)], [])])
    ([(1, 1)], [((0, 0), (1, 0))], [])
    """
    return _mixed.Intersection(multisegment, multipolygon, accurate).compute()


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

    >>> complete_intersect_multipolygons([], [])
    ([], [], [])
    >>> complete_intersect_multipolygons([([(0, 0), (1, 0), (0, 1)], [])], [])
    ([], [], [])
    >>> complete_intersect_multipolygons([], [([(0, 0), (1, 0), (0, 1)], [])])
    ([], [], [])
    >>> complete_intersect_multipolygons([([(0, 0), (1, 0), (0, 1)], [])],
    ...                                  [([(0, 0), (1, 0), (0, 1)], [])])
    ([], [], [([(0, 0), (1, 0), (0, 1)], [])])
    >>> complete_intersect_multipolygons([([(0, 0), (1, 0), (0, 1)], [])],
    ...                                  [([(0, 1), (1, 0), (1, 1)], [])])
    ([], [((0, 1), (1, 0))], [])
    >>> complete_intersect_multipolygons([([(0, 0), (1, 0), (0, 1)], [])],
    ...                                  [([(1, 0), (2, 0), (2, 1)], [])])
    ([(1, 0)], [], [])
    """
    return _shaped.CompleteIntersection(left, right, accurate).compute()


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

    >>> intersect_multipolygons([], [])
    []
    >>> intersect_multipolygons([([(0, 0), (1, 0), (0, 1)], [])], [])
    []
    >>> intersect_multipolygons([], [([(0, 0), (1, 0), (0, 1)], [])])
    []
    >>> intersect_multipolygons([([(0, 0), (1, 0), (0, 1)], [])],
    ...                         [([(0, 0), (1, 0), (0, 1)], [])])
    [([(0, 0), (1, 0), (0, 1)], [])]
    """
    return _shaped.Intersection(left, right, accurate).compute()


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

    >>> subtract_multipolygons([], [])
    []
    >>> subtract_multipolygons([([(0, 0), (1, 0), (0, 1)], [])], [])
    [([(0, 0), (1, 0), (0, 1)], [])]
    >>> subtract_multipolygons([], [([(0, 0), (1, 0), (0, 1)], [])])
    []
    >>> subtract_multipolygons([([(0, 0), (1, 0), (0, 1)], [])],
    ...                        [([(0, 0), (1, 0), (0, 1)], [])])
    []
    """
    return _shaped.Difference(minuend, subtrahend, accurate).compute()


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

    >>> symmetric_subtract_multipolygons([], [])
    []
    >>> symmetric_subtract_multipolygons([([(0, 0), (1, 0), (0, 1)], [])], [])
    [([(0, 0), (1, 0), (0, 1)], [])]
    >>> symmetric_subtract_multipolygons([], [([(0, 0), (1, 0), (0, 1)], [])])
    [([(0, 0), (1, 0), (0, 1)], [])]
    >>> symmetric_subtract_multipolygons([([(0, 0), (1, 0), (0, 1)], [])],
    ...                                  [([(0, 0), (1, 0), (0, 1)], [])])
    []
    """
    return _shaped.SymmetricDifference(left, right, accurate).compute()


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

    >>> unite_multipolygons([], [])
    []
    >>> unite_multipolygons([([(0, 0), (1, 0), (0, 1)], [])], [])
    [([(0, 0), (1, 0), (0, 1)], [])]
    >>> unite_multipolygons([], [([(0, 0), (1, 0), (0, 1)], [])])
    [([(0, 0), (1, 0), (0, 1)], [])]
    >>> unite_multipolygons([([(0, 0), (1, 0), (0, 1)], [])],
    ...                     [([(0, 0), (1, 0), (0, 1)], [])])
    [([(0, 0), (1, 0), (0, 1)], [])]
    """
    return _shaped.Union(left, right, accurate).compute()
