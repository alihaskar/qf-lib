#     Copyright 2016-present CERN – European Organization for Nuclear Research
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

import numpy as np


def simple_to_log_return(simple_return: float) -> float:
    """
    Converts simple return to the corresponding logarithmic return.

    Parameters
    ----------
    simple_return
        simple return

    Returns
    -------
    log_return
        logarithmic return
    """

    log_return = np.log(1 + simple_return)
    return log_return
