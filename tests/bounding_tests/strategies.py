from typing import Tuple

from ground.hints import Coordinate
from hypothesis import strategies
from hypothesis_geometry import planar

from clipping.hints import Region
from tests.strategies import coordinates_strategies
from tests.utils import (Box,
                         Contour,
                         Polygon,
                         Strategy,
                         sort_pair,
                         to_pairs,
                         to_triplets)


def to_degenerate_boxes(coordinates: Strategy[Coordinate]
                        ) -> Strategy[Box]:
    def to_x_degenerate_box(x: Coordinate,
                                     ys: Tuple[Coordinate, Coordinate]
                                     ) -> Box:
        return Box(x, x, *sort_pair(ys))

    def to_y_degenerate_box(xs: Tuple[Coordinate, Coordinate],
                                     y: Coordinate) -> Box:
        return Box(*sort_pair(xs), y, y)

    unique_coordinates_pairs = strategies.lists(coordinates,
                                                min_size=2,
                                                max_size=2,
                                                unique=True)
    return (strategies.builds(to_x_degenerate_box, coordinates,
                              unique_coordinates_pairs)
            | strategies.builds(to_y_degenerate_box,
                                unique_coordinates_pairs, coordinates))


non_degenerate_boxes = coordinates_strategies.flatmap(planar.boxes)
degenerate_boxes = coordinates_strategies.flatmap(to_degenerate_boxes)
boxes = degenerate_boxes | non_degenerate_boxes


def to_contours_with_boxes(coordinates: Strategy[Coordinate]
                           ) -> Strategy[Tuple[Contour, Box]]:
    return strategies.tuples(planar.contours(coordinates),
                             planar.boxes(coordinates))


contours_with_boxes = coordinates_strategies.flatmap(to_contours_with_boxes)


def to_polygons_with_boxes(coordinates: Strategy[Coordinate]
                           ) -> Strategy[Tuple[Polygon, Box]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.boxes(coordinates))


polygons_with_boxes = coordinates_strategies.flatmap(to_polygons_with_boxes)


def to_regions_with_boxes(coordinates: Strategy[Coordinate]
                          ) -> Strategy[Tuple[Region, Box]]:
    return strategies.tuples(planar.contours(coordinates),
                             planar.boxes(coordinates))


regions_with_boxes = coordinates_strategies.flatmap(to_regions_with_boxes)
boxes_strategies = coordinates_strategies.map(planar.boxes)
boxes_pairs = boxes_strategies.flatmap(to_pairs)
boxes_triplets = boxes_strategies.flatmap(to_triplets)
