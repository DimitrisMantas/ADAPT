from pymoo.core.callback import Callback


class ConvergenceCallback(Callback):

    def __init__(self) -> None:

        super().__init__()
        self.F = []
        self.X = []

    def notify(self, algorithm):
        self.F.append(algorithm.pop.get("F"))
        self.X.append(algorithm.pop.get("X"))
