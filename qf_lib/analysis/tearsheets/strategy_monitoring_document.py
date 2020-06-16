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
from datetime import datetime

import matplotlib as plt

from qf_lib.analysis.error_handling import ErrorHandling
from qf_lib.analysis.tearsheets.abstract_tearsheet import AbstractTearsheet
from qf_lib.containers.series.qf_series import QFSeries
from qf_lib.documents_utils.document_exporting.element.chart import ChartElement
from qf_lib.documents_utils.document_exporting.element.paragraph import ParagraphElement
from qf_lib.plotting.charts.cone_chart_oos import ConeChartOOS
from qf_lib.plotting.decorators.axes_position_decorator import AxesPositionDecorator
from qf_lib.settings import Settings


@ErrorHandling.class_error_logging()
class StrategyMonitoringDocument(AbstractTearsheet):

    def __init__(self, settings: Settings, pdf_exporter, strategy_series: QFSeries, benchmark_series: QFSeries,
                 live_date: datetime = None, title: str = "Strategy Analysis"):
        super().__init__(settings, pdf_exporter, strategy_series, live_date, title)

        self.is_mean_return = None
        self.is_sigma = None

        self.benchmark_series = benchmark_series

    def build_document(self):
        self._add_header()
        self.document.add_element(ParagraphElement("\n\n"))

        series_list = [self.strategy_series, self.benchmark_series]
        self._add_perf_chart(series_list)
        self.document.add_element(ParagraphElement("\n\n"))

        self._add_cone_chart()
        self.document.add_element(ParagraphElement("\n\n"))

        self._add_rolling_chart(self.strategy_series)

    def set_in_sample_statistics(self, is_mean_return, is_sigma):
        self.is_mean_return = is_mean_return
        self.is_sigma = is_sigma

    def _add_cone_chart(self):
        cone_chart = ConeChartOOS(self.strategy_series,
                                  is_mean_return=self.is_mean_return,
                                  is_sigma=self.is_sigma)

        position_decorator = AxesPositionDecorator(*self.full_image_axis_position)
        cone_chart.add_decorator(position_decorator)

        chart_element = ChartElement(cone_chart, self.full_image_size, self.dpi, False)
        self.document.add_element(chart_element)

    def save(self, report_dir: str = ""):
        # Set the style for the report
        plt.style.use(['tearsheet'])

        filename = "%Y_%m_%d-%H%M {}.pdf".format(self.title)
        filename = datetime.now().strftime(filename)
        return self.pdf_exporter.generate([self.document], report_dir, filename)
