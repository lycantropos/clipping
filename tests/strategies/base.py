from fractions import Fraction
from functools import partial

from hypothesis import strategies

MAX_NUMBER = 10 ** 10
MIN_NUMBER = -MAX_NUMBER
coordinates_strategies_factories = {
    float: partial(strategies.floats,
                   allow_nan=False,
                   allow_infinity=False),
    Fraction: partial(strategies.fractions,
                      max_denominator=MAX_NUMBER),
    int: strategies.integers,
}
coordinates_strategies = strategies.sampled_from(
        [factory(MIN_NUMBER, MAX_NUMBER)
         for factory in coordinates_strategies_factories.values()])
