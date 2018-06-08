# it is important to import the matplotlib first and then switch the interactive/dynamic mode on.
import matplotlib.pyplot as plt
plt.ion()  # required for dynamic chart
import csv
from qf_lib.backtesting.qstrader.order_fill import OrderFill
from qf_lib.common.utils.document_exporting.pdf_exporter import PDFExporter
from qf_lib.get_sources_root import get_src_root
from qf_lib.settings import Settings
from datetime import datetime
from os import path, makedirs
from qf_lib.backtesting.qstrader.backtest_result.backtest_result import BacktestResult
from qf_lib.backtesting.qstrader.monitoring.abstract_monitor import AbstractMonitor
from qf_lib.common.tearsheets.tearsheet_without_benchmark import TearsheetWithoutBenchmark


class BacktestMonitor(AbstractMonitor):
    """
    This Monitor will be used to monitor backtest run from the script.
    It will display the portfolio value as the backtest progresses and generate a PDF at the end.
    It is not suitable for the Web application
    """

    def __init__(self, backtest_result: BacktestResult, settings: Settings, pdf_exporter: PDFExporter):
        super().__init__(backtest_result)

        # Set up an empty chart that can be updated
        self._figure, self._ax = plt.subplots()
        self._figure.set_size_inches(12, 5)
        self._line, = self._ax.plot([], [])

        self._ax.set_autoscaley_on(True)

        end_date = backtest_result.end_date
        if end_date is None:
            end_date = datetime.now()

        self._ax.set_xlim(backtest_result.start_date, end_date)
        self._ax.grid()
        self._ax.set_title("Progress of the backtest - {}".format(backtest_result.backtest_name))
        self._figure.autofmt_xdate(rotation=20)
        self._settings = settings
        self._pdf_exporter = pdf_exporter
        self._trades_file_path = self._init_csv_file()

    def end_of_trading_update(self, _: datetime=None):
        """
        Generates a tearsheet PDF with the statistics of the backtest and saves it on the disk
        """
        portfolio_tms = self.backtest_result.portfolio.get_portfolio_timeseries()
        portfolio_tms.name = self.backtest_result.backtest_name
        tearsheet = TearsheetWithoutBenchmark(
            self._settings, self._pdf_exporter, portfolio_tms, title=portfolio_tms.name)
        tearsheet.build_document()
        tearsheet.save()

    def end_of_day_update(self, timestamp: datetime=None):
        """
        Update line chart with current timeseries
        """
        portfolio_tms = self.backtest_result.portfolio.get_portfolio_timeseries()
        self._ax.grid()

        # Set the data on x and y
        self._line.set_xdata(portfolio_tms.index)
        self._line.set_ydata(portfolio_tms.values)

        # Need both of these in order to rescale
        self._ax.relim()
        self._ax.autoscale_view()

        # We need to draw and flush
        self._figure.canvas.draw()
        self._figure.canvas.flush_events()

        self._ax.grid()  # we need two grid() calls in order to keep the grid on the chart

    def real_time_update(self, timestamp: datetime=None):
        """
        This method will not be used by the historical backtest
        """
        pass

    def record_trade(self, order_fill: OrderFill):
        """
        Print the trade to the CSV file and on the console
        """
        self._save_trade_to_file(order_fill)

    def _init_csv_file(self) -> str:
        """
        Creates a new csv file for every backtest run, writes the header and returns the path to the file.
        """
        output_dir = path.join(get_src_root(), self._settings.output_directory, "Trades")
        if not path.exists(output_dir):
            makedirs(output_dir)

        file_name_template = "%Y_%m_%d-%H%M {}.csv".format(self.backtest_result.backtest_name)
        csv_filename = datetime.now().strftime(file_name_template)
        file_path = path.expanduser(path.join(output_dir, csv_filename))

        # Write new file header
        fieldnames = ["Timestamp", "Contract", "Quantity", "Price", "Commission"]
        with open(file_path, 'a', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

        return file_path

    def _save_trade_to_file(self, order_fill: OrderFill):
        """
        Append all details about the OrderFill to the CSV trade log.
        """
        with open(self._trades_file_path, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([
                order_fill.time,
                order_fill.contract.symbol,
                order_fill.quantity,
                order_fill.price,
                order_fill.commission
            ])