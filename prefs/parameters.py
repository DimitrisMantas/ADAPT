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
#
#
parameters = {

    # This setting controls the number of decimal places used in graphical and non-graphical outputs.
    # NOTE - This value must be a positive integer.
    "OUTPUT_DECIMALS": 2,

    # This setting controls the number of decimal places used during the initial population sampling to reduce the
    # design space.
    # NOTE - This value must be a positive integer.
    "SAMPLING_DECIMALS": 2,

    # This setting controls the seed of the RNG engine used during the sim process to ensure reproducible
    # results.
    # NOTE - This value must be a positive integer.
    "SEED": 4144415054,

    # This setting controls the value of η for the standard or custom binary crossover scheme. Low values of η result
    # in children that do not resemble their parents, while high values of η do the opposite.
    # NOTE - This value must be a positive integer between 1 amd 200.
    "CROSSOVER_ETA": 1,

    # This setting controls the population crossover probability.
    # NOTE - This value must be a real number between 0.0 and 1.0.
    "CROSSOVER_PROBABILITY": 0.8,

    #
    # NOTE -
    "MUTATION_ETA": 1,

    # This value is the reporting time interval used in the CSV output file of the sim engine.
    # NOTE - This value must be less than or equal to the sim process time interval and such that it divides
    #  said interval exactly.
    "DF_FREQ_STR": "1H",
    "DF_FREQ_NUM": 1
}
