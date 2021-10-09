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

import eppy.modeleditor


def modify_schedule(x, idf, schedule_object, idd="../simulation/eplus/eplus.idd", set_idd=True) -> None:
    """Edit any schedule inside a standard .IDF file."""

    # The .IDD file needs to be set only once during a given workflow.
    if set_idd:
        eppy.modeleditor.IDF.setiddname(idd)

    idf = eppy.modeleditor.IDF(idf)

    schedule = idf.idfobjects['Schedule:Day:Interval'][schedule_object]

    for i in range(1, 25):  # The upper bound depends on the simulation unit time.
        field = "Value_Until_Time_" + str(i)

        # This is equivalent to the commented block below.
        setattr(schedule, field, x[i - 1])

    idf.save()
