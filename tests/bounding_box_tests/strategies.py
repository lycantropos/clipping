from typing import Tuple

from hypothesis import strategies
from hypothesis_geometry import planar

from clipping.core.hints import BoundingBox
from clipping.hints import (Contour,
                            Coordinate,
                            Polygon)
from tests.strategies import coordinates_strategies
from tests.utils import (Strategy,
                         sort_pair,
                         to_pairs,
                         to_triplets)


def to_degenerate_bounding_boxes(coordinates: Strategy[Coordinate]
                                 ) -> Strategy[BoundingBox]:
    def to_x_degenerate_bounding_box(x: Coordinate,
                                     ys: Tuple[Coordinate, Coordinate]
                                     ) -> BoundingBox:
        return (x, x, *sort_pair(ys))

    def to_y_degenerate_bounding_box(xs: Tuple[Coordinate, Coordinate],
                                     y: Coordinate) -> BoundingBox:
        return (y, y, *sort_pair(xs))

    unique_coordinates_pairs = strategies.lists(coordinates,
                                                min_size=2,
                                                max_size=2,
                                                unique=True)
    return (strategies.builds(to_x_degenerate_bounding_box, coordinates,
                              unique_coordinates_pairs)
            | strategies.builds(to_y_degenerate_bounding_box,
                                unique_coordinates_pairs, coordinates))


non_degenerate_bounding_boxes = (coordinates_strategies
                                 .flatmap(planar.bounding_boxes))
degenerate_bounding_boxes = (coordinates_strategies
                             .flatmap(to_degenerate_bounding_boxes))
bounding_boxes = degenerate_bounding_boxes | non_degenerate_bounding_boxes


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
