from itertools import combinations
from typing import (List,
                    Tuple)

from hypothesis import strategies
from hypothesis_geometry import planar

from clipping.hints import (Coordinate,
                            Multipolygon,
                            Multisegment,
                            Point,
                            Segment)
from tests.strategies import (coordinates_strategies,
                              rational_coordinates_strategies)
from tests.utils import (Strategy,
                         to_pairs,
                         to_triplets)


def points_to_nets(points: Strategy[Point]) -> Strategy[List[Segment]]:
    def to_net(points_list: List[Point]) -> List[Segment]:
        return list(combinations(points_list, 2))

    return (strategies.lists(points,
                             min_size=2,
                             max_size=8,
                             unique=True)
            .map(to_net))


rational_segments_lists = (
        (rational_coordinates_strategies.map(planar.segments)
         .flatmap(strategies.lists))
        | (rational_coordinates_strategies.map(planar.points)
           .flatmap(points_to_nets)))
segments_lists = ((coordinates_strategies.map(planar.segments)
                   .flatmap(strategies.lists))
                  | (coordinates_strategies.map(planar.points)
                     .flatmap(points_to_nets)))
empty_multipolygons = empty_multiregions = empty_multisegments = (
    strategies.builds(list))
multipolygons = coordinates_strategies.flatmap(planar.multipolygons)
multiregions = coordinates_strategies.flatmap(planar.multicontours)
multisegments = coordinates_strategies.flatmap(planar.multisegments)
empty_multisegments_with_multisegments = strategies.tuples(empty_multisegments,
                                                           multisegments)
rational_multisegments_strategies = (rational_coordinates_strategies
                                     .map(planar.multisegments))
rational_multisegments_pairs = (rational_multisegments_strategies
                                .flatmap(to_pairs))
rational_multisegments_triplets = (rational_multisegments_strategies
                                   .flatmap(to_triplets))
multisegments_strategies = coordinates_strategies.map(planar.multisegments)
multisegments_pairs = multisegments_strategies.flatmap(to_pairs)
multisegments_triplets = multisegments_strategies.flatmap(to_triplets)
empty_multipolygons_with_multisegments = strategies.tuples(empty_multipolygons,
                                                           multisegments)
multipolygons_with_empty_multisegments = strategies.tuples(multipolygons,
                                                           empty_multisegments)


def coordinates_to_multipolygons_with_multisegments(
        coordinates: Strategy[Coordinate]) -> Strategy[Tuple[Multipolygon,
                                                             Multisegment]]:
    return strategies.tuples(planar.multipolygons(coordinates),
                             planar.multisegments(coordinates))


rational_multipolygons_with_multisegments = (
    rational_coordinates_strategies.flatmap(
            coordinates_to_multipolygons_with_multisegments))
multipolygons_with_multisegments = coordinates_strategies.flatmap(
        coordinates_to_multipolygons_with_multisegments)
empty_multipolygons_with_multipolygons = strategies.tuples(empty_multipolygons,
                                                           multipolygons)
empty_multiregions_with_multiregions = strategies.tuples(empty_multiregions,
                                                         multiregions)
multipolygons_strategies = coordinates_strategies.map(planar.multipolygons)
multipolygons_pairs = multipolygons_strategies.flatmap(to_pairs)
multipolygons_triplets = multipolygons_strategies.flatmap(to_triplets)
multiregions_strategies = coordinates_strategies.map(planar.multicontours)
multiregions_pairs = multiregions_strategies.flatmap(to_pairs)
multiregions_triplets = multiregions_strategies.flatmap(to_triplets)
