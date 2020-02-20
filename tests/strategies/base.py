from fractions import Fraction
from typing import Optional

from bentley_ottmann.hints import Scalar
from hypothesis import strategies

from tests.utils import Strategy

MAX_FLOAT = 1.e10
MIN_FLOAT = -MAX_FLOAT


def to_floats(*,
              min_value: Optional[Scalar] = MIN_FLOAT,
              max_value: Optional[Scalar] = MAX_FLOAT,
              allow_nan: bool = False,
              allow_infinity: bool = False) -> Strategy:
    return strategies.floats(min_value=min_value,
                             max_value=max_value,
                             allow_nan=allow_nan,
                             allow_infinity=allow_infinity)


scalars_strategies_factories = {float: to_floats,
                                Fraction: strategies.fractions,
                                int: strategies.integers}
scalars_strategies = strategies.sampled_from(
        [factory()
         for factory in scalars_strategies_factories.values()])
