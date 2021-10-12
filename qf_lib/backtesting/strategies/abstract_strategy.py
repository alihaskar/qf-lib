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
import abc

from qf_lib.backtesting.trading_session.trading_session import TradingSession


class AbstractStrategy(metaclass=abc.ABCMeta):
    """ Basic interface used to create a generic strategy. """

    def __init__(self, ts: TradingSession):
        self.timer = ts.timer
        self.notifiers = ts.notifiers

    @abc.abstractmethod
    def calculate_and_place_orders(self):
        """
        The base function of every strategy. Its purpose is the computation of desired signals, creation of
        corresponding orders and afterwards sending them to the broker.
        """
        raise NotImplementedError()
