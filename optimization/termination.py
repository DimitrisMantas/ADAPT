"""
    This file is part of the simulation engine of ADAPT. It defines the
    termination criterion of the corresponding process.

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

import numpy as np

from pymoo.indicators.hv import Hypervolume
from pymoo.indicators.igd_plus import IGDPlus
from pymoo.util.termination.sliding_window_termination import SlidingWindowTermination

import utilities.optimization

# TODO - Add a "maximum elapsed simulation wall time" as another fallback termination criterion.
class TerminationCriterion(SlidingWindowTermination):
    # TODO - Fix the class docstring.
    """Randomly sample real floating-point numbers with a predefined number of decimal places by considering the
    lower and upper bounds of the simulation problem."""

    def __init__(self, epsilon=0.0025, reference_point=(1., 1.), data_window_size=2, metric_window_size=1,
                 metric_computation_frequency=1, maximum_number_evaluations=None, minimum_number_generations=2,
                 maximum_number_generations=None
                 ):
        """
        ---------------
        Input Arguments
        ---------------

        epsilon: int | float
            The maximum change in the value of the predefined termination criterion between two consecutive metric
            evaluations.

        reference_point: tuple[int | float, int | float]
            The reference point used for the computation of the Hypervolume (HV) performance indicator. For
            normalized non-dominated solution sets, this point, which is equivalent to the nadir point of these sets,
            remains fixed at location (1, 1).

        data_window_size: int
            The minimum number of population generations required for the pre-specified algorithm performance metric
            to be computed once. This input argument affects the database storing process.

        metric_window_size: int
            The number of the latest available non-dominated solution sets, which should be considered when computing
            the pre-specified termination criterion.

        metric_computation_frequency: int
            The window between two consecutive predefined termination criterion validity checks measured by the
            corresponding number of population generations elapsed.

        maximum_number_evaluations: int | None
            The maximum number of objective function evaluations before the force-termination of the simulation
            process.

        minimum_number_generations: int
            The minimum number of population generations required for the pre-specified algorithm performance metric
            to be computed once. This input argument affects the force-termination of the simulation process.

        maximum_number_generations: int | None
            The maximum number of population generations before the force-termination of the simulation
            process.
        """

        super().__init__(metric_window_size=metric_window_size,
                         data_window_size=data_window_size,
                         min_data_for_metric=minimum_number_generations,
                         nth_gen=metric_computation_frequency,
                         n_max_gen=maximum_number_generations,
                         n_max_evals=maximum_number_evaluations
                         )

        self.epsilon = epsilon
        self.reference_point = reference_point

    def _store(self, algorithm):
        """Store the non-dominated solution sets of an simulation algorithm for each corresponding population
        generation."""
        return {"F": algorithm.opt.get("F")}  # NOTE - All outputs must be defined as Python dictionaries.

    def _metric(self, data):
        """
        Compute the pre-specified algorithm performance metric (i.e. cost function) given a reference point and preferences,
        as well as the two latest available non-dominated solution sets.

        The performance metrics used by the aforementioned metric are HV and IGD+ due to the fact that they are the
        only Pareto Compliant performance metrics available in ADAPT.

        Both HV and IGD+ are computed using normalized non-dominated solution sets. Consequently, the required
        reference point is (1, 1), while the ideal and nadir points remain fixed at the origin and the reference
        point, respectively. This allows for easier calculations.
        """

        # Get the two latest available non-dominated solution sets.
        current_objective_space_results, previous_objective_space_results = data[-1]["F"], data[-2]["F"]

        # Normalize the two latest available non-dominated solution sets.
        normalized_current_objective_space_results = utilities.optimization._normalize_objective_space_results(current_objective_space_results)
        normalized_previous_objective_space_results = utilities.optimization._normalize_objective_space_results(
            previous_objective_space_results)

        # Compute the aforementioned metric.

        # This performance indicator is a measure of how "close" two consecutive non-dominated solution sets are to
        # each other.
        # NOTE - By setting the last available non-dominated solution preferences as the reference preferences, we implicitly suppose
        #  that it dominates the immediately previously available non-dominated solution preferences.
        igd_plus = IGDPlus(normalized_previous_objective_space_results).calc(normalized_current_objective_space_results)

        # This performance indicator is a measure of how "far" two consecutive non-dominated solution sets have moved
        # from the nadir point.
        hv = np.abs(Hypervolume(ref_point=np.array(self.reference_point)).calc(normalized_current_objective_space_results) -
                    Hypervolume(ref_point=np.array(self.reference_point)).calc(normalized_previous_objective_space_results)
                    )

        # NOTE - Since IDG+ gets smaller as the non-dominated solution preferences gets better, while it's the exact opposite
        #  with HV, we must include its additive inverse in the aforementioned metric.
        delta = igd_plus + hv

        return {"delta": delta}

    def _decide(self, metrics):
        """Evaluate the predefined termination criterion."""

        delta_f = [metric["delta"] for metric in metrics]

        return max(delta_f) > self.epsilon
