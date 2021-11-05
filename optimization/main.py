#      This program is part of ADAPT.
#
#      You should have received this program as part of its parent software
#      package.  If not, see <https://www.github.com/DimitrisMantas/ADAPT>.
#
#      Copyright (C) 2021
#
#          Dimitris Mantas
#          Senior Undergraduate Student
#
#          Department of Civil Engineering
#          School of Engineering
#          University of Patras
#
#          A: University Campus, Rio, Achaia, 265 04, Greece
#          Ε: dimitris.mantas@outlook.com
#          Τ: +30 698 995 8826
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.


import math
import os
import warnings

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

import numpy as np
import pandas as pd

from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2

from pymoo.optimize import minimize
from pymoo.factory import get_performance_indicator
from pymoo.factory import get_decomposition
from pymoo.factory import get_decision_making

import algorithm
import callback
import monitor
import termination_criterion

import preferences.colors
import preferences.parameters

import simulation.runner
import simulation.modifier
import simulation.reader

import utilities.librarian
import utilities.optimization


class OptimizationProblem(ElementwiseProblem):
    """Formulate the simulation problem."""

    def __init__(self, decimals=preferences.parameters.parameters["SAMPLING_DECIMALS"]):
        """..."""

        variable_bounds = utilities.optimization.read_problem_bounds(
            "../database/optimization/model/variable_bounds.csv")

        # The number of design space variables depends on the simulation unit time.
        super().__init__(n_var=48, n_obj=2, xl=variable_bounds[0],
                         xu=utilities.optimization.close_bound(variable_bounds[1], decimals=decimals))

    def _evaluate(self, x, out, *args, **kwargs):
        """..."""

        # Heating Schedule
        simulation.modifier.modify_schedule(x[00:24], "../database/simulation/model/ASHRAE901_OfficeMedium_STD2019_Tucson.idf", 29)

        # Cooling Schedule
        simulation.modifier.modify_schedule(x[24:48], "../database/simulation/model/ASHRAE901_OfficeMedium_STD2019_Tucson.idf", 36)

        # Simulation Controller
        simulation.runner.run_eplus("../database/simulation/model/ASHRAE901_OfficeMedium_STD2019_Tucson.idf",
                                        "../database/simulation/model/USA_AZ_Tucson-Davis-Monthan.AFB.722745_TMY3.epw",
                                        set_idd=False)

        # Objectives
        nse = simulation.reader.read_nse()
        ppd = simulation.reader.read_ppd()

        out["F"] = [ppd, nse]


optimization_problem = OptimizationProblem()

optimization_algorithm = NSGA2(pop_size=100,
                               sampling=algorithm.SamplingScheme(),
                               # NOTE - Check the parent population selection process.
                               crossover=algorithm.CrossoverScheme(
                                   eta=preferences.parameters.parameters["CROSSOVER_ETA"],
                                   prob=preferences.parameters.parameters["CROSSOVER_PROBABILITY"]),
                               mutation=algorithm.MutationScheme(eta=preferences.parameters.parameters["MUTATION_ETA"]),
                               # NOTE - Check the population survival selection process.
                               eliminate_duplicates=True
                               )


# The termination criterion is checked against before each new generation. It cannot be checked againts before the
# whole population is evaluated, so the smallest input arguments it can take are: (i) n_max_gen = 1, (ii) n_max_evals
# = pop_size, and (iii) max_time = pop_size * mean (or max) simulation time.

# Similarly, the possible values of those input arguments are: (i) n_max_gen = k, where k is an integer,
# (ii) n_max_evals = k * pop_size, and (iii) max_time = k * pop_size * mean (or max) simulation time.

# Other values are also valid, but may yield unexpected results. For example, when pop_size = 100 and n_max_evals =
# 150, then the optimization will stop after the evaluation of the second generation is finished.

termination_criterion = termination_criterion.TerminationCriterion(tol=2)

convergence_callback = callback.ConvergenceCallback()

res = minimize(optimization_problem, optimization_algorithm, termination_criterion, callback=convergence_callback,
               seed=preferences.parameters.parameters["SEED"], display=monitor.ConvergenceMonitor(), verbose=True)


# API USAGE EXAMPLE
if __name__ == "__main__":
    exec_time = res.exec_time
    n_gen = res.algorithm.n_gen
    print("OPTIMIZATION WALL TIME =\n" + "{}".format(exec_time))
    print("GENERATIONS =\n" + "{}".format(n_gen))
    print(np.shape(res.F)[0])  # onvg


########################################################################################################################


# STEP 08 - ASSESS THE PERFORMANCE OF THE OPTIMIZATION ALGORITHM - DONE


def algorithm_performance(objective_space_results, reference_point=(1., 1.), reference_set=None,
                                              extreme_solutions=None
                                              ):
    """Assess the performance of the simulation algorithm using various relevant metrics."""

    # NO COMPARISON

    # NOTE - The OVERALL NON-DOMINATED VECTOR GENERATION (ONVG) performance indicator refers to the cardinality of
    #  the non-dominated solution preferences and needs to be maximized.
    onvg = np.shape(objective_space_results)[0]

    # Build the reference preferences (i.e. the the X- and Y- axes for the normalized solution preferences).
    if reference_set is None:
        # Calculate the number of points per axis.
        num_points = int(0.5 * onvg)

        # Calculate the variable component of the required point coordinates.
        point_coordinates = np.linspace(0., 1., num_points)

        x_axis = np.column_stack([point_coordinates, np.zeros(num_points)])
        y_axis = np.column_stack([np.zeros(num_points), point_coordinates])

        # TODO - The origin is included twice. Check if this can cause a bug.
        # TODO - Does it matter of the solution preferences is not sorted?
        reference_set = np.row_stack([x_axis, y_axis])

        # NOTE - Check for shape match as a debugging tool. Remove this before final release.
        # NOTE - This will throw an error if the population size OR the total number of generations is an odd number.
        assert np.shape(reference_set) == np.shape(
            non_dominated_solutions), "The dimensions of the reference and the non-dominated solution sets do not match."

    # Normalize the the non-dominated solution preferences.
    normalized_objective_space_results = utilities.optimization._normalize_objective_space_results(
        objective_space_results)

    # COMPARISON TO REFERENCE POINT

    # NOTE - The HYPERVOLUME (HV) performance indicator refers to the area enclosed by the non-dominated solution preferences
    #  and a reference point in the feasible region, which is taken to be as "bad" as possible [i.e. (1, 1) for the
    #  normalized solution preferences] and needs to be maximized.
    hv = get_performance_indicator("hv", ref_point=np.array(reference_point)).do(normalized_objective_space_results)

    # COMPARISON TO A REFERENCE SET

    # NOTE - The GENERATIONAL DISTANCE (GD) performance indicator refers to the Euclidean distance between the
    #  non-dominated solution preferences and a reference point preferences, which is taken to be the actual Pareto Frontier [i.e.
    #  the X- and Y- axes for the normalized solution preferences] and needs to be minimized.
    gd = get_performance_indicator("gd", reference_set).do(normalized_objective_space_results)

    # NOTE - The INVERTED GENERATIONAL DISTANCE PLUS (IDG+) performance indicator refers to the inverted GD between
    #  the non-dominated solution preferences and a reference point preferences, which is taken to be the actual Pareto Frontier [
    #  i.e. the X- and Y- axes for the normalized solution preferences] and needs to be minimized.

    # NOTE - In contrast to IGD, IGD+ is weakly Pareto compliant, meaning that given two distinct non-dominated
    #  solutions sets A and B, if A < B, then IGD+(A) >= IGD+(B). This is property is essential if IDG+ is to be used
    #  a stopping criterion for the simulation process.

    igd_plus = get_performance_indicator("igd+", reference_set).do(normalized_objective_space_results)

    # NOTE - The DELTA (Δ OR Δ') performance indicator refers to the difference between the Euclidean distance
    #  between consecutive elements of the non-dominated solution preferences and the average of said distances while also
    #  taking its extents into account and needs to be minimized.

    def _delta(_objective_space_results=objective_space_results, _extreme_solutions=extreme_solutions, _onvg=onvg):
        """..."""

        # Sort the non-dominated solution preferences with respect to its X-axis coordinates.
        _sorted_objective_space_results = _objective_space_results[_objective_space_results[:, 0].argsort()]

        # Compute the lower and upper bounds of the non-dominated solution preferences.
        _lower_bound = _sorted_objective_space_results[0, :]
        _upper_bound = _sorted_objective_space_results[-1, :]

        # The extreme solutions (i.e. the boundary elements of the reference solution preferences) are arbitrarily taken to
        # be 25% "better" than the boundary elements of the non-dominated solution preferences.
        if _extreme_solutions is None:
            _padding = 0.25

            # Instantiate some commonly used intermediate variables for readability and speed.
            _add = 1. + _padding
            _sub = 1. - _padding

            # Calculate the extreme solutions.
            _extreme_solutions = ((_sub * _lower_bound[0], _add * _lower_bound[1]),
                                  (_add * _upper_bound[0], _sub * _upper_bound[1])
                                  )

        # Compute the Euclidean distances between the extreme solutions and the boundary elements of the
        # non-dominated solution preferences.
        _df = math.dist(_extreme_solutions[0], _lower_bound)
        _dl = math.dist(_extreme_solutions[1], _upper_bound)

        # Compute Euclidean distances between consecutive internal elements of the non-dominated solution preferences.
        _di = []
        for _i in range(onvg - 1):
            _di.append(math.dist(_sorted_objective_space_results[_i, :], _sorted_objective_space_results[_i + 1, :]))
        _di = np.array(_di)

        # Compute the mean corresponding distance.
        _dbar = np.mean(_di)

        # Compute the required sum term.
        _sum_term = np.sum(np.abs(_di - _dbar))

        return (_df + _dl + _sum_term) / (_df + _dl + (_onvg - 1) * _dbar)

    delta = _delta()

    local_variables = locals().copy()
    performance_indicators = ["delta", "gd", "hv", "igd_plus", "onvg"]

    return {i: local_variables[i] for i in performance_indicators}


# API USAGE EXAMPLE
if __name__ == "__main__":
    non_dominated_solutions = res.F

    # NOTE - THE ASSERTION ABOVE HAS RUINED A 2 HOUR RUN FOR NO REASON.
    # kpis = assess_optimization_algorithm_performance(non_dominated_solutions)
    # print("PERFORMANCE INDICATORS =\n" + "{}".format(kpis))


########################################################################################################################


# STEP 09 - CALCULATE THE OPTIMAL POINT OF THE PARETO FRONTIER - DONE


def recommend_point(objective_space_results, max_ppd=10.0):
    """
    Decompose the multi-objective simulation problem of BEC vs. owPPD and and estimate its optimal solution.

    Decompose the multi-objective simulation problem of BEC vs. owPPD, which is represented by its corresponding
    Pareto Frontier, by using the a priori method of formulating and solving an equivalent single-objective
    simulation problem such that its optimal solution is (i) also a non-dominated optimal solution to the initial
    problem and (ii) mathematically and objectively "optimal" with respect to an arbitrarily pre-specified criterion.

    # TODO - Confirm the maximum value of PPD in ISO 7730:2005.

    If owPPD(x) ≤ 15% (i.e. the maximum value recommended by ISO 7730:2005), then the optimal solution of the
    aforementioned single-objective simulation problem is equivalent to argmax(owPPD). However, in all other cases,
    the non-dominated solutions of the initial multi-objective simulation problem are (i) normalized using minimax
    feature scaling [1] to fit within the range [0, 1] and evaluated using the Achievement Scalarization Function
    (ASF) proposed by Wierzbicki [2].
    """
    # CASE 1: Build the corresponding difference matrix.
    diff = objective_space_results[:, 0] - max_ppd
    # CASE 1: Mask all values greater than 0% (i.e. owPPD > max_owPPD).
    mask = np.ma.greater(diff, 0)
    # If all values of the difference matrix need to be masked, then owPPD(x) > max_owPPD.
    if np.all(mask):
        warnings.warn(
            "owPPD(x) > {}%: Switching to Wierzbicki's ASF assuming equal simulation objective importance.".format(
                max_ppd))
        # CASE 2: Normalize the non-dominated solutions of the initial multi-objective simulation problem to fit
        # within the range [0, 1].

        normalized_objective_space_results = utilities.optimization._normalize_objective_space_results(
            objective_space_results)

        # CASE 2: This is a measure of how "important" each objective of the initial multi-objective simulation
        # problem is. Since, BEC and owPPD are of equal importance, their individual weights will be be preferences to 1.
        weights = np.array([1, 1])
        # Since the range of F is normalized to [0, 1], the default values, which result in the corresponding utopian
        # point being placed at the origin, are OK and we don't need to calculate it ourselves.
        return get_decomposition("asf").do(normalized_objective_space_results, weights).argmin()
    return np.ma.masked_array(diff, mask).argmax()


# API USAGE EXAMPLE
if __name__ == "__main__":
    # NOTE - The API accepts res.F and not res (more user-friendly) because pymoo performs scalarization and high
    #  trade-off area computation using indices. So, to get the actual output, you need to pas these indices to
    #  res.F and res.X, so you must already know what they are and how to use them.
    I0 = recommend_point(non_dominated_solutions)
    P0 = non_dominated_solutions[I0, :]
    print("OPTIMAL POINT - OBJECTIVE SPACE =\n" + "{}".format(P0))


########################################################################################################################


# STEP 10 - DECOMPOSE THE DESIGN SPACE RESULTS


def recommend_schedule(design_space_results, index):
    """Decompose the individual components of the input argument of BEC(x) for a given value of BEC."""
    return design_space_results[index, :]


# API USAGE EXAMPLE
if __name__ == "__main__":
    design_space_results = recommend_schedule(res.X, I0)
    print("OPTIMAL POINT - DESIGN SPACE =\n" + "{}".format(design_space_results))


########################################################################################################################


# STEP 11 - CALCULATE THE HIGH TRADE-OFF AREA OF THE PARETO FRONTIER


def calculate_high_tradeoff_area(objective_space_results):
    """Calculate the high-tradeoff area of the Pareto Frontier"""
    return get_decision_making("high-tradeoff").do(objective_space_results)


# API USAGE EXAMPLE
if __name__ == "__main__":
    # TODO - ZERO IDENTTIYI ERROR

    I1 = calculate_high_tradeoff_area(non_dominated_solutions)
    P1 = non_dominated_solutions[I1, :]
    print("HIGH TRADE-OFF AREA =\n" + "{}".format(P1))


########################################################################################################################


# STEP 12 - SAVE THE NON GRAPHICAL OUTPUT TO FILE

def write_logs(callback, decimals=preferences.parameters.parameters["OUTPUT_DECIMALS"], paths=None):
    """
    Write the objective and design space output for each generation to a CSV file for further manipulation.
    """

    # NOTE - This avoids a mutable default argument.
    if paths is None:
        paths = {"F": "../database/optimization/logs/objective_space.csv",
                 "X": "../database/optimization/logs/design_space.csv"
                 }

    # Instantiate two dataframes to store the design and objective space output per population generation.
    dataframe_F = pd.DataFrame()
    dataframe_X = pd.DataFrame()

    for i in range(len(callback.F)):
        # Add the design space output.
        # NOTE - That the index column represents each objective function evaluation.
        dataframe_F["Generation" + " " + str(i) + ": " + "owPPD"] = np.round(callback.F[i][:, 0], decimals)
        dataframe_F["Generation" + " " + str(i) + ": " + "NSE"] = np.round(callback.F[i][:, 1], decimals)

        # Add the objective space output.
        # NOTE - That the index column represents each objective function evaluation.
        for _i in range(len(callback.X[i][0,
                            :])):  # The first row of res.X MUST have the same number of columns as the rest of the rows. # NOTE - This means that each population generation must be of the same size.
            dataframe_X["Generation" + " " + str(i) + ": " + "X" + str(_i)] = np.round(callback.X[i][:, _i], decimals)

    # Write the required dataframes to CSV files.
    # TODO - Find a better way to write this.
    utilities.librarian.create_directory(os.path.split(paths["F"])[0])
    utilities.librarian.create_directory(os.path.split(paths["X"])[0])

    dataframe_F.to_csv(paths["F"], index_label="Evaluation")
    dataframe_X.to_csv(paths["X"], index_label="Evaluation")


def write_result(design_space_result, lookup_table, decimals=preferences.parameters.parameters["OUTPUT_DECIMALS"],
                 path="../database/optimization/output/schedules.csv"):
    """
    # TODO - Fix the function docstring.
    Write the design space output to a CSV file.

    The supplied database must be an iterable of iterables in the form of [StartIndex, StopIndex, Label],
    where StartIndex and LastIndex are the first and last (+1) values of a specific independent variable, respectively,
    and Label is said variable's given name (e.g. Heating Setpoints).

    Example Input

    [[00, 08, "HTGSETP (°C)"],
     [08, 16, "CLGSETP (°C)"]
    ]

    """

    # Instantiate the required dataframe.
    dataframe = pd.DataFrame()

    # Create the time column.
    # NOTE - This will return a timeseries starting from 01:00, up to 24:00, repeating every freq hours.
    dataframe["Time (HH:MM:SS)"] = pd.date_range("01:00", freq=preferences.parameters.parameters["DF_FREQ_STR"],
                                                 periods=24 / preferences.parameters.parameters["DF_FREQ_NUM"]).time

    # NOTE - The following procedure is repeated for each element of the supplemental database (i.e. each required database
    #  column).
    for i in range(len(lookup_table)):
        # The design space output can be thought of as a compressed version of the required column database. To
        # decompress this database, each "compressed" value must be repeated the appropriate amount of times,
        # such that the length of the decompressed column database is equal to the number of rows of the dataframe.
        # NOTE - All compressed values must be repeated an equal number of times.
        compressed_column_data = design_space_result[lookup_table[i][0]:lookup_table[i][1]]

        # Compute the required number of repeated values.
        repeats = int(len(dataframe) / (lookup_table[i][1] - lookup_table[i][0]))

        decompressed_column_data = np.repeat(compressed_column_data, repeats)

        # Append the decompressed column database to the dataframe with the appropriate label.
        dataframe[lookup_table[i][2]] = np.round(decompressed_column_data, decimals)

    # Write the required dataframe to a CSV file.
    utilities.librarian.create_directory(os.path.split(path)[0])
    dataframe.to_csv(path, index=False)


# API USAGE EXAMPLE
if __name__ == "__main__":
    write_logs(convergence_callback)

    supplemental_data = [[00, 24, "Heating Setpoint (°C)"],
                         [24, 48, "Cooling Setpoint (°C)"]
                         ]

    write_result(design_space_results, supplemental_data)


########################################################################################################################
#                                                  GRAPHICS ENGINE                                                     #
########################################################################################################################


# STEP 13 - INSTANTIATE THE FIGURE FOR THE GRAPHICAL OUTPUT - DONE


def instantiate_figure(figure_dimensions=(10, 10), axis_labels=(
"Fanger's Thermal Comfort Model: Occupancy-Weighted PPD (%)", "Net Site Energy Consumption (kWh)",
"Global Warming Potential (kg $\mathregular{CO_2eq}$)")):
    figure, main_axes = plt.subplots(constrained_layout=True, figsize=figure_dimensions)  # (W, H) in 10**2 pixels.

    main_axes.set_xlabel(axis_labels[0])
    main_axes.set_ylabel(axis_labels[1])

    secondary_axes = main_axes.twinx()
    secondary_axes.set_ylabel(axis_labels[2])

    return figure, main_axes, secondary_axes


# API USAGE EXAMPLE
if __name__ == "__main__":
    figure, main_axes, secondary_axes = instantiate_figure()


########################################################################################################################


# STEP 14 - GRAPH THE MINIMUM REQUIRED DATA TO HELP SET UP THE MAIN AND SECONDARY AXES - DONE


def scatter(figure_object, main_axes_object, data, marker=".", marker_fill_color=preferences.colors.colors["CORNFLOWERBLUE"],
            marker_label=None, marker_size=None
            ):
    """Create a scatter plot of a given colors, label, marker and marker size."""
    if marker_size is None:
        marker_size = 0.025
    # NOTE - Marker size is measured in points**2 where 1 point is 100/72 pixels.
    marker_size *= max(figure_object.get_size_inches()) * figure_object.dpi

    if len(np.shape(data)) == 1:  # One Point
        data0 = data[0]
        data1 = data[1]
    else:
        data0 = data[:, 0]
        data1 = data[:, 1]

    main_axes_object.scatter(data0, data1, marker=marker, c=marker_fill_color, label=marker_label, s=marker_size)


# API USAGE EXAMPLE
if __name__ == "__main__":
    scatter(figure, main_axes, non_dominated_solutions)


########################################################################################################################


# STEP 15 - SET UP THE GRAPH MAIN AND SECONDARY AXES


def setup_axes(axes_object, axes_name, num_ticks, optimal_point,
               decimals=preferences.parameters.parameters["OUTPUT_DECIMALS"], axes_limits=None,
               secondary_axes_limits=None,
               secondary_axis_scale=1.
               ):
    """Format the Pareto Front axis ticks."""

    SETTINGS = {
        "x": (axes_object.get_xlim,
              axes_object.set_xticks,
              axes_object.set_xticklabels,
              axes_object.xaxis,
              axes_object.set_xlim,
              optimal_point[0],
              0.307
              ),
        "y": (axes_object.get_ylim,
              axes_object.set_yticks,
              axes_object.set_yticklabels,
              axes_object.yaxis,
              axes_object.set_ylim,
              optimal_point[1],
              0.128
              )
    }

    if secondary_axes_limits is None:
        secondary_axes_limits = SETTINGS[axes_name][0]()

    min_value, max_value = secondary_axes_limits

    if secondary_axis_scale != 1.:
        min_value *= secondary_axis_scale
        max_value *= secondary_axis_scale

    custom_ticks = np.linspace(min_value, max_value, num_ticks)

    # Calculate the value to be appended regarding the optimal point and check if there is already an existing one
    # within 5%. If yes, remove the existing value.
    append_val = secondary_axis_scale * SETTINGS[axes_name][5]

    # The iterables supplied to math.dist need to be in the form of a list. Tuples return a TypeError.
    padding = SETTINGS[axes_name][6] * math.dist([custom_ticks[0]], [custom_ticks[1]])

    del_range = [append_val - padding, append_val + padding]

    custom_ticks = custom_ticks[(custom_ticks <= del_range[0]) | (custom_ticks >= del_range[1])]
    # Sorting will help later because the appended value be in its correct place.
    custom_ticks = np.sort(np.append(custom_ticks, append_val))

    SETTINGS[axes_name][1](custom_ticks)
    SETTINGS[axes_name][2](custom_ticks)

    SETTINGS[axes_name][3].set_major_formatter(FormatStrFormatter('%.' + str(decimals) + 'f'))

    if axes_limits == "preferences":
        SETTINGS[axes_name][4](min_value, max_value)

    # Disable axis autoscaling.
    axes_object.autoscale(False)

    if axes_limits == "return":
        return secondary_axes_limits


# API USAGE EXAMPLE
if __name__ == "__main__":
    setup_axes(main_axes, "x", 10, P0)
    # We need the Y-axis limits for the secondary axis.
    main_axes_limits = setup_axes(main_axes, "y", 10, P0, axes_limits="return")
    # Secondary axis.
    setup_axes(secondary_axes, "y", 10, P0, axes_limits="preferences", secondary_axes_limits=main_axes_limits,
               secondary_axis_scale=0.579249757500518)


########################################################################################################################


# STEP 16 - DRAW THE OPTIMAL POINT OF THE PARETO FRONTIER - DONE


def draw_recommended_point(figure_object, main_axes_object, optimal_point,
                       marker_fill_color=preferences.colors.colors["MEDIUMSEAGREEN"],
                       marker_label="Optimal Point", marker_size=0.25,
                       crosshair_stroke_color=preferences.colors.colors["MEDIUMSEAGREEN"], crosshair_stroke_weight=None
                       ):
    def _draw_crosshair(_figure_object=figure_object, _main_axes_object=main_axes_object, _optimal_point=optimal_point,
                        _crosshair_stroke_color=crosshair_stroke_color, _crosshair_stroke_weight=crosshair_stroke_weight
                        ):
        """Draw a straight line parallel to either the X- or the Y- axis."""

        if _crosshair_stroke_weight is None:
            _crosshair_stroke_weight = 0.0015
        _crosshair_stroke_weight *= max(_figure_object.get_size_inches()) * _figure_object.dpi

        _main_axes_object.plot(_main_axes_object.get_xlim(), (_optimal_point[1], _optimal_point[1]),
                               c=_crosshair_stroke_color, lw=_crosshair_stroke_weight
                               )
        _main_axes_object.plot((_optimal_point[0], _optimal_point[0]), _main_axes_object.get_ylim(),
                               c=_crosshair_stroke_color, lw=_crosshair_stroke_weight
                               )

    scatter(figure_object, main_axes_object, optimal_point, marker_fill_color=marker_fill_color,
            marker_label=marker_label, marker_size=marker_size
            )
    _draw_crosshair()


# API USAGE EXAMPLE
if __name__ == "__main__":
    draw_recommended_point(figure, main_axes, P0)


########################################################################################################################


# STEP 17 - DRAW THE HIGH TRADE-OFF AREA OF THE PARETO FRONTIER - DONE


def draw_high_tradeoff_area(figure_object, main_axes_object, high_tradeoff_area,
                            marker_fill_color=preferences.colors.colors["LIGHTCORAL"],
                            marker_label="High Trade-Off Area",
                            marker_size=0.25, rectangle_fill=False, rectangle_fill_color=None,
                            rectangle_stroke_color=preferences.colors.colors["LIGHTCORAL"],
                            rectangle_stroke_weight=None,
                            rectangle_size=0.5
                            ):
    def _draw_rectangle(_figure_object=figure_object, _axes_object=main_axes_object,
                        _high_tradeoff_area=high_tradeoff_area, _rectangle_size=rectangle_size,
                        _rectangle_fill=rectangle_fill, _rectangle_fill_color=rectangle_fill_color,
                        _rectangle_stroke_color=rectangle_stroke_color, _rectangle_stroke_weight=rectangle_stroke_weight
                        ):
        if _rectangle_stroke_weight is None:
            _rectangle_stroke_weight = 0.0015
        _rectangle_stroke_weight *= max(_figure_object.get_size_inches()) * _figure_object.dpi

        # Calculate the center of gravity of the rectangle
        center = np.mean(_high_tradeoff_area, axis=0)

        if np.shape(_high_tradeoff_area)[0] == 1:
            # Compute the dimensions of the rectangle as a percentage of the corresponding axes' bin size.
            # NOTE - To avoid a bug where the selected bin includes an appended value and is therefore smaller in size
            #  than the rest, we compute the max bin size between the first and last bins since the appended value can't
            #  be in both. The choice of the first and last bin is made arbitrarily.
            width = _rectangle_size * max(math.dist([_axes_object.get_xticks()[0]], [_axes_object.get_xticks()[1]]),
                                          math.dist([_axes_object.get_xticks()[-2]], [_axes_object.get_xticks()[-1]])
                                          )
            height = _rectangle_size * max(math.dist([_axes_object.get_yticks()[0]], [_axes_object.get_yticks()[1]]),
                                           math.dist([_axes_object.get_yticks()[-2]], [_axes_object.get_yticks()[-1]])
                                           )

            # Calculate the insertion point of the rectangle.
            ins = (center[0] - 0.5 * width, center[1] - 0.5 * height)
        else:
            # TODO - Fix this...
            # Get the limits of the high trade-off area.
            _lower_bound = np.min(_high_tradeoff_area, axis=0)
            _upper_bound = np.max(_high_tradeoff_area, axis=0)

            # Compute the dimensions of the rectangle, such that it's area is larger than the bounds of the high
            # tradeoff area by a factor of **_rectangle_size**.
            width = math.dist([_lower_bound[0]], [_upper_bound[0]])
            height = math.dist([_lower_bound[1]], [_upper_bound[1]])

            # Calculate the insertion point of the rectangle.
            ins = (_lower_bound[0], _lower_bound[1])

            print(_lower_bound)
            print(_upper_bound)

        rect = mpatches.Rectangle(ins, width, height, fill=_rectangle_fill, fc=_rectangle_fill_color,
                                  ec=_rectangle_stroke_color, lw=_rectangle_stroke_weight
                                  )
        _axes_object.add_patch(rect)

    scatter(figure_object, main_axes_object, high_tradeoff_area, marker_fill_color=marker_fill_color,
            marker_label=marker_label, marker_size=marker_size
            )
    _draw_rectangle()


# API USAGE EXAMPLE
if __name__ == "__main__":
    draw_high_tradeoff_area(figure, main_axes, P1)


########################################################################################################################


# STEP 18 - FINALIZE AND ACTIVATE THE FIGURE FOR THE GRAPHICAL OUTPUT


def finalize_figure(main_axes_object, grid_linestyle="--", color=preferences.colors.colors["GRAY"],
                    path="../database/optimization/output/pareto.png", dpi=300):
    main_axes_object.grid(ls=grid_linestyle, c=color)

    main_axes_object.legend()

    # plt.show()

    utilities.librarian.create_directory(os.path.split(path)[0])
    plt.savefig(path, dpi=dpi)


# API USAGE EXAMPLE
if __name__ == "__main__":
    finalize_figure(main_axes)

###################H#####################################################################################################

"""
[1]https://en.wikipedia.org/wiki/Feature_scaling
[2]Wierzbicki, A.P., 1980. The use of reference objectives in 
multiobjective simulation, in: Multiple criteria decision making theory and application. Springer, pp. 468–486.
[20]    doi:10.1007/978-3-642-48782-8_32
"""
