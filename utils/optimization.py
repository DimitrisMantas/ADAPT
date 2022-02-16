#  ADAPT is a Python program for the optimization of building energy
#  consumption and human comfort.
#          Copyright (C) 2021-2022 Dimitris Mantas
#
#          This program is free software: you can redistribute it and/or modify
#          it under the terms of the GNU General Public License as published by
#          the Free Software Foundation, either version 3 of the License, or
#          (at your option) any later version.
#
#          This program is distributed in the hope that it will be useful,
#          but WITHOUT ANY WARRANTY; without even the implied warranty of
#          MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#          GNU General Public License for more details.
#
#          You should have received a copy of the GNU General Public License
#          along with this program. If not, see <https://www.gnu.org/licenses/>.


import numpy as np
import numpy.typing as npt

import csv
import os
import pickle
from typing import Any, List, Union

import numpy as np

import utils.librarian


def _normalize_objective_space_results(_objective_space_results: npt.NDArray) -> npt.NDArray:
    """
    Normalize a non-dominated solution prefs using min-max feature scaling.

    ----------------
    Input Parameters
    ----------------

    objective_space_results: numpy.ndarray
        The non-dominated solution prefs to be normalized.
    """

    _normalized_objective_space_results = np.empty_like(_objective_space_results)

    for _i in range(np.shape(_objective_space_results)[1]):
        _objective_space_results_column = _objective_space_results[:, _i]

        _numerator = _objective_space_results_column - np.min(_objective_space_results_column)
        _denominator = np.max(_objective_space_results_column) - np.min(_objective_space_results_column)

        _normalized_objective_space_results[:, _i] = _numerator / _denominator

    return _normalized_objective_space_results


def close_bound(bound: npt.NDArray, decimals: int) -> npt.NDArray:
    """
    Close the sim problem bounds.

    The initial population sampling process for discontinuous sim variables is performed by uniformly
    sampling real-floating point numbers over half-open interval [a, b), a < b, where a and b are the lower and upper
    bounds of these variables, respectively, and then rounding them as required.

    However, since b is required to be a feasible design-space result, the aforementioned interval is closed by
    extending it by a predefined accuracy level, measured by the number of decimal places to which these numbers
    should be rounded.

    ----------------
    Input Parameters
    ----------------

    _xu: numpy.ndarray
        The upper sim variable bounds.

    _decimals: int
        The accuracy level, to which the initial population sampling process should be performed, measured by the
        number of decimal places to which the sampled real floating-point numbers should be rounded.
    """

    return bound + (10 ** -decimals)


def read_problem_bounds(path: str) -> List[Union[int, float]]:
    """Read the sim problem bounds from a givem .CSV file."""

    with open(path, "r") as file:
        reader = csv.reader(file)

        data = []
        for row in reader:
            data.append(row)

    return np.array(data, dtype="f")
