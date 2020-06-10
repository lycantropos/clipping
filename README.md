clipping
========

[![](https://travis-ci.com/lycantropos/clipping.svg?branch=master)](https://travis-ci.com/lycantropos/clipping "Travis CI")
[![](https://dev.azure.com/lycantropos/clipping/_apis/build/status/lycantropos.clipping?branchName=master)](https://dev.azure.com/lycantropos/clipping/_build/latest?definitionId=21&branchName=master "Azure Pipelines")
[![](https://readthedocs.org/projects/clip/badge/?version=latest)](https://clip.readthedocs.io/en/latest "Documentation")
[![](https://codecov.io/gh/lycantropos/clipping/branch/master/graph/badge.svg)](https://codecov.io/gh/lycantropos/clipping "Codecov")
[![](https://img.shields.io/github/license/lycantropos/clipping.svg)](https://github.com/lycantropos/clipping/blob/master/LICENSE "License")
[![](https://badge.fury.io/py/clipping.svg)](https://badge.fury.io/py/clipping "PyPI")

In what follows
- `python` is an alias for `python3.5` or any later
version (`python3.6` and so on),
- `pypy` is an alias for `pypy3.5` or any later
version (`pypy3.6` and so on).

Installation
------------

Install the latest `pip` & `setuptools` packages versions:
- with `CPython`
  ```bash
  python -m pip install --upgrade pip setuptools
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --upgrade pip setuptools
  ```

### User

Download and install the latest stable version from `PyPI` repository:
- with `CPython`
  ```bash
  python -m pip install --upgrade clipping
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --upgrade clipping
  ```

### Developer

Download the latest version from `GitHub` repository
```bash
git clone https://github.com/lycantropos/clipping.git
cd clipping
```

Install dependencies:
- with `CPython`
  ```bash
  python -m pip install --force-reinstall -r requirements.txt
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --force-reinstall -r requirements.txt
  ```

Install:
- with `CPython`
  ```bash
  python setup.py install
  ```
- with `PyPy`
  ```bash
  pypy setup.py install
  ```

Usage
-----
```python
>>> left_edge = ((0, 0), (0, 1))
>>> right_edge = ((1, 0), (1, 1))
>>> bottom_edge = ((0, 0), (1, 0))
>>> top_edge = ((0, 1), (1, 1))
>>> main_diagonal = ((0, 0), (1, 1))
>>> trident = [left_edge, main_diagonal, bottom_edge]
>>> square_edges = [bottom_edge, right_edge, top_edge, left_edge]
>>> from clipping.planar import intersect_multisegments
>>> (intersect_multisegments(trident, square_edges)
...  == intersect_multisegments(square_edges, trident)
...  == [left_edge, bottom_edge])
True
>>> from clipping.planar import complete_intersect_multisegments
>>> (complete_intersect_multisegments(trident, square_edges)
...  == complete_intersect_multisegments(square_edges, trident)
...  == ([(1, 1)], intersect_multisegments(trident, square_edges), []))
True
>>> from clipping.planar import unite_multisegments
>>> (unite_multisegments(trident, square_edges)
...  == unite_multisegments(square_edges, trident)
...  == [left_edge, bottom_edge, main_diagonal, top_edge, right_edge])
True
>>> from clipping.planar import subtract_multisegments
>>> subtract_multisegments(trident, square_edges) == [main_diagonal]
True
>>> subtract_multisegments(square_edges, trident) == [top_edge, right_edge]
True
>>> from clipping.planar import symmetric_subtract_multisegments
>>> (symmetric_subtract_multisegments(trident, square_edges)
...  == symmetric_subtract_multisegments(square_edges, trident)
...  == [main_diagonal, top_edge, right_edge])
True
>>> left_triangle = [([(0, 0), (1, 0), (0, 1)], [])]
>>> right_triangle = [([(0, 1), (1, 0), (1, 1)], [])]
>>> square = [([(0, 0), (1, 0), (1, 1), (0, 1)], [])]
>>> from clipping.planar import intersect_multipolygons
>>> all(intersect_multipolygons(square, triangle)
...     == intersect_multipolygons(triangle, square) == triangle
...     for triangle in (left_triangle, right_triangle))
True
>>> intersect_multipolygons(left_triangle, right_triangle) == []
True
>>> from clipping.planar import complete_intersect_multipolygons
>>> all(complete_intersect_multipolygons(square, triangle)
...     == ([], [], intersect_multipolygons(square, triangle))
...     for triangle in (left_triangle, right_triangle))
True
>>> (complete_intersect_multipolygons(left_triangle, right_triangle)
...  == ([], [((0, 1), (1, 0))], []))
True
>>> from clipping.planar import unite_multipolygons
>>> all(unite_multipolygons(square, triangle)
...     == unite_multipolygons(triangle, square)
...     == square
...     for triangle in (left_triangle, right_triangle))
True
>>> (unite_multipolygons(left_triangle, right_triangle)
...  == unite_multipolygons(right_triangle, left_triangle)
...  == square)
True
>>> from clipping.planar import subtract_multipolygons
>>> all(subtract_multipolygons(triangle, square) == []
...     for triangle in (left_triangle, right_triangle))
True
>>> subtract_multipolygons(square, left_triangle) == right_triangle
True
>>> subtract_multipolygons(square, right_triangle) == left_triangle
True
>>> from clipping.planar import symmetric_subtract_multipolygons
>>> symmetric_subtract_multipolygons(left_triangle, right_triangle) == square
True
>>> symmetric_subtract_multipolygons(square, left_triangle) == right_triangle
True
>>> symmetric_subtract_multipolygons(square, right_triangle) == left_triangle
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

Install dependencies:
- with `CPython`
  ```bash
  python -m pip install --force-reinstall -r requirements-tests.txt
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --force-reinstall -r requirements-tests.txt
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
