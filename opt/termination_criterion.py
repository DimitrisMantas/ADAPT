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

import rolling_window


class TerminationCriterion(rolling_window.RollingWindow):

    def __init__(self,
                 n_last=20,
                 tol=1,
                 mode="medium",
                 n_max_gen=None,  # None sets it equal to the IEEE 754 32-bit limit.
                 n_max_evals=None,
                 max_time=None
                 ) -> None:
        super().__init__(metric_window_size=n_last,
                         n_max_gen=n_max_gen,
                         n_max_evals=n_max_evals,
                         max_time=max_time)
        self.tol = tol
        self.mode = mode

    def _store(self, algorithm):
        return algorithm.pop.get("X")

    def _metric(self, data):
        input_argument = np.abs(data[-1] - data[-2])
        if self.mode.lower() == "soft" or self.mode.lower() == "medium":
            return np.mean(input_argument)
        elif self.mode.lower() == "hard":
            return np.max(input_argument)
        else:
            raise NameError("The termination criterion mode must be set to either soft, medium, or hard.")

    def _decide(self, metrics):
        if self.mode.lower() == "soft":
            comparison_argument = np.mean(metrics)
        elif self.mode.lower() == "medium" or self.mode.lower() == "hard":
            comparison_argument = np.max(metrics)
        else:
            raise NameError("The termination criterion mode must be set to either soft, medium, or hard.")

        return comparison_argument > self.tol
