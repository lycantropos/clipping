from hypothesis import strategies
from hypothesis_geometry import planar

from clipping.hints import (Multipolygon,
                            Polygon)
from tests.strategies import scalars_strategies
from tests.utils import (Strategy,
                         identity,
                         to_pairs,
                         to_triplets)

polygons_strategies = scalars_strategies.map(planar.polygons)
empty_multipolygons = strategies.builds(list)


def to_multipolygons(polygons: Strategy[Polygon]
                     ) -> Strategy[Multipolygon]:
    def to_multipolygon(polygon: Polygon) -> Multipolygon:
        return [polygon]

    return empty_multipolygons | polygons.map(to_multipolygon)


multipolygons_strategies = polygons_strategies.map(to_multipolygons)
multipolygons = multipolygons_strategies.flatmap(identity)
empty_multipolygons_with_multipolygons = strategies.tuples(empty_multipolygons,
                                                           multipolygons)
multipolygons_pairs = multipolygons_strategies.flatmap(to_pairs)
multipolygons_triplets = multipolygons_strategies.flatmap(to_triplets)
