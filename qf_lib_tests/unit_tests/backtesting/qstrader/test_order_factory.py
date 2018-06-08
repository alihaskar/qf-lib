import unittest
from math import floor

import pandas as pd
from mockito import mock, when

from qf_lib.backtesting.qstrader.contract.contract import Contract
from qf_lib.backtesting.qstrader.contract_to_ticker_conversion.bloomberg_mapper import \
    DummyBloombergContractTickerMapper
from qf_lib.backtesting.qstrader.order.execution_style import MarketOrder, StopOrder
from qf_lib.backtesting.qstrader.order.order import Order
from qf_lib.backtesting.qstrader.order.orderfactory import OrderFactory
from qf_lib.common.tickers.tickers import BloombergTicker


class TestOrderFactory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = Contract('AAPL US Equity', 'STK', 'NASDAQ')
        cls.ticker = BloombergTicker('AAPL US Equity')
        cls.current_portfolio_value = 1000.0
        cls.share_price = 10.0

        position = mock(strict=True)
        when(position).quantity().thenReturn(10)
        when(position).contract().thenReturn(cls.contract)

        broker = mock(strict=True)
        when(broker).get_portfolio_value().thenReturn(cls.current_portfolio_value)
        when(broker).get_positions().thenReturn([position])

        data_handler = mock(strict=True)
        when(data_handler).get_last_available_price([cls.ticker]).thenReturn(
            pd.Series([cls.share_price], index=[cls.ticker]))

        cls.order_factory = OrderFactory(broker, data_handler, DummyBloombergContractTickerMapper())

    def test_order(self):
        quantity = 5
        execution_style = MarketOrder()
        time_in_force = 'GTC'

        orders = self.order_factory.orders({self.contract: quantity}, execution_style, time_in_force)
        self.assertEqual(orders[0], Order(self.contract, quantity, execution_style, time_in_force))

    def test_order_target(self):
        quantity = -5
        execution_style = StopOrder(4.20)
        time_in_force = 'DAY'

        orders = self.order_factory.target_orders({self.contract: 5}, execution_style, time_in_force)
        self.assertEqual(orders[0], Order(self.contract, quantity, execution_style, time_in_force))

    def test_order_value(self):
        value = 100.0
        quantity = floor(100.0/self.share_price)  # type: int
        execution_style = StopOrder(4.20)
        time_in_force = 'DAY'

        orders = self.order_factory.value_orders({self.contract: value}, execution_style, time_in_force)
        self.assertEqual(orders[0], Order(self.contract, quantity, execution_style, time_in_force))

    def test_order_percent(self):
        percentage = 0.5
        execution_style = StopOrder(4.20)
        time_in_force = 'GTC'
        quantity = floor(percentage * self.current_portfolio_value / self.share_price)  # type: int

        orders = self.order_factory.percent_order({self.contract: percentage}, execution_style, time_in_force)
        self.assertEqual(orders[0], Order(self.contract, quantity, execution_style, time_in_force))

    def test_order_target_value(self):
        execution_style = StopOrder(4.20)
        time_in_force = 'GTC'
        quantity = 4

        orders = self.order_factory.target_value_order({self.contract: 140.0}, execution_style, time_in_force)
        self.assertEqual(orders[0], Order(self.contract, quantity, execution_style, time_in_force))

    def test_order_target_percent(self):
        quantity = 40
        execution_style = StopOrder(4.20)
        time_in_force = 'GTC'

        orders = self.order_factory.order_target_percent({self.contract: 0.5}, execution_style, time_in_force)
        self.assertEqual(orders[0], Order(self.contract, quantity, execution_style, time_in_force))


if __name__ == "__main__":
    unittest.main()