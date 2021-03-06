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

from abc import abstractmethod

from pymoo.util.sliding_window import SlidingWindow
from pymoo.util.termination.collection import TerminationCollection
from pymoo.util.termination.max_eval import MaximumFunctionCallTermination
from pymoo.util.termination.max_gen import MaximumGenerationTermination

import max_wall_time


class RollingWindow(TerminationCollection):

    def __init__(self,
                 metric_window_size=None,
                 data_window_size=2,
                 min_data_for_metric=2,
                 nth_gen=1,
                 n_max_gen=None,
                 n_max_evals=None,
                 max_time=None,
                 truncate_metrics=True,
                 truncate_data=True,
                 ) -> None:
        """

        Parameters
        ----------

        metric_window_size : int
            The last generations that should be considering during the calculations

        data_window_size : int
            How much of the history should be kept in memory based on a sliding window.

        nth_gen : int
            Each n-th generation the termination should be checked for

        """

        super().__init__(MaximumGenerationTermination(n_max_gen=n_max_gen),
                         MaximumFunctionCallTermination(n_max_evals=n_max_evals),
                         max_wall_time.MaxWallTime(max_time=max_time))

        # the window sizes stored in objects
        self.data_window_size = data_window_size
        self.metric_window_size = metric_window_size

        # the obtained data at each iteration
        self.data = SlidingWindow(data_window_size) if truncate_data else []

        # the metrics calculated also in a sliding window
        self.metrics = SlidingWindow(metric_window_size) if truncate_metrics else []

        # each n-th generation the termination decides whether to terminate or not
        self.nth_gen = nth_gen

        # number of entries of data need to be stored to calculate the metric at all
        self.min_data_for_metric = min_data_for_metric

    def _do_continue(self, algorithm):

        # if the maximum generation or maximum evaluations say terminated -> do so
        if not super()._do_continue(algorithm):
            return False

        # store the data decided to be used by the implementation
        obj = self._store(algorithm)
        if obj is not None:
            self.data.append(obj)

        # if enough data has be stored to calculate the metric
        if len(self.data) >= self.min_data_for_metric:
            metric = self._metric(self.data[-self.data_window_size:])
            if metric is not None:
                self.metrics.append(metric)

        # if its the n-th generation and enough metrics have been calculated make the decision
        if algorithm.n_gen % self.nth_gen == 0 and len(self.metrics) >= self.metric_window_size:

            # ask the implementation whether to terminate or not
            return self._decide(self.metrics[-self.metric_window_size:])

        # otherwise by default just continue
        else:
            return True

    # given an algorithm object decide what should be stored as historical information - by default just opt
    @abstractmethod
    def _store(self, algorithm):
        pass

    @abstractmethod
    def _metric(self, data):
        pass

    def get_metric(self):
        if len(self.metrics) > 0:
            return self.metrics[-1]
        else:
            return None

    @abstractmethod
    def _decide(self, metrics):
        pass
