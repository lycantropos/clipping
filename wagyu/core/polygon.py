from typing import (Iterable,
                    Optional)

from wagyu.hints import (Contour,
                         Polygon)
from .point_node import (PointNode,
                         point_node_to_point)
from .ring import Ring


def rings_to_polygons(rings: Iterable[Optional[Ring]]) -> Iterable[Polygon]:
    for ring in rings:
        if ring is None:
            continue
        yield (point_node_to_contour(ring.node),
               [point_node_to_contour(child.node)
                for child in ring.children
                if child is not None])
        for child in ring.children:
            if child is None:
                continue
            yield from rings_to_polygons(child.children)


def point_node_to_contour(node: PointNode) -> Contour:
    return list(map(point_node_to_point, node))
