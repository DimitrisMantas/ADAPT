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


import pathlib


def create_directories(path: str) -> None:
    """
    Create a directory along with all its parents at a specified location.

    Parameters:
        path (str):
    Returns:
        None
    """
    # NOTE - This input argument setup helps to mimic the behavior of the POSIX **mkdir -p** command.
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


# TODO
def move_file():
    pass
