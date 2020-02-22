from fractions import Fraction
from functools import partial

from hypothesis import strategies

MAX_FLOAT = 10 ** 10
MIN_FLOAT = -MAX_FLOAT
scalars_strategies_factories = {float: partial(strategies.floats,
                                               MIN_FLOAT, MAX_FLOAT,
                                               allow_nan=False,
                                               allow_infinity=False),
                                Fraction: strategies.fractions,
                                int: strategies.integers}
scalars_strategies = strategies.sampled_from(
        [factory()
         for factory in scalars_strategies_factories.values()])
