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
import eppy.modeleditor


def modify_schedule(x, idf, schedule_object, idd="../sim/EnergyPlus/EnergyPlus.idd", set_idd=True) -> None:
    """Edit any schedule inside a standard .IDF file."""

    # The .IDD file needs to be set only once during a given workflow.
    if set_idd:
        eppy.modeleditor.IDF.setiddname(idd)

    idf = eppy.modeleditor.IDF(idf)

    schedule = idf.idfobjects['Schedule:Compact'][schedule_object]

    for i in range(15, 63, 2):
        field = "Field_" + str(i)

        # This is equivalent to the commented block below.
        setattr(schedule, field, x[int((0.5 * i) - 7.5)])  # This maps 15,17,19,...,61 to 0,1,2,...,23.

    idf.save()



x = [15.00,  # 1
     15.00,  # 2
     15.00,  # 3
     15.00,  # 4
     15.00,  # 5
     21.00,  # 6
     21.00,  # 7
     21.00,  # 8
     21.00,  # 9
     21.00,  # 10
     21.00,  # 11
     21.00,  # 12
     21.00,  # 13
     21.00,  # 14
     21.00,  # 15
     21.00,  # 16
     21.00,  # 17
     21.00,  # 18
     21.00,  # 19
     21.00,  # 20
     21.00,  # 21
     21.00,  # 22
     15.00,  # 23
     15.00,  # 24

     15.001,  # 1
     15.001,  # 2
     15.001,  # 3
     15.001,  # 4
     15.001,  # 5
     21.001,  # 6
     21.001,  # 7
     21.001,  # 8
     21.001,  # 9
     21.001,  # 10
     21.001,  # 11
     21.001,  # 12
     21.001,  # 13
     21.001,  # 14
     21.001,  # 15
     21.001,  # 16
     21.001,  # 17
     21.001,  # 18
     21.001,  # 19
     21.001,  # 20
     21.001,  # 21
     21.001,  # 22
     15.001,  # 23
     15.001,  # 24
     ]
# Heating
modify_schedule(x[00:24], "../database/sim/model/ASHRAE901_OfficeMedium_STD2019_Tucson.idf", 29)
# Cooling
modify_schedule(x[24:48], "../database/sim/model/ASHRAE901_OfficeMedium_STD2019_Tucson.idf", 36)