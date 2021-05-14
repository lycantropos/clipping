from hypothesis import given

from clipping.hints import Region
from clipping.planar import (complete_intersect_regions,
                             intersect_regions)
from tests.utils import (RegionsPair,
                         are_compounds_similar,
                         compound_to_shaped,
                         is_holeless_compound,
                         is_polygon_similar_to_region,
                         reverse_compound_coordinates,
                         reverse_region,
                         reverse_region_coordinates)
from . import strategies


@given(strategies.regions_pairs)
def test_basic(regions_pair: RegionsPair) -> None:
    first, second = regions_pair

    result = complete_intersect_regions(first, second)

    assert is_holeless_compound(result)


@given(strategies.regions)
def test_idempotence(region: Region) -> None:
    result = complete_intersect_regions(region, region)

    assert is_polygon_similar_to_region(result, region)


@given(strategies.regions_pairs)
def test_commutativity(regions_pair: RegionsPair) -> None:
    first, second = regions_pair

    result = complete_intersect_regions(first, second)

    assert result == complete_intersect_regions(second, first)


@given(strategies.regions_pairs)
def test_connection_with_intersect(regions_pair: RegionsPair
                                   ) -> None:
    first, second = regions_pair

    result = complete_intersect_regions(first, second)

    assert compound_to_shaped(result) == intersect_regions(first, second)


@given(strategies.regions_pairs)
def test_reversals(regions_pair: RegionsPair) -> None:
    first, second = regions_pair

    result = complete_intersect_regions(first, second)

    assert result == complete_intersect_regions(first, reverse_region(second))
    assert are_compounds_similar(
            result,
            reverse_compound_coordinates(complete_intersect_regions(
                    reverse_region_coordinates(first),
                    reverse_region_coordinates(second))))
