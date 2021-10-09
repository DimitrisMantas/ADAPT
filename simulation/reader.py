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

import statistics
import warnings

import eppy.results.fasthtml
import numpy
import pandas


def read_nse(path="../data/simulation/logs/eplustbl.htm", convert_value=True) -> float:
    """Read the net site energy consumption from a standard eplustbl.HTM eplus™ result file."""

    with open(path, "r") as file:
        value = eppy.results.fasthtml.tablebyindex(file, 0)[1][1][1]

    # Convert NSE from GJ (i.e. the default value used by eplus™) to kWh.
    if convert_value:
        value *= 1E6 / 3600

    return value


def read_ppd(mode="max") -> float:
    """Read the occupancy-weighted PPD from a standard eplusout.HTM eplus™ result file."""

    # The .CSV file contains timestamps, which are not required.
    dataframe = pandas.read_csv("../data/simulation/logs/eplusout.csv").drop("Date/Time", axis=1)

    split_index = len(dataframe.columns) // 2

    occ = dataframe.iloc[:, 0:split_index].to_numpy()  # TODO - DO WE NEED THE ZERO?
    ppd = dataframe.iloc[:, split_index:].to_numpy()

    # Throw a RunTime warning when dividing by zero.
    with numpy.errstate(divide='warn'):

        # Treat this warning as an error.
        # NOTE - THIS IS A GLOBAL SETTING.
        warnings.filterwarnings('error', category=RuntimeWarning)

        _ppd = []
        for i in range(len(occ)):
            try:
                # This will create a PPD time series for the whole site.
                _ppd.append(sum(occ[i, :] * ppd[i, :]) / sum(occ[i, :]))
            except RuntimeWarning:
                _ppd.append(0)  # The whole site is unoccupied.

        # Reset the warning handling functionality back to default.
        warnings.filterwarnings('default')

    if mode == "max":
        return max(_ppd)
    elif mode == "mean":
        _ppd = [i for i in _ppd if i != 0.]
        return statistics.mean(ppd)
    else:
        raise ValueError('Mode must be set to either "max" or "mean".')


if __name__ == "__main__":
    def main():
        """Entry point for debugging purposes."""

        print(read_nse())
        print(read_ppd())


    main()
