from itertools import combinations
from typing import List

from ground.hints import Scalar
from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import coordinates_strategies
from tests.utils import (MultisegmentWithSegment,
                         Point,
                         PolygonWithMultisegment,
                         PolygonWithSegment,
                         Segment,
                         Strategy,
                         to_pairs,
                         to_triplets)

segments_strategies = coordinates_strategies.map(planar.segments)
segments = coordinates_strategies.flatmap(planar.segments)
segments_pairs = segments_strategies.flatmap(to_pairs)
segments_triplets = segments_strategies.flatmap(to_triplets)


def points_to_nets(points: Strategy[Point]) -> Strategy[List[Segment]]:
    def to_net(points_list: List[Point]) -> List[Segment]:
        return [Segment(start, end)
                for start, end in combinations(points_list, 2)]

    return (strategies.lists(points,
                             min_size=2,
                             max_size=8,
                             unique=True)
            .map(to_net))


segments_lists = ((coordinates_strategies.map(planar.segments)
                   .flatmap(strategies.lists))
                  | (coordinates_strategies.map(planar.points)
                     .flatmap(points_to_nets)))
polygons = coordinates_strategies.flatmap(planar.polygons)
regions = coordinates_strategies.flatmap(planar.contours)
multisegments = coordinates_strategies.flatmap(planar.multisegments)
multisegments_strategies = coordinates_strategies.map(planar.multisegments)
multisegments_pairs = multisegments_strategies.flatmap(to_pairs)
multisegments_triplets = multisegments_strategies.flatmap(to_triplets)


def coordinates_to_multisegments_with_segments(
        coordinates: Strategy[Scalar]) -> Strategy[MultisegmentWithSegment]:
    return strategies.tuples(planar.multisegments(coordinates),
                             planar.segments(coordinates))


multisegments_with_segments = coordinates_strategies.flatmap(
        coordinates_to_multisegments_with_segments)


def coordinates_to_polygons_with_segments(coordinates: Strategy[Scalar]
                                          ) -> Strategy[PolygonWithSegment]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.segments(coordinates))


polygons_with_segments = (coordinates_strategies
                          .flatmap(coordinates_to_polygons_with_segments))


def coordinates_to_polygons_with_multisegments(
        coordinates: Strategy[Scalar]) -> Strategy[PolygonWithMultisegment]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.multisegments(coordinates))


polygons_with_multisegments = coordinates_strategies.flatmap(
        coordinates_to_polygons_with_multisegments)
polygons_strategies = coordinates_strategies.map(planar.polygons)
polygons_pairs = polygons_strategies.flatmap(to_pairs)
polygons_triplets = polygons_strategies.flatmap(to_triplets)
regions_strategies = coordinates_strategies.map(planar.contours)
regions_pairs = regions_strategies.flatmap(to_pairs)
regions_triplets = regions_strategies.flatmap(to_triplets)
