"""
    This file is part of the sim engine of ADAPT. It defines the
    input parameters of the corresponding algorithm.

    Copyright (C) 2021-2022
        Dimitris Mantas, MEng (s)

        Department of Civil Engineering
        School of Engineering
        University of Patras

        A: University Campus, Rio, Achaia, 265 04, Greece
        E: d.mantas@g.upatras.gr | d.mantas@upnet.gr
        T: +30 698 995 8826

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

#  ADAPT is a Python program for the opt of building energy
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

from pymoo.core.crossover import Crossover
from pymoo.core.duplicate import ElementwiseDuplicateElimination

from pymoo.core.mutation import Mutation

from pymoo.core.sampling import Sampling
from pymoo.operators.repair.to_bound import set_to_bounds_if_outside_by_problem

from prefs.parameters import parameters


class SamplingScheme(Sampling):
    """Uniformly sample real floating-point numbers with a predefined number of decimal places by considering the
    lower and upper bounds of the sim problem."""

    def __init__(self, decimals=parameters["SAMPLING_DECIMALS"]) -> None:
        """
        ----------------
        Input Parameters
        ----------------

        decimals: int
            The accuracy level, to which the initial population sampling process should be performed, measured by the
            number of decimal places to which the sampled real floating-point numbers should be rounded.
        """

        super().__init__()

        self.decimals = decimals

    def _do(self, problem, n_samples, **kwargs):
        # TODO - Fix the method docstring.
        """Uniformly sample real floating-point numbers with a predefined number of decimal places by considering the
        lower and upper bounds of the sim problem."""

        # Initialize NumPy's recommended RNG.
        rng = np.random.default_rng(seed=parameters["SEED"])

        # Sample the initial population from a uniform distribution.
        samples = rng.uniform(problem.xl, problem.xu, (n_samples, problem.n_var))

        # TODO - IMPLEMENT THIS LATER.
        # # Round the samples to the predefined number of decimal places.
        # samples = np.round(samples, self.decimals)

        return samples


class CrossoverScheme(Crossover):
    def __init__(self, eta, n_offsprings=2, prob_per_variable=0.5, **kwargs):
        super().__init__(2, n_offsprings, **kwargs)
        self.eta = float(eta)
        self.prob_per_variable = prob_per_variable

    def _do(self, problem, X, **kwargs):

        X = X.astype(float)
        _, n_matings, n_var = X.shape

        # boundaries of the problem
        xl, xu = problem.xl, problem.xu

        #if np.any(X < xl) or np.any(X > xu):
        #    raise Exception("Simulated binary crossover requires all variables to be in bounds!")

        # crossover mask that will be used in the end
        do_crossover = np.full(X[0].shape, True)

        # per variable the probability is then 50%
        do_crossover[np.random.random((n_matings, problem.n_var)) > self.prob_per_variable] = False
        # also if values are too close no mating is done
        do_crossover[np.abs(X[0] - X[1]) <= 1.0e-14] = False

        # assign y1 the smaller and y2 the larger value
        y1 = np.min(X, axis=0)
        y2 = np.max(X, axis=0)

        # random values for each individual
        rand = np.random.random((n_matings, problem.n_var))

        def calc_betaq(beta):
            # print(f"{beta=}")
            # print(f"{self.eta=}")
            alpha = 2.0 - np.power(beta, -(self.eta + 1.0))
            # print(f"{alpha=}")

            mask, mask_not = (rand <= (1.0 / alpha)), (rand > (1.0 / alpha))

            betaq = np.zeros(mask.shape)
            betaq[mask] = np.power((rand * alpha), (1.0 / (self.eta + 1.0)))[mask]
            betaq[mask_not] = np.power((1.0 / (2.0 - rand * alpha)), (1.0 / (self.eta + 1.0)))[mask_not]

            return betaq

        # difference between all variables
        delta = (y2 - y1)

        # now just be sure not dividing by zero (these cases will be filtered later anyway)
        # delta[np.logical_or(delta < 1.0e-10, np.logical_not(do_crossover))] = 1.0e-10
        delta[delta < 1.0e-10] = 1.0e-10

        beta = 1.0 + (2.0 * (y1 - xl) / delta)
        betaq = calc_betaq(beta)
        c1 = 0.5 * ((y1 + y2) - betaq * delta)

        beta = 1.0 + (2.0 * (xu - y2) / delta)
        betaq = calc_betaq(beta)
        c2 = 0.5 * ((y1 + y2) + betaq * delta)

        # do randomly a swap of variables
        b = np.random.random((n_matings, problem.n_var)) <= 0.5
        val = np.copy(c1[b])
        c1[b] = c2[b]
        c2[b] = val

        # take the parents as _template
        c = np.copy(X)

        # copy the positions where the crossover was done
        c[0, do_crossover] = c1[do_crossover]
        c[1, do_crossover] = c2[do_crossover]

        c[0] = set_to_bounds_if_outside_by_problem(problem, c[0])
        c[1] = set_to_bounds_if_outside_by_problem(problem, c[1])

        if self.n_offsprings == 1:
            # Randomly select one offspring
            c = c[np.random.choice(2, X.shape[1]), np.arange(X.shape[1])]
            c = c.reshape((1, X.shape[1], X.shape[2]))

        return c


class MutationScheme(Mutation):
    def __init__(self, eta, prob=None):
        super().__init__()
        self.eta = float(eta)

        if prob is not None:
            self.prob = float(prob)
        else:
            self.prob = None

    def _do(self, problem, X, **kwargs):

        X = X.astype(float)
        Y = np.full(X.shape, np.inf)

        if self.prob is None:
            self.prob = 1.0 / problem.n_var

        do_mutation = np.random.random(X.shape) < self.prob

        Y[:, :] = X

        xl = np.repeat(problem.xl[None, :], X.shape[0], axis=0)[do_mutation]
        xu = np.repeat(problem.xu[None, :], X.shape[0], axis=0)[do_mutation]

        X = X[do_mutation]

        delta1 = (X - xl) / (xu - xl)
        delta2 = (xu - X) / (xu - xl)

        mut_pow = 1.0 / (self.eta + 1.0)

        rand = np.random.random(X.shape)
        mask = rand <= 0.5
        mask_not = np.logical_not(mask)

        deltaq = np.zeros(X.shape)

        xy = 1.0 - delta1
        val = 2.0 * rand + (1.0 - 2.0 * rand) * (np.power(xy, (self.eta + 1.0)))
        d = np.power(val, mut_pow) - 1.0
        deltaq[mask] = d[mask]

        xy = 1.0 - delta2
        val = 2.0 * (1.0 - rand) + 2.0 * (rand - 0.5) * (np.power(xy, (self.eta + 1.0)))
        d = 1.0 - (np.power(val, mut_pow))
        deltaq[mask_not] = d[mask_not]

        # mutated values
        _Y = X + deltaq * (xu - xl)

        # back in bounds if necessary (floating point issues)
        _Y[_Y < xl] = xl[_Y < xl]
        _Y[_Y > xu] = xu[_Y > xu]

        # prefs the values for out
        Y[do_mutation] = _Y

        # in case out of bounds repair (very unlikely)
        Y = set_to_bounds_if_outside_by_problem(problem, Y)

        return Y


class DuplicateEliminationScheme(ElementwiseDuplicateElimination):
    pass