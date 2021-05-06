from ground.hints import Multipolygon
from hypothesis import given

from clipping.planar import (intersect_multipolygons,
                             subtract_multipolygons,
                             unite_multipolygons)
from tests.utils import (MultipolygonsPair,
                         MultipolygonsTriplet,
                         are_multipolygons_similar,
                         is_multipolygon,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_coordinates,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours)
from . import strategies


@given(strategies.multipolygons_pairs)
def test_basic(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = intersect_multipolygons(left_multipolygon, right_multipolygon)

    assert is_multipolygon(result)


@given(strategies.multipolygons)
def test_idempotence(multipolygon: Multipolygon) -> None:
    result = intersect_multipolygons(multipolygon, multipolygon)

    assert are_multipolygons_similar(result, multipolygon)


@given(strategies.empty_multipolygons_with_multipolygons)
def test_left_absorbing_element(empty_multipolygon_with_multipolygon
                                : MultipolygonsPair) -> None:
    empty_multipolygon, multipolygon = empty_multipolygon_with_multipolygon

    result = intersect_multipolygons(empty_multipolygon, multipolygon)

    assert not result.polygons


@given(strategies.empty_multipolygons_with_multipolygons)
def test_right_absorbing_element(empty_multipolygon_with_multipolygon
                                 : MultipolygonsPair) -> None:
    empty_multipolygon, multipolygon = empty_multipolygon_with_multipolygon

    result = intersect_multipolygons(multipolygon, empty_multipolygon)

    assert not result.polygons


@given(strategies.multipolygons_pairs)
def test_absorption_identity(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = intersect_multipolygons(left_multipolygon,
                                     unite_multipolygons(left_multipolygon,
                                                         right_multipolygon))

    assert are_multipolygons_similar(result, left_multipolygon)


@given(strategies.multipolygons_pairs)
def test_commutativity(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = intersect_multipolygons(left_multipolygon, right_multipolygon)

    assert result == intersect_multipolygons(right_multipolygon,
                                             left_multipolygon)


@given(strategies.multipolygons_triplets)
def test_associativity(multipolygons_triplet: MultipolygonsTriplet) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = intersect_multipolygons(
            intersect_multipolygons(left_multipolygon, mid_multipolygon),
            right_multipolygon)

    assert result == intersect_multipolygons(left_multipolygon,
                                             intersect_multipolygons(
                                                     mid_multipolygon,
                                                     right_multipolygon))


@given(strategies.multipolygons_triplets)
def test_difference_operand(multipolygons_triplet: MultipolygonsTriplet
                            ) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = intersect_multipolygons(
            subtract_multipolygons(left_multipolygon, mid_multipolygon),
            right_multipolygon)

    assert result == subtract_multipolygons(
            intersect_multipolygons(left_multipolygon, right_multipolygon),
            mid_multipolygon)


@given(strategies.multipolygons_triplets)
def test_distribution_over_union(multipolygons_triplet: MultipolygonsTriplet
                                 ) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = intersect_multipolygons(left_multipolygon,
                                     unite_multipolygons(mid_multipolygon,
                                                         right_multipolygon))

    assert result == unite_multipolygons(
            intersect_multipolygons(left_multipolygon, mid_multipolygon),
            intersect_multipolygons(left_multipolygon, right_multipolygon))


@given(strategies.multipolygons_pairs)
def test_equivalents(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = intersect_multipolygons(left_multipolygon, right_multipolygon)

    assert are_multipolygons_similar(
            result,
            subtract_multipolygons(left_multipolygon,
                                   subtract_multipolygons(left_multipolygon,
                                                          right_multipolygon)))


@given(strategies.multipolygons_pairs)
def test_reversals(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = intersect_multipolygons(left_multipolygon, right_multipolygon)

    assert result == intersect_multipolygons(
            reverse_multipolygon(left_multipolygon), right_multipolygon)
    assert result == intersect_multipolygons(
            left_multipolygon, reverse_multipolygon(right_multipolygon))
    assert result == intersect_multipolygons(
            reverse_multipolygon_borders(left_multipolygon),
            right_multipolygon)
    assert result == intersect_multipolygons(
            left_multipolygon,
            reverse_multipolygon_borders(right_multipolygon))
    assert result == intersect_multipolygons(
            reverse_multipolygon_holes(left_multipolygon), right_multipolygon)
    assert result == intersect_multipolygons(
            left_multipolygon, reverse_multipolygon_holes(right_multipolygon))
    assert result == intersect_multipolygons(
            reverse_multipolygon_holes_contours(left_multipolygon),
            right_multipolygon)
    assert result == intersect_multipolygons(
            left_multipolygon,
            reverse_multipolygon_holes_contours(right_multipolygon))
    assert are_multipolygons_similar(
            result, reverse_multipolygon_coordinates(intersect_multipolygons(
                    reverse_multipolygon_coordinates(left_multipolygon),
                    reverse_multipolygon_coordinates(right_multipolygon))))
