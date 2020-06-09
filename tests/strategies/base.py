from fractions import Fraction
from functools import partial

from hypothesis import strategies

MAX_NUMBER = 10 ** 2
MIN_NUMBER = -MAX_NUMBER
rational_coordinates_strategies_factories = {
    Fraction: partial(strategies.fractions,
                      max_denominator=MAX_NUMBER),
    int: strategies.integers,
}
coordinates_strategies_factories = {
    float: partial(strategies.floats,
                   allow_nan=False,
                   allow_infinity=False),
    **rational_coordinates_strategies_factories,
}
rational_coordinates_strategies = strategies.sampled_from(
        [factory(MIN_NUMBER, MAX_NUMBER)
         for factory in rational_coordinates_strategies_factories.values()])
coordinates_strategies = strategies.sampled_from(
        [factory(MIN_NUMBER, MAX_NUMBER)
         for factory in coordinates_strategies_factories.values()])
