from typing import Tuple

from hypothesis import strategies
from hypothesis_geometry import planar

from clipping.hints import (BoundingBox,
                            Contour,
                            Coordinate,
                            Polygon)
from tests.strategies import coordinates_strategies
from tests.utils import (Strategy,
                         to_pairs,
                         to_triplets)

bounding_boxes = coordinates_strategies.flatmap(planar.bounding_boxes)


def to_contours_with_bounding_boxes(coordinates: Strategy[Coordinate]
                                    ) -> Strategy[Tuple[Contour, BoundingBox]]:
    return strategies.tuples(planar.contours(coordinates),
                             planar.bounding_boxes(coordinates))


contours_with_bounding_boxes = (coordinates_strategies
                                .flatmap(to_contours_with_bounding_boxes))


def to_polygons_with_bounding_boxes(coordinates: Strategy[Coordinate]
                                    ) -> Strategy[Tuple[Polygon, BoundingBox]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.bounding_boxes(coordinates))


polygons_with_bounding_boxes = (coordinates_strategies
                                .flatmap(to_polygons_with_bounding_boxes))
bounding_boxes_strategies = coordinates_strategies.map(planar.bounding_boxes)
bounding_boxes_pairs = bounding_boxes_strategies.flatmap(to_pairs)
bounding_boxes_triplets = bounding_boxes_strategies.flatmap(to_triplets)
