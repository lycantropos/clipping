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


def to_simple_multipolygons(contours: Strategy[Contour]
                            ) -> Strategy[Multipolygon]:
    def to_simple_multipolygon(polygon: Polygon) -> Multipolygon:
        return [polygon]

    return (strategies.tuples(contours, strategies.builds(list))
            .map(to_simple_multipolygon))


multipolygons_strategies = contours_strategies.map(to_simple_multipolygons)
multipolygons = multipolygons_strategies.flatmap(identity)
empty_multipolygons_with_multipolygons = strategies.tuples(
        multipolygons, strategies.builds(list))
multipolygons_pairs = multipolygons_strategies.flatmap(to_pairs)
multipolygons_triplets = multipolygons_strategies.flatmap(to_triplets)
