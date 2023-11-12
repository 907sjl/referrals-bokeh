from bokeh.document import Document
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.ranges import FactorRange
from bokeh.models.annotations import HTMLLabelSet

import pandas as pd

from datetime import datetime

import model.WaitTimes as wt


class ReferralVolumePlot:

    def __init__(self,
                 doc: Document,
                 plot_name: str,
                 sent_measure: str,
                 canceled_measure: str,
                 rejected_measure: str,
                 closed_wbs_measure: str,
                 plot_width: int = 300,
                 plot_height: int = 80):

        self.document = doc
        self.plot_name = plot_name
        self.volume_measures = ['Sent', 'Canceled', 'Rejected', 'Closed WBS']
        self.bar_colors = ['#EB895F', '#9071CE', '#A1343C', '#118DFF']
        self.sent_measure = sent_measure
        self.canceled_measure = canceled_measure
        self.rejected_measure = rejected_measure
        self.closed_wbs_measure = closed_wbs_measure
        self.plot_width = plot_width
        self.plot_height = plot_height
        self.volume_data = {}
        self.plot_data = pd.DataFrame()
        self.plot_data_source = None
        self.plot_left_align_label_data = pd.DataFrame()
        self.plot_left_align_label_source = None
        self.plot_right_align_label_data = pd.DataFrame()
        self.plot_right_align_label_source = None

    def load_clinic_data(self, month: datetime, clinic: str) -> None:
        volume_values = [wt.get_clinic_count_measure(month, clinic, self.sent_measure),
                         wt.get_clinic_count_measure(month, clinic, self.canceled_measure),
                         wt.get_clinic_count_measure(month, clinic, self.rejected_measure),
                         wt.get_clinic_count_measure(month, clinic, self.closed_wbs_measure)]
        self.volume_data = {'measure': self.volume_measures,
                            'value': volume_values,
                            'bar_color': self.bar_colors}
    # END load_clinic_data

    def create_plot_data(self) -> None:

        max_data_value = max(self.volume_data['value'])

        # Create a dataframe with the plot data
        volume_dataframe = pd.DataFrame.from_dict(self.volume_data, orient='columns')

        # If a data point is more than 75% of the range the label will be right-aligned inside the bar
        volume_dataframe['range_ratio'] = volume_dataframe.value / max_data_value
        volume_dataframe.loc[(volume_dataframe.range_ratio > 0.75), ['data_label_align']] = 'right'
        volume_dataframe.loc[(volume_dataframe.range_ratio <= 0.75), ['data_label_align']] = 'left'

        # Create the data label text
        volume_dataframe['data_point_label'] = volume_dataframe['value'].apply(lambda x: str(x))

        # Store the plot data to be used for rendering
        self.plot_data = volume_dataframe

        # Either create or update a column data source for the bar chart
        if self.plot_data_source is None:
            self.plot_data_source = ColumnDataSource(volume_dataframe)
        else:
            self.plot_data_source.data = volume_dataframe.to_dict(orient="list")

        # The left and right aligned labels must be in separate label sets
        self.plot_left_align_label_data = volume_dataframe.loc[(volume_dataframe.data_label_align == 'left')]
        if self.plot_left_align_label_source is None:
            self.plot_left_align_label_source = ColumnDataSource(self.plot_left_align_label_data)
        else:
            self.plot_left_align_label_source.data = self.plot_left_align_label_data.to_dict(orient="list")

        self.plot_right_align_label_data = volume_dataframe.loc[(volume_dataframe.data_label_align == 'right')]
        if self.plot_right_align_label_source is None:
            self.plot_right_align_label_source = ColumnDataSource(self.plot_right_align_label_data)
        else:
            self.plot_right_align_label_source.data = self.plot_right_align_label_data.to_dict(orient="list")
    # END create_plot_data

    def add_plot(self) -> None:

        # Reverse the measures for the chart range so that the first measure is on top (higher y value)
        volume_y_range = FactorRange(factors=self.volume_measures[::-1])

        volume_plot = figure(y_range=volume_y_range,
                             title=None,
                             toolbar_location=None,
                             height=self.plot_height, width=self.plot_width,
                             x_axis_type=None,
                             output_backend="svg")
        volume_plot.hbar(y='measure',
                         right='value',
                         color='bar_color',
                         height=0.8,
                         source=self.plot_data_source)

        # Create the data point labels and add them to the plot
        volume_left_align_label_set = HTMLLabelSet(x='value',
                                                   x_offset=4,
                                                   y='measure',
                                                   y_offset=-2,
                                                   text='data_point_label',
                                                   level='glyph',
                                                   text_align='left',
                                                   text_baseline='middle',
                                                   text_font_size='11pt',
                                                   text_color='#000000',
                                                   source=self.plot_left_align_label_source)
        volume_plot.add_layout(volume_left_align_label_set)
        volume_right_align_label_set = HTMLLabelSet(x='value',
                                                    x_offset=-4,
                                                    y='measure',
                                                    y_offset=-2,
                                                    text='data_point_label',
                                                    level='glyph',
                                                    text_align='right',
                                                    text_baseline='middle',
                                                    text_font_size='11pt',
                                                    text_color='#FFFFFF',
                                                    source=self.plot_right_align_label_source)
        volume_plot.add_layout(volume_right_align_label_set)

        # Set style configs
        volume_plot.background_fill_alpha = 0
        volume_plot.outline_line_alpha = 0
        volume_plot.border_fill_alpha = 0
        volume_plot.flow_mode = 'inline'
        volume_plot.sizing_mode = 'fixed'
        volume_plot.width_policy = 'fixed'

        volume_plot.xgrid.grid_line_color = None
        volume_plot.ygrid.grid_line_color = None

        volume_plot.yaxis.major_label_text_font_size = '11pt'
        volume_plot.yaxis.major_label_text_color = '#000000'
        volume_plot.yaxis.axis_line_alpha = 0
        volume_plot.yaxis.major_tick_line_alpha = 0
        volume_plot.yaxis.major_label_standoff = 0

        # Add this figure to the document, must be embedded to avoid a JS error
        volume_plot.name = self.plot_name
        self.document.add_root(volume_plot)
    # END add_plot
# END CLASS ReferralVolumePlot
