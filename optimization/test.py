from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.factory import get_problem
from pymoo.optimize import minimize
from pymoo.util.termination.x_tol import DesignSpaceToleranceTermination
from pymoo.visualization.scatter import Scatter

import termination

problem = get_problem("zdt3")
algorithm = NSGA2(pop_size=100)
# termination = termination.TerminationCriterion2(tol=0.0025, n_last=20)
termination = termination.TerminationCriterion1(epsilon=0.01, metric_window_size=20)

res = minimize(problem,
               algorithm,
               termination,
               pf=True,
               seed=1,
               verbose=False)

print("Generations", res.algorithm.n_gen)
plot = Scatter(title="ZDT3")
plot.add(problem.pareto_front(use_cache=False, flatten=False), plot_type="line", color="black")
plot.add(res.F, facecolor="none", edgecolor="red", alpha=0.8, s=20)
plot.show()