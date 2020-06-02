"""
Boolean operations on polygons/multipolygons in the plane.

Based on algorithm by F. Martinez et al.

Time complexity:
    ``O((len(left) + len(right) + len(intersections)) * log (len(left) \
+ len(right)))``
Memory complexity:
    ``O(len(left) + len(right) + len(intersections))``
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

**Mix** --- triplet of disjoint/touching multipoint, multisegment and multipolygon.
"""

from .core import operation as _operation
from .hints import (Mix,
                    Multipolygon)


def complete_intersect(left: Multipolygon,
                       right: Multipolygon,
                       *,
                       accurate: bool = True) -> Mix:
    """
    Returns intersection of multipolygons considering degenerate cases
    with polygons touching each other in points/segments.

    :param left: left operand.
    :param right: right operand.
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: intersection of operands.

    >>> complete_intersect([], [])
    ([], [], [])
    >>> complete_intersect([([(0, 0), (1, 0), (0, 1)], [])], [])
    ([], [], [])
    >>> complete_intersect([], [([(0, 0), (1, 0), (0, 1)], [])])
    ([], [], [])
    >>> complete_intersect([([(0, 0), (1, 0), (0, 1)], [])],
    ...                    [([(0, 0), (1, 0), (0, 1)], [])])
    ([], [], [([(0, 0), (1, 0), (0, 1)], [])])
    >>> complete_intersect([([(0, 0), (1, 0), (0, 1)], [])],
    ...                    [([(0, 1), (1, 0), (1, 1)], [])])
    ([], [((0, 1), (1, 0))], [])
    >>> complete_intersect([([(0, 0), (1, 0), (0, 1)], [])],
    ...                    [([(1, 0), (2, 0), (2, 1)], [])])
    ([(1, 0)], [], [])
    """
    return _operation.compute(_operation.CompleteIntersection, left, right,
                              accurate=accurate)


def intersect(left: Multipolygon,
              right: Multipolygon,
              *,
              accurate: bool = True) -> Multipolygon:
    """
    Returns intersection of multipolygons.

    :param left: left operand.
    :param right: right operand.
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: intersection of operands.

    >>> intersect([], [])
    []
    >>> intersect([([(0, 0), (1, 0), (0, 1)], [])], [])
    []
    >>> intersect([], [([(0, 0), (1, 0), (0, 1)], [])])
    []
    >>> intersect([([(0, 0), (1, 0), (0, 1)], [])],
    ...           [([(0, 0), (1, 0), (0, 1)], [])])
    [([(0, 0), (1, 0), (0, 1)], [])]
    """
    return _operation.compute(_operation.Intersection, left, right,
                              accurate=accurate)


def subtract(minuend: Multipolygon,
             subtrahend: Multipolygon,
             *,
             accurate: bool = True) -> Multipolygon:
    """
    Returns difference of multipolygons.

    :param minuend: multipolygon from which to subtract.
    :param subtrahend: multipolygon which to subtract.
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: difference between minuend and subtrahend.

    >>> subtract([], [])
    []
    >>> subtract([([(0, 0), (1, 0), (0, 1)], [])], [])
    [([(0, 0), (1, 0), (0, 1)], [])]
    >>> subtract([], [([(0, 0), (1, 0), (0, 1)], [])])
    []
    >>> subtract([([(0, 0), (1, 0), (0, 1)], [])],
    ...          [([(0, 0), (1, 0), (0, 1)], [])])
    []
    """
    return _operation.compute(_operation.Difference, minuend, subtrahend,
                              accurate=accurate)


def symmetric_subtract(left: Multipolygon,
                       right: Multipolygon,
                       *,
                       accurate: bool = True) -> Multipolygon:
    """
    Returns symmetric difference of multipolygons.

    :param left: left operand.
    :param right: right operand.
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: symmetric difference of operands.

    >>> symmetric_subtract([], [])
    []
    >>> symmetric_subtract([([(0, 0), (1, 0), (0, 1)], [])], [])
    [([(0, 0), (1, 0), (0, 1)], [])]
    >>> symmetric_subtract([], [([(0, 0), (1, 0), (0, 1)], [])])
    [([(0, 0), (1, 0), (0, 1)], [])]
    >>> symmetric_subtract([([(0, 0), (1, 0), (0, 1)], [])],
    ...                    [([(0, 0), (1, 0), (0, 1)], [])])
    []
    """
    return _operation.compute(_operation.SymmetricDifference, left, right,
                              accurate=accurate)


def unite(left: Multipolygon,
          right: Multipolygon,
          *,
          accurate: bool = True) -> Multipolygon:
    """
    Returns union of multipolygons.

    :param left: left operand.
    :param right: right operand.
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: union of operands.

    >>> unite([], [])
    []
    >>> unite([([(0, 0), (1, 0), (0, 1)], [])], [])
    [([(0, 0), (1, 0), (0, 1)], [])]
    >>> unite([], [([(0, 0), (1, 0), (0, 1)], [])])
    [([(0, 0), (1, 0), (0, 1)], [])]
    >>> unite([([(0, 0), (1, 0), (0, 1)], [])],
    ...       [([(0, 0), (1, 0), (0, 1)], [])])
    [([(0, 0), (1, 0), (0, 1)], [])]
    """
    return _operation.compute(_operation.Union, left, right,
                              accurate=accurate)
