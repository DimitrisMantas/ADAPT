"""
    This file is part of the interface of ADAPT. It defines the
    directory creation methods for reading and writing data parsed form its
    performance simulation to its simulation engine and vice versa.

    Copyright (C) 2021-2022
        Dimitris Mantas, MEng (s)

        Department of Civil Engineering
        School of Engineering
        University of Patras

        A: University Campus, Rio, Achaia, 265 04, Greece
        E: d.mantas@g.upatras.gr | d.mantas@upnet.gr
        T: +30 698 995 8826

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import pathlib


def create_directory(path: str) -> None:
    """Create a directory (i.e. folder) at a predefined path."""

    # NOTE - This input argument setup helps to mimic the behavior of the POSIX **mkdir -p** command.
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

#TODO
def move_file():
    pass
