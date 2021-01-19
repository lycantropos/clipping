from typing import (Sequence,
                    Tuple)

from ground.hints import (Contour as _Contour,
                          Multipoint as _Multipoint,
                          Multipolygon as _Multipolygon,
                          Multisegment as _Multisegment)

Region = _Contour
Multiregion = Sequence[Region]
LinearMix = Tuple[_Multipoint, _Multisegment]
Mix = Tuple[_Multipoint, _Multisegment, _Multipolygon]
HolelessMix = Tuple[_Multipoint, _Multisegment, Multiregion]
