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

import openstudio


def osm2idf(input_path: str, output_path: str) -> None:
    """Convert an .OSM file to its .IDF equivalent."""

    # DO NOT TOUCH THIS!
    openstudio.energyplus.ForwardTranslator().translateModel(
        openstudio.osversion.VersionTranslator().loadModel(openstudio.path(input_path)).get()).save(
        openstudio.path(output_path), True)


if __name__ == "__main__":
    def main():
        """Entry point for debugging purposes."""

        osm2idf("../data/simulation/model/ASHRAE901_OfficeMedium_STD2016_Tucson.osm",
                "../data/simulation/model/ASHRAE901_OfficeMedium_STD2016_Tucson.idf")


    main()
