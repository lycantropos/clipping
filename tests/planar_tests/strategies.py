from itertools import combinations
from typing import (List,
                    Tuple)

from ground.hints import Scalar
from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import coordinates_strategies
from tests.utils import (Multipolygon,
                         Multisegment,
                         Point,
                         Segment,
                         Strategy,
                         to_pairs,
                         to_triplets)


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
multipolygons = coordinates_strategies.flatmap(planar.multipolygons)
multiregions = coordinates_strategies.flatmap(planar.multicontours)
multisegments = coordinates_strategies.flatmap(planar.multisegments)
multisegments_strategies = coordinates_strategies.map(planar.multisegments)
multisegments_pairs = multisegments_strategies.flatmap(to_pairs)
multisegments_triplets = multisegments_strategies.flatmap(to_triplets)


def coordinates_to_multipolygons_with_multisegments(
        coordinates: Strategy[Scalar]) -> Strategy[Tuple[Multipolygon,
                                                         Multisegment]]:
    return strategies.tuples(planar.multipolygons(coordinates),
                             planar.multisegments(coordinates))


multipolygons_with_multisegments = coordinates_strategies.flatmap(
        coordinates_to_multipolygons_with_multisegments)
multipolygons_strategies = coordinates_strategies.map(planar.multipolygons)
multipolygons_pairs = multipolygons_strategies.flatmap(to_pairs)
multipolygons_triplets = multipolygons_strategies.flatmap(to_triplets)
multiregions_strategies = coordinates_strategies.map(planar.multicontours)
multiregions_pairs = multiregions_strategies.flatmap(to_pairs)
multiregions_triplets = multiregions_strategies.flatmap(to_triplets)
