from wagyu.hints import Multipolygon
from . import hot_pixels
from .enums import (Fill,
                    OperandKind,
                    OperationKind)
from .local_minimum import multipolygon_to_local_minimums
from .ring_manager import RingManager


def execute(subject: Multipolygon,
            clip: Multipolygon,
            operation_kind: OperationKind,
            subject_fill_type: Fill,
            clip_fill_type: Fill,
            accurate: bool) -> Multipolygon:
    minimums = multipolygon_to_local_minimums(subject, OperandKind.SUBJECT)
    minimums.extend(multipolygon_to_local_minimums(clip, OperandKind.CLIP))
    if not minimums:
        return []
    manager = RingManager()
    manager.hot_pixels = hot_pixels.from_local_minimums(minimums)
    manager.execute_vatti(minimums, operation_kind, subject_fill_type,
                          clip_fill_type)
    manager.correct_topology()
    return manager.build_result()
