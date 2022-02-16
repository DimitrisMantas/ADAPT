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

from setuptools import setup

with open("README.md", "r") as file:
    read_me = file.read()

setup(name="ADAPT",
      version="1.0.0",

      description="ADAPT is a Python 3 module for the opt of building energy consumption and human comfort "
                  "using genetic algorithms coupled with whole building performance sim software.",
      long_description=read_me,

      license="AGPL-3.0",

      author="Dimitris Mantas",
      author_email="dimitris.mantas@outlook.com",
      url="https://github.com/DimitrisMantas/ADAPT",

      packages=["opt", "prefs", "sim", "utils"],
      install_requires=["eppy==0.5.56", "matplotlib==3.4.3", "numpy==1.21.2", "openstudio==3.2.1", "pandas==1.3.3",
                        "pymoo==0.5.0"])
