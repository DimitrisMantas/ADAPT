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
from pymoo.util.display import Display
from pymoo.util.display import Output


class OutputSettings(Output):
    def __init__(self):
        super(OutputSettings, self).__init__()

    def format_float(self, number, width):
        format_str = "{:"+ str(width) + ".2f}"
        return format_str.format(number)  # TODO - Replace 2 with preferred decimals from PARAMS.



class ConvergenceMonitor(Display):

    def __init__(self):
        super().__init__()


        self.output = OutputSettings()

        self.metric_window_size=21 # The first generation cannot be compared to anything, so we need 20 + 1 = 21 generations for 20 pairs.
        self.min_generations = 2

    def _do(self, problem, evaluator, algorithm):
        self.output.append("Generation", algorithm.n_gen)
        self.output.append("Total Simulations", evaluator.n_eval, width=18)
        self.output.append("Mean PPD (%)", np.mean(algorithm.pop.get("F")[:, 0]))
        self.output.append("Mean NSE (kWh)", np.mean(algorithm.pop.get("F")[:, 1]), width=15)

        # TODO - Tidy this block up a bit.
        data = algorithm.pop.get("X")
        if algorithm.n_gen >= self.min_generations and algorithm.n_gen % self.metric_window_size == 0:
            output_str = self.output.format_float(np.mean(np.abs(data[-1] - data[-2])), self.output.default_width) + " -- CHECK"
        elif algorithm.n_gen >= self.min_generations:
            output_str = self.output.format_float(np.mean(np.abs(data[-1] - data[-2])), self.output.default_width)
        else:
            output_str = "N/A"

        self.output.append("Termination Metric", output_str)