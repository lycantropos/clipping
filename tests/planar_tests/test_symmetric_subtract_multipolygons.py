from ground.hints import Multipolygon
from hypothesis import given

from clipping.planar import (intersect_multipolygons,
                             subtract_multipolygons,
                             symmetric_subtract_multipolygons,
                             unite_multipolygons)
from tests.utils import (MultipolygonsPair,
                         MultipolygonsTriplet,
                         are_compounds_similar,
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

    result = symmetric_subtract_multipolygons(left_multipolygon,
                                              right_multipolygon)

    assert is_multipolygon(result)


@given(strategies.multipolygons)
def test_self_inverse(multipolygon: Multipolygon) -> None:
    result = symmetric_subtract_multipolygons(multipolygon, multipolygon)

    assert not result.polygons


@given(strategies.multipolygons_pairs)
def test_commutativity(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = symmetric_subtract_multipolygons(left_multipolygon,
                                              right_multipolygon)

    assert result == symmetric_subtract_multipolygons(right_multipolygon,
                                                      left_multipolygon)


@given(strategies.multipolygons_triplets)
def test_associativity(multipolygons_triplet: MultipolygonsTriplet) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = symmetric_subtract_multipolygons(
            symmetric_subtract_multipolygons(left_multipolygon,
                                             mid_multipolygon),
            right_multipolygon)

    assert are_compounds_similar(
            result, symmetric_subtract_multipolygons(
                    left_multipolygon,
                    symmetric_subtract_multipolygons(mid_multipolygon,
                                                     right_multipolygon)))


@given(strategies.multipolygons_triplets)
def test_repeated(multipolygons_triplet: MultipolygonsTriplet) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = symmetric_subtract_multipolygons(
            symmetric_subtract_multipolygons(left_multipolygon,
                                             mid_multipolygon),
            symmetric_subtract_multipolygons(mid_multipolygon,
                                             right_multipolygon))

    assert are_compounds_similar(result,
                                 symmetric_subtract_multipolygons(
                                             left_multipolygon,
                                             right_multipolygon))


@given(strategies.multipolygons_pairs)
def test_equivalents(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = symmetric_subtract_multipolygons(left_multipolygon,
                                              right_multipolygon)

    assert result == unite_multipolygons(
            subtract_multipolygons(left_multipolygon, right_multipolygon),
            subtract_multipolygons(right_multipolygon, left_multipolygon))
    assert result == subtract_multipolygons(
            unite_multipolygons(left_multipolygon, right_multipolygon),
            intersect_multipolygons(right_multipolygon, left_multipolygon))


@given(strategies.multipolygons_pairs)
def test_reversals(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = symmetric_subtract_multipolygons(left_multipolygon,
                                              right_multipolygon)

    assert are_compounds_similar(
            result, symmetric_subtract_multipolygons(
                    reverse_multipolygon(left_multipolygon),
                    right_multipolygon))
    assert are_compounds_similar(
            result,
            symmetric_subtract_multipolygons(left_multipolygon,
                                             reverse_multipolygon(
                                                     right_multipolygon)))
    assert are_compounds_similar(
            result,
            symmetric_subtract_multipolygons(
                    reverse_multipolygon_borders(left_multipolygon),
                    right_multipolygon))
    assert are_compounds_similar(
            result, symmetric_subtract_multipolygons(
                    left_multipolygon,
                    reverse_multipolygon_borders(right_multipolygon)))
    assert are_compounds_similar(
            result,
            symmetric_subtract_multipolygons(
                    reverse_multipolygon_holes(left_multipolygon),
                    right_multipolygon))
    assert are_compounds_similar(
            result, symmetric_subtract_multipolygons(
                    left_multipolygon,
                    reverse_multipolygon_holes(right_multipolygon)))
    assert are_compounds_similar(
            result, symmetric_subtract_multipolygons(
                    reverse_multipolygon_holes_contours(left_multipolygon),
                    right_multipolygon))
    assert are_compounds_similar(
            result, symmetric_subtract_multipolygons(
                    left_multipolygon,
                    reverse_multipolygon_holes_contours(right_multipolygon)))
    assert are_compounds_similar(
            result,
            reverse_multipolygon_coordinates(symmetric_subtract_multipolygons(
                    reverse_multipolygon_coordinates(left_multipolygon),
                    reverse_multipolygon_coordinates(right_multipolygon))))
