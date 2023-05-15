from fractions import Fraction
from functools import partial

from hypothesis import strategies

MAX_SCALAR = 10 ** 10
MIN_SCALAR = -MAX_SCALAR
coordinates_strategies_factories = {
    Fraction: partial(strategies.fractions,
                      max_denominator=MAX_SCALAR),
    int: strategies.integers,
}
coordinates_strategies = strategies.sampled_from(
        [factory(MIN_SCALAR, MAX_SCALAR)
         for factory in coordinates_strategies_factories.values()]
)
