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


import setuptools

with open("README.md", "r") as readme:
    read_me = readme.read()

setuptools.setup(name="ADAPT",
                 version="1.0.0",

                 description="ADAPT is a Python program for the opt of building energy consumption and human "
                             "comfort.",
                 long_description=read_me,

                 license="GPL-3.0",

                 author="Dimitris Mantas",
                 author_email="dimitris.mantas@outlook.com",
                 url="https://github.com/DimitrisMantas/ADAPT",

                 packages=["opt", "prefs", "sim", "utils"],
                 install_requires=["eppy>=0.5.57",
                                   "matplotlib",
                                   "numpy",
                                   "openstudio",
                                   "pandas",
                                   "pymoo==0.5.0"])
