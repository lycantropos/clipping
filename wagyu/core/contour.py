from typing import List

from wagyu.hints import Contour
from .edge import Edge


def contour_to_edges(contour: Contour) -> List[Edge]:
    return [Edge(contour[index - 1], contour[index])
            for index in range(len(contour))]
