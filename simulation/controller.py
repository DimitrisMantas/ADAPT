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


def run_eplus(idf: str, epw: str, idd="eplus/eplus.idd", set_idd=True, output_path="../database/simulation/logs/",
              read_vars=True, verbose="q") -> None:
    """Run an eplus™ whole building performance simulation."""

    # The .IDD file needs to be set only once during a given workflow.
    if set_idd:
        eppy.modeleditor.IDF.setiddname(idd)

    eppy.modeleditor.IDF(idf, epw).run(output_directory=output_path, readvars=read_vars, verbose=verbose)


if __name__ == "__main__":
    def main():
        """Entry point for debugging purposes."""

        run_eplus("../database/simulation/model/ASHRAE901_OfficeMedium_STD2019_Tucson.idf",
                  "../database/simulation/model/USA_AZ_Tucson-Davis-Monthan.AFB.722745_TMY3.epw")


    main()
