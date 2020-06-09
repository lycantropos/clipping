from typing import Tuple

from hypothesis import strategies
from hypothesis_geometry import planar

from clipping.hints import (Coordinate,
                            Multipolygon,
                            Multisegment)
from tests.strategies import coordinates_strategies
from tests.utils import (Strategy,
                         to_pairs,
                         to_triplets)

empty_multipolygons = empty_multisegments = strategies.builds(list)
multipolygons = coordinates_strategies.flatmap(planar.multipolygons)
multisegments = coordinates_strategies.flatmap(planar.multisegments)
empty_multisegments_with_multisegments = strategies.tuples(empty_multisegments,
                                                           multisegments)
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


multipolygons_with_multisegments = coordinates_strategies.flatmap(
        coordinates_to_multipolygons_with_multisegments)
empty_multipolygons_with_multipolygons = strategies.tuples(empty_multipolygons,
                                                           multipolygons)
multipolygons_strategies = coordinates_strategies.map(planar.multipolygons)
multipolygons_pairs = multipolygons_strategies.flatmap(to_pairs)
multipolygons_triplets = multipolygons_strategies.flatmap(to_triplets)
