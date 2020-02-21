from hypothesis import strategies
from hypothesis_geometry import planar

from clipping.hints import (Contour,
                            Multipolygon,
                            Polygon)
from tests.strategies import scalars_strategies
from tests.utils import (Strategy,
                         identity,
                         to_pairs,
                         to_triplets)

contours_strategies = scalars_strategies.map(planar.contours)

empty_multipolygons = strategies.builds(list)


def to_simple_multipolygons(contours: Strategy[Contour]
                            ) -> Strategy[Multipolygon]:
    def to_simple_multipolygon(polygon: Polygon) -> Multipolygon:
        return [polygon]

    return (empty_multipolygons
            | (strategies.tuples(contours, empty_multipolygons)
               .map(to_simple_multipolygon)))


multipolygons_strategies = contours_strategies.map(to_simple_multipolygons)
multipolygons = multipolygons_strategies.flatmap(identity)
empty_multipolygons_with_multipolygons = strategies.tuples(empty_multipolygons,
                                                           multipolygons)
multipolygons_pairs = multipolygons_strategies.flatmap(to_pairs)
multipolygons_triplets = multipolygons_strategies.flatmap(to_triplets)
