from hypothesis_geometry import planar

from tests.strategies import coordinates_strategies
from tests.utils import to_pairs

bounding_boxes = coordinates_strategies.flatmap(planar.bounding_boxes)
bounding_boxes_strategies = coordinates_strategies.map(planar.bounding_boxes)
bounding_boxes_pairs = bounding_boxes_strategies.flatmap(to_pairs)
