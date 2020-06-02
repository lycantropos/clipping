from functools import partial

from hypothesis import strategies
from hypothesis_geometry import planar

from tests.strategies import coordinates_strategies
from tests.utils import (to_pairs,
                         to_triplets)

empty_multipolygons = strategies.builds(list)
multipolygons_strategies = coordinates_strategies.map(planar.multipolygons)
multipolygons = coordinates_strategies.flatmap(planar.multipolygons)
empty_multipolygons_with_multipolygons = strategies.tuples(empty_multipolygons,
                                                           multipolygons)
empty_multipolygons_lists = strategies.builds(list)
multipolygons_lists = multipolygons_strategies.flatmap(strategies.lists)
non_empty_multipolygons_lists = (multipolygons_strategies
                                 .flatmap(partial(strategies.lists,
                                                  min_size=1)))
multipolygons_pairs = multipolygons_strategies.flatmap(to_pairs)
multipolygons_triplets = multipolygons_strategies.flatmap(to_triplets)
