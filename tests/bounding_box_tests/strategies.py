from typing import Tuple

from hypothesis import strategies
from hypothesis_geometry import planar

from clipping.core.hints import BoundingBox
from clipping.hints import (Contour,
                            Coordinate,
                            Polygon)
from tests.strategies import coordinates_strategies
from tests.utils import (Strategy,
                         to_pairs,
                         to_triplets)


def to_degenerate_bounding_boxes(coordinates: Strategy[Coordinate]
                                 ) -> Strategy[BoundingBox]:
    def to_x_degenerate_bounding_box(x: Coordinate,
                                     y_min: Coordinate,
                                     y_max: Coordinate) -> BoundingBox:
        return x, x, y_min, y_max

    def to_y_degenerate_bounding_box(x_min: Coordinate,
                                     x_max: Coordinate,
                                     y: Coordinate) -> BoundingBox:
        return y, y, x_min, x_max

    return (strategies.builds(to_x_degenerate_bounding_box, coordinates,
                              coordinates, coordinates)
            | strategies.builds(to_y_degenerate_bounding_box, coordinates,
                                coordinates, coordinates))


bounding_boxes = (coordinates_strategies.flatmap(to_degenerate_bounding_boxes)
                  | coordinates_strategies.flatmap(planar.bounding_boxes))


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
