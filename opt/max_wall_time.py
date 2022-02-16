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

import time

from pymoo.core.termination import Termination
from pymoo.util.misc import time_to_int


class MaxWallTime(Termination):

    def __init__(self, max_time) -> None:
        super().__init__()
        self.start = None
        self.now = None

        if max_time is None:
            self.max_time = 2147483647  # This is the UNIX timestamp upper limit.
        elif isinstance(max_time, str):
            self.max_time = time_to_int(max_time)
        elif isinstance(max_time, int) or isinstance(max_time, float):
            self.max_time = max_time
        else:
            raise Exception("The maximum runtime must be provided in either integer or string form.")

    def do_continue(self, algorithm):
        if self.start is None:
            self.start = algorithm.start_time

        self.now = time.time()
        return self.now - self.start < self.max_time

