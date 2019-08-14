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

import math
from typing import Sequence, Tuple

from qf_lib.backtesting.execution_handler.slippage.base import Slippage
from qf_lib.backtesting.order.execution_style import MarketOrder, StopOrder
from qf_lib.backtesting.order.order import Order
from qf_lib.common.utils.logging.qf_parent_logger import qf_logger


class PriceBasedSlippage(Slippage):
    """
    Calculates the slippage by using some fixed fraction of the current securities' price (e.g. always 0.01%).
    """

    def __init__(self, slippage_rate: float):
        self.slippage_rate = slippage_rate
        self._logger = qf_logger.getChild(self.__class__.__name__)

    def apply_slippage(
            self, orders: Sequence[Order], no_slippage_fill_prices: Sequence[float]
    ) -> Tuple[Sequence[float], Sequence[int]]:
        fully_filled_order_volumes = [order.quantity for order in orders]

        if self.slippage_rate == 0.0:
            return no_slippage_fill_prices, fully_filled_order_volumes

        fill_prices = []
        for order, no_slippage_price in zip(orders, no_slippage_fill_prices):
            execution_style = order.execution_style
            if isinstance(execution_style, (MarketOrder, StopOrder)):
                fill_price = self._get_single_fill_price(order, no_slippage_price)
            else:
                self._logger.warning("Unsupported execution style: {}. No slippage was applied".format(execution_style))
                fill_price = no_slippage_price

            fill_prices.append(fill_price)

        return fill_prices, fully_filled_order_volumes

    def _get_single_fill_price(self, order, no_slippage_price):
        if math.isnan(no_slippage_price):
            fill_price = float('nan')
        else:
            if order.quantity > 0:  # BUY Order
                multiplier = 1 + self.slippage_rate
            else:  # SELL Order
                multiplier = 1 - self.slippage_rate

            fill_price = no_slippage_price * multiplier

        return fill_price
