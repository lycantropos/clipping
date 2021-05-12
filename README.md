clipping
========

[![](https://dev.azure.com/lycantropos/clipping/_apis/build/status/lycantropos.clipping?branchName=master)](https://dev.azure.com/lycantropos/clipping/_build/latest?definitionId=21&branchName=master "Azure Pipelines")
[![](https://readthedocs.org/projects/clip/badge/?version=latest)](https://clip.readthedocs.io/en/latest "Documentation")
[![](https://codecov.io/gh/lycantropos/clipping/branch/master/graph/badge.svg)](https://codecov.io/gh/lycantropos/clipping "Codecov")
[![](https://img.shields.io/github/license/lycantropos/clipping.svg)](https://github.com/lycantropos/clipping/blob/master/LICENSE "License")
[![](https://badge.fury.io/py/clipping.svg)](https://badge.fury.io/py/clipping "PyPI")

In what follows `python` is an alias for `python3.5` or `pypy3.5`
or any later version (`python3.6`, `pypy3.6` and so on).

Installation
------------

Install the latest `pip` & `setuptools` packages versions
```bash
python -m pip install --upgrade pip setuptools
```

### User

Download and install the latest stable version from `PyPI` repository
```bash
python -m pip install --upgrade clipping
```

### Developer

Download the latest version from `GitHub` repository
```bash
git clone https://github.com/lycantropos/clipping.git
cd clipping
```

Install dependencies
```bash
python -m pip install -r requirements.txt
```

Install
```bash
python setup.py install
```

Usage
-----
```python
>>> from ground.base import get_context
>>> context = get_context()
>>> EMPTY = context.empty
>>> Mix = context.mix_cls
>>> Multipoint = context.multipoint_cls
>>> Multisegment = context.multisegment_cls
>>> Point = context.point_cls
>>> Segment = context.segment_cls
>>> left_edge = Segment(Point(0, 0), Point(0, 1))
>>> right_edge = Segment(Point(1, 0), Point(1, 1))
>>> bottom_edge = Segment(Point(0, 0), Point(1, 0))
>>> top_edge = Segment(Point(0, 1), Point(1, 1))
>>> main_diagonal = Segment(Point(0, 0), Point(1, 1))
>>> trident = Multisegment([left_edge, main_diagonal, bottom_edge])
>>> square_edges = Multisegment([bottom_edge, right_edge, top_edge, left_edge])
>>> from clipping.planar import intersect_multisegments
>>> (intersect_multisegments(trident, square_edges)
...  == intersect_multisegments(square_edges, trident)
...  == Multisegment([left_edge, bottom_edge]))
True
>>> from clipping.planar import complete_intersect_multisegments
>>> (complete_intersect_multisegments(trident, square_edges)
...  == complete_intersect_multisegments(square_edges, trident)
...  == Mix(Multipoint([Point(1, 1)]), Multisegment([left_edge, bottom_edge]),
...         EMPTY))
True
>>> from clipping.planar import unite_multisegments
>>> (unite_multisegments(trident, square_edges)
...  == unite_multisegments(square_edges, trident)
...  == Multisegment([left_edge, bottom_edge, main_diagonal, top_edge,
...                   right_edge]))
True
>>> from clipping.planar import subtract_multisegments
>>> subtract_multisegments(trident, square_edges) == main_diagonal
True
>>> (subtract_multisegments(square_edges, trident)
...  == Multisegment([top_edge, right_edge]))
True
>>> from clipping.planar import symmetric_subtract_multisegments
>>> (symmetric_subtract_multisegments(trident, square_edges)
...  == symmetric_subtract_multisegments(square_edges, trident)
...  == Multisegment([main_diagonal, top_edge, right_edge]))
True
>>> Contour = context.contour_cls
>>> Multipolygon = context.multipolygon_cls
>>> Polygon = context.polygon_cls
>>> first_square = Contour([Point(0, 0), Point(1, 0), Point(1, 1),
...                         Point(0, 1)])
>>> second_square = Contour([Point(1, 0), Point(2, 0), Point(2, 1),
...                          Point(1, 1)])
>>> third_square = Contour([Point(1, 1), Point(2, 1), Point(2, 2),
...                         Point(1, 2)])
>>> fourth_square = Contour([Point(0, 1), Point(1, 1), Point(1, 2),
...                          Point(0, 2)])
>>> from clipping.planar import intersect_multipolygons
>>> (intersect_multipolygons(Multipolygon([Polygon(first_square, []),
...                                        Polygon(third_square, [])]),
...                          Multipolygon([Polygon(second_square, []),
...                                        Polygon(fourth_square, [])]))
...  is EMPTY)
True
>>> (intersect_multipolygons(Multipolygon([Polygon(first_square, []),
...                                        Polygon(third_square, [])]),
...                          Multipolygon([Polygon(first_square, []),
...                                        Polygon(third_square, [])]))
...  == Multipolygon([Polygon(first_square, []), Polygon(third_square, [])]))
True
>>> from clipping.planar import complete_intersect_multipolygons
>>> (complete_intersect_multipolygons(
...      Multipolygon([Polygon(first_square, []), Polygon(third_square, [])]),
...      Multipolygon([Polygon(second_square, []),
...                    Polygon(fourth_square, [])]))
...  == Multisegment([Segment(Point(0, 1), Point(1, 1)),
...                   Segment(Point(1, 0), Point(1, 1)),
...                   Segment(Point(1, 1), Point(2, 1)),
...                   Segment(Point(1, 1), Point(1, 2))]))
True
>>> (complete_intersect_multipolygons(
...      Multipolygon([Polygon(first_square, []), Polygon(third_square, [])]),
...      Multipolygon([Polygon(first_square, []), Polygon(third_square, [])]))
...  == Multipolygon([Polygon(first_square, []), Polygon(third_square, [])]))
True
>>> from clipping.planar import unite_multipolygons
>>> (unite_multipolygons(Multipolygon([Polygon(first_square, []),
...                                    Polygon(third_square, [])]),
...                      Multipolygon([Polygon(second_square, []),
...                                    Polygon(fourth_square, [])]))
...  == Polygon(Contour([Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)]),
...             []))
True
>>> (unite_multipolygons(Multipolygon([Polygon(first_square, []),
...                                    Polygon(third_square, [])]),
...                      Multipolygon([Polygon(first_square, []),
...                                    Polygon(third_square, [])]))
...  == Multipolygon([Polygon(first_square, []), Polygon(third_square, [])]))
True
>>> from clipping.planar import subtract_multipolygons
>>> (subtract_multipolygons(Multipolygon([Polygon(first_square, []),
...                                       Polygon(third_square, [])]),
...                         Multipolygon([Polygon(first_square, []),
...                                       Polygon(third_square, [])]))
...  is EMPTY)
True
>>> (subtract_multipolygons(Multipolygon([Polygon(first_square, []),
...                                       Polygon(third_square, [])]),
...                         Multipolygon([Polygon(second_square, []),
...                                       Polygon(fourth_square, [])]))
...  == Multipolygon([Polygon(first_square, []), Polygon(third_square, [])]))
True
>>> from clipping.planar import symmetric_subtract_multipolygons
>>> (symmetric_subtract_multipolygons(
...      Multipolygon([Polygon(first_square, []), Polygon(third_square, [])]),
...      Multipolygon([Polygon(first_square, []), Polygon(third_square, [])]))
...  is EMPTY)
True
>>> (symmetric_subtract_multipolygons(
...      Multipolygon([Polygon(first_square, []), Polygon(third_square, [])]),
...      Multipolygon([Polygon(second_square, []),
...                    Polygon(fourth_square, [])]))
...  == Polygon(Contour([Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)]),
...             []))
True

```

Development
-----------

### Bumping version

#### Preparation

Install
[bump2version](https://github.com/c4urself/bump2version#installation).

#### Pre-release

Choose which version number category to bump following [semver
specification](http://semver.org/).

Test bumping version
```bash
bump2version --dry-run --verbose $CATEGORY
```

where `$CATEGORY` is the target version number category name, possible
values are `patch`/`minor`/`major`.

Bump version
```bash
bump2version --verbose $CATEGORY
```

This will set version to `major.minor.patch-alpha`. 

#### Release

Test bumping version
```bash
bump2version --dry-run --verbose release
```

Bump version
```bash
bump2version --verbose release
```

This will set version to `major.minor.patch`.

### Running tests

Install dependencies
```bash
python -m pip install -r requirements-tests.txt
```

Plain
```bash
pytest
```

Inside `Docker` container:
- with `CPython`
  ```bash
  docker-compose --file docker-compose.cpython.yml up
  ```
- with `PyPy`
  ```bash
  docker-compose --file docker-compose.pypy.yml up
  ```

`Bash` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```bash
  ./run-tests.sh
  ```
  or
  ```bash
  ./run-tests.sh cpython
  ```

- with `PyPy`
  ```bash
  ./run-tests.sh pypy
  ```

`PowerShell` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```powershell
  .\run-tests.ps1
  ```
  or
  ```powershell
  .\run-tests.ps1 cpython
  ```
- with `PyPy`
  ```powershell
  .\run-tests.ps1 pypy
  ```
