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


import openstudio


def convert_osm_to_idf(osm_filepath: str, idf_filepath: str) -> None:
    """
    Converts an OSM file to its IDF equivalent one.

    The provided file paths can be either relative or absolute.

    @param osm_filepath: The OSM file path.
    @param idf_filepath: The IDF file path.
    """
    # DO NOT TOUCH THIS!
    openstudio.energyplus.ForwardTranslator().translateModel(
        openstudio.osversion.VersionTranslator().loadModel(openstudio.path(osm_filepath)).get()).save(
        openstudio.path(idf_filepath), True)


if __name__ == "__main__":
    def main():
        """Entry point for debugging purposes."""

        convert_osm_to_idf("../database/simulation/model/ASHRAE901_OfficeMedium_STD2016_Tucson.osm",
                           "../database/simulation/model/ASHRAE901_OfficeMedium_STD2016_Tucson.idf")


    main()
