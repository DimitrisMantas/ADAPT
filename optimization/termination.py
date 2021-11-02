import time

import numpy as np
from pymoo.indicators.igd import IGD
from pymoo.util.misc import time_to_int
from pymoo.util.termination.sliding_window_termination import SlidingWindowTermination


class TerminationCriterion1(SlidingWindowTermination):
    """
    Parameters
    ----------
    metric_window_size: int
        The number of generations that should be included in the required calculations. The optimization process will
        not conclude before this time, unless the maximum run time criterion is validated first.
    epsilon: int | float
        The maximum allowed difference between two consecutive schedules. Measured in schedule units.
    calculation_frequency: int
        The frequency with which the required calculations should be performed. Measured in number of generations.
    max_generations: int
        The maximum allowed number of generations.
    max_simulations: int
        The maximum allowed number of simulations.
    max_runtime: int
        The maximum allowed run time.
    """

    def __init__(self,
                 # Set the sliding window criterion.
                 metric_window_size=20,
                 epsilon=0.001,
                 calculation_frequency=1,

                 # Set the maximum number of generations.
                 max_generations=5000,

                 # Set the maximum number of simulations.
                 max_simulations=500000,

                 # Set the maximum runtime.
                 max_runtime="23:59:59",
                 **kwargs):

        super().__init__(metric_window_size=metric_window_size,
                         data_window_size=2,
                         min_data_for_metric=2,
                         nth_gen=calculation_frequency,
                         n_max_gen=max_generations,
                         n_max_evals=max_simulations,
                         **kwargs)
        self.epsilon = epsilon
        self.start_time = None
        self.check_time = None

        if isinstance(max_runtime, str):
            self.max_runtime = time_to_int(max_runtime)
        elif isinstance(max_runtime, int) or isinstance(max_runtime, float):
            self.max_runtime = max_runtime
        else:
            raise Exception("Either provide the time as a string or an integer.")

    def _do_continue(self, algorithm):

        self.check_time = time.time()

        # This block checks the current number of generations and simulations. Since it takes some time, the run time
        # criterion will be checked using the time before it starts.
        if not super()._do_continue(algorithm):
            return False

        # This block check total run time.
        if self.start_time is None:
            self.start_time = algorithm.start_time
        return self.check_time - self.start_time < self.max_runtime

    def _store(self, algorithm):
        return algorithm.pop.get("X")

    def _metric(self, data):
        # print("ADAPT = {}".format(np.mean(np.abs(data[-1] - data[-2]))))
        # print("pymoo = {}".format(IGD(data[-1]).do(data[-2])))
        return np.mean(np.abs(data[-1] - data[-2]))
        # return IGD(data[-1]).do(data[-2])

    def _decide(self, metrics):
        return np.mean(metrics) > self.epsilon

import numpy as np

from pymoo.indicators.igd import IGD
from pymoo.util.misc import to_numpy
from pymoo.util.normalization import normalize
from pymoo.util.termination.sliding_window_termination import SlidingWindowTermination


class TerminationCriterion2(SlidingWindowTermination):

    def __init__(self,
                 n_last=20,
                 tol=1e-6,
                 nth_gen=1,
                 n_max_gen=None,
                 n_max_evals=None,
                 **kwargs):

        super().__init__(metric_window_size=n_last,
                         data_window_size=2,
                         min_data_for_metric=2,
                         nth_gen=nth_gen,
                         n_max_gen=n_max_gen,
                         n_max_evals=n_max_evals,
                         **kwargs)
        self.tol = tol

    def _store(self, algorithm):
        # problem = algorithm.problem
        # X = algorithm.opt.get("X")
        #
        # if X.dtype != object:
        #     if problem.xl is not None and problem.xu is not None:
        #         X = normalize(X, xl=problem.xl, xu=problem.xu)
        #     return X
        return algorithm.pop.get("X")

    def _metric(self, data):
        last, current = data[-2], data[-1]
        return IGD(current).do(last)

    def _decide(self, metrics):
        return np.mean(metrics) > self.tol
