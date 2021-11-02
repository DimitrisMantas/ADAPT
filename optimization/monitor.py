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

        self.metric_window_size=20
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