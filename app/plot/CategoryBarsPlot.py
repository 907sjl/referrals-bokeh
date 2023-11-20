"""
CategoryBarsPlot.py
Class that represents a comparative bar chart plot of referral counts.
https://907sjl.github.io/
"""

import pandas as pd

from datetime import datetime

from bokeh.document import Document
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.models.annotations import HTMLLabelSet
import model.Pending as p


class CategoryBarsPlot:
    """
    Class that represents a comparative bar chart plot of referral counts.
    """

    def __init__(self,
                 doc: Document,
                 plot_name: str,
                 values_measure: str,
                 category_column: str,
                 values_column: str,
                 plot_width: int = 286):
        self.document = doc
        self.figure = None
        self.volume_y_range = None
        self.plot_name = plot_name
        self.values_measure = values_measure
        self.category_column = category_column
        self.values_column = values_column
        self.ratio_data = {}
        self.plot_data = pd.DataFrame()
        self.plot_data_source = None
        self.left_align_labels_df = pd.DataFrame()
        self.left_align_labels_source = None
        self.right_align_labels_df = pd.DataFrame()
        self.right_align_labels_source = None
        self.plot_width = plot_width
        self.plot_height = 0
    # END __init__

    def load_clinic_data(self, month: datetime, clinic: str) -> None:
        if self.values_measure == 'get_counts_by_on_hold_reason':
            volume_values = p.get_counts_by_on_hold_reason(clinic).copy()
            volume_values['Reason for Hold'] = volume_values['Reason for Hold'].str.replace('Coordinating', 'Coord.')
        elif self.values_measure == 'get_counts_by_pending_reschedule_sub_status':
            volume_values = p.get_counts_by_pending_reschedule_sub_status(clinic).copy()
            volume_values['Referral Sub-Status'] = (
                volume_values['Referral Sub-Status'].str.replace('Call Patient to Schedule Appointment',
                                                                 'Call Patient to Schedule'))
        elif self.values_measure == 'get_counts_by_pending_acceptance_sub_status':
            volume_values = p.get_counts_by_pending_acceptance_sub_status(clinic).copy()
            volume_values['Referral Sub-Status'] = (
                volume_values['Referral Sub-Status'].str.replace('Call Patient to Schedule Appointment',
                                                                 'Call Patient to Schedule'))
        elif self.values_measure == 'get_counts_by_accepted_referral_sub_status':
            volume_values = p.get_counts_by_accepted_referral_sub_status(clinic).copy()
            volume_values['Referral Sub-Status'] = (
                volume_values['Referral Sub-Status'].str.replace('Call Patient to Schedule Appointment',
                                                                 'Call Patient to Schedule'))
        else:
            volume_values = pd.DataFrame.from_dict({self.category_column: [],
                                                    self.values_column: []})
        self.ratio_data = {'measure': volume_values[self.category_column].tolist(),
                           'value': volume_values[self.values_column].tolist()}
    # END load_clinic_data

    def create_plot_data(self) -> None:

        max_data_value = max(self.ratio_data['value'])
        if len(self.ratio_data['measure']) > 11:
            self.plot_height = 34 + (22 * 10)
        else:
            self.plot_height = 34 + (22 * (len(self.ratio_data['measure']) - 1))

        # Create a dataframe to hold potting data for each slice of the pie chart
        df = pd.DataFrame.from_dict(self.ratio_data).sort_values(by=['value'], ascending=False).reindex()

        # If a data point is more than 75% of the range the label will be right-aligned inside the bar
        df['range_ratio'] = df['value'] / max_data_value
        df.loc[(df['range_ratio'] > 0.75), ['data_label_align']] = 'right'
        df.loc[(df['range_ratio'] <= 0.75), ['data_label_align']] = 'left'

        # Create the data label text
        df['data_point_label'] = df['value'].apply(lambda x: str(x))

        # Color the bars
        df['bar_color'] = '#EB895F'
        df.loc[(df['measure'] == 'Other'), ['bar_color']] = '#808080'
        df.loc[(df['measure'] == '(none)'), ['bar_color']] = '#808080'
        df.loc[(df['measure'] == 'No Status'), ['bar_color']] = '#808080'

        # Store plot data for rendering later
        self.plot_data = df

        if self.plot_data_source is None:
            self.plot_data_source = ColumnDataSource(self.plot_data)
        else:
            self.plot_data_source.data = self.plot_data.to_dict(orient="list")

        # The left and right aligned labels must be in separate label sets
        self.left_align_labels_df = df.loc[(df.data_label_align == 'left')]
        if self.left_align_labels_source is None:
            self.left_align_labels_source = ColumnDataSource(self.left_align_labels_df)
        else:
            self.left_align_labels_source.data = self.left_align_labels_df.to_dict(orient="list")

        self.right_align_labels_df = df.loc[(df.data_label_align == 'right')]
        if self.right_align_labels_source is None:
            self.right_align_labels_source = ColumnDataSource(self.right_align_labels_df)
        else:
            self.right_align_labels_source.data = self.right_align_labels_df.to_dict(orient="list")
    # END create_plot_data

    def add_plot(self) -> None:

        # Reverse the measures for the chart range so that the first measure is on top (higher y value)
        self.volume_y_range = FactorRange(factors=self.plot_data['measure'].to_list()[::-1])

        # Create a plot area with the custom range, plot horizontal bars for each measure
        self.figure = figure(y_range=self.volume_y_range,
                             title=None,
                             toolbar_location=None,
                             height=self.plot_height,
                             width=self.plot_width,
                             x_axis_type=None,
                             output_backend="svg")
        self.figure.hbar(y='measure',
                         right='value',
                         color='bar_color',
                         height=0.75,
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
                                                   text_font_size='12pt',
                                                   text_color='#000000',
                                                   source=self.left_align_labels_source)
        self.figure.add_layout(volume_left_align_label_set)
        volume_right_align_label_set = HTMLLabelSet(x='value',
                                                    x_offset=-4,
                                                    y='measure',
                                                    y_offset=-2,
                                                    text='data_point_label',
                                                    level='glyph',
                                                    text_align='right',
                                                    text_baseline='middle',
                                                    text_font_size='12pt',
                                                    text_color='#FFFFFF',
                                                    source=self.right_align_labels_source)
        self.figure.add_layout(volume_right_align_label_set)

        # Set style configs
        self.figure.background_fill_alpha = 0
        self.figure.outline_line_alpha = 0
        self.figure.border_fill_alpha = 0
        self.figure.flow_mode = 'inline'
        self.figure.sizing_mode = 'fixed'
        self.figure.width_policy = 'fixed'

        self.figure.xgrid.grid_line_color = None
        self.figure.ygrid.grid_line_color = None

        self.figure.yaxis.major_label_text_font_size = '12pt'
        self.figure.yaxis.major_label_text_color = '#000000'
        self.figure.yaxis.axis_line_alpha = 0
        self.figure.yaxis.major_tick_line_alpha = 0
        self.figure.yaxis.major_label_standoff = 0

        # Add this figure to the document, must be embedded to avoid a JS error
        self.figure.name = self.plot_name
        self.document.add_root(self.figure)
    # END add_plot

    def update_plot(self) -> None:
        self.figure.height = self.plot_height
        self.figure.y_range.factors = self.plot_data['measure'].to_list()[::-1]
    # END update_plot
# END CLASS CategoryBarsPlot
