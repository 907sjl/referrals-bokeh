"""
SeenRatioPlot.py
Class that represents a pie chart representing the percent of referrals seen or scheduled.
https://907sjl.github.io/

Classes:
    SeenRatioPlot - Adds a donut chart to a Bokeh document representing the percentage of referrals seen and scheduled
"""

from bokeh.document import Document
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.ranges import Range1d
from bokeh.models.annotations import HTMLLabelSet

import pandas as pd

from datetime import datetime

from math import pi

from numpy import cumsum, cos, sin

import model.WaitTimes as wt
import app.common as v


class SeenRatioPlot:
    """
    Class that represents a donut chart in a Bokeh document representing the percentage of referrals seen and scheduled

    Public Methods:
        load_clinic_data - Loads the data used to render visualizations.
        create_plot_data - Creates or updates the Bokeh ColumnDataSource using the clinic data collected.
        add_plot - Creates the figure and models that render the visual.
    """

    def __init__(self,
                 doc: Document,
                 plot_name: str,
                 denominator_measure: str,
                 seen_measure: str,
                 scheduled_measure: str,
                 neither_measure: str,
                 plot_width: int = 300,
                 plot_height: int = 100):
        """
        Initialize instances.
        :param doc: The Bokeh document for an instance of this application
        :param plot_name: The name of the plot in the HTML document
        :param denominator_measure: The name of the measure used to get the denominator count
        :param seen_measure: The name of the measure used to get the count of referrals seen
        :param scheduled_measure: The name of the measure used to get the count of referrals scheduled
        :param neither_measure: The name of the measure used to get the count of remaining referrals
        :param plot_width: The width of the resulting plot in pixels
        :param plot_height: The height of the resulting plot in pixels
        """

        self.document = doc
        self.plot_name = plot_name
        self.denominator_measure = denominator_measure
        self.denominator = 0
        self.seen_measure = seen_measure
        self.scheduled_measure = scheduled_measure
        self.neither_measure = neither_measure
        self.ratio_measures = ['Seen', 'Scheduled', 'Neither']
        self.slice_colors = ['#55BCFF', '#EAEA6A', '#B3B0AD']
        self.ratio_data = {}
        self.plot_width = plot_width
        self.plot_height = plot_height
        self.plot_data = pd.DataFrame()
        self.plot_data_source = None
        self.plot_center_top_labels_data = pd.DataFrame()
        self.plot_center_top_labels_data_source = None
        self.plot_center_bottom_labels_data = pd.DataFrame()
        self.plot_center_bottom_labels_data_source = None
        self.plot_left_middle_labels_data = pd.DataFrame()
        self.plot_left_middle_labels_data_source = None
        self.plot_right_middle_labels_data = pd.DataFrame()
        self.plot_right_middle_labels_data_source = None
        self.seen_ratio_label_data = {}
        self.seen_ratio_label_data_source = None
    # END __init__

    def load_clinic_data(self, month: datetime, clinic: str) -> None:
        """
        Loads the data used to render visualizations.
        :param month: The month to query data from
        :param clinic: The name of the clinic to query data for
        """

        ratio_values = [wt.get_clinic_count_measure(month, clinic, self.seen_measure),
                        wt.get_clinic_count_measure(month, clinic, self.scheduled_measure),
                        wt.get_clinic_count_measure(month, clinic, self.neither_measure)]
        self.denominator = wt.get_clinic_count_measure(month, clinic, self.denominator_measure)
        self.ratio_data = {'measure': self.ratio_measures,
                           'value': ratio_values,
                           'color': self.slice_colors}
    # END load_clinic_data

    def create_plot_data(self) -> None:
        """Creates or updates the Bokeh ColumnDataSource using the clinic data collected."""

        # Calculate the size of the donut
        if self.plot_height < self.plot_width:
            outer_radius = self.plot_height / 2.0
        else:
            outer_radius = self.plot_width / 2.0
        outer_radius = outer_radius - (self.plot_height / 7.0)

        # Create a dataframe to hold potting data for each slice of the pie chart
        seen_ratio_dataframe = pd.DataFrame.from_dict(self.ratio_data)
        seen_ratio_dataframe = seen_ratio_dataframe.loc[seen_ratio_dataframe['value'] > 0]
        if self.denominator > 0:
            seen_ratio_dataframe['angle_increment'] = seen_ratio_dataframe['value'] / self.denominator * 2 * pi
        else:
            seen_ratio_dataframe['angle_increment'] = 0
        seen_ratio_dataframe['ending_plot_angle'] = cumsum(seen_ratio_dataframe['angle_increment'].values)
        seen_ratio_dataframe['starting_plot_angle'] = 0
        seen_ratio_dataframe.loc[1:, ['starting_plot_angle']] = seen_ratio_dataframe.shift(1).ending_plot_angle

        # Place the labels in the center of each slice in a circle around the outside edge of the pie wedges
        if self.denominator > 0:
            seen_ratio_dataframe['label_angle'] = (
                    seen_ratio_dataframe['ending_plot_angle'] - seen_ratio_dataframe['angle_increment'].div(2))
            seen_ratio_dataframe['label_y_pos'] = (
                round(sin(seen_ratio_dataframe['label_angle']) * (outer_radius + 4), 2))
            seen_ratio_dataframe['label_x_pos'] = (
                round(cos(seen_ratio_dataframe['label_angle']) * (outer_radius + 4), 2))
        else:
            seen_ratio_dataframe['label_angle'] = 0
            seen_ratio_dataframe['label_y_pos'] = 0
            seen_ratio_dataframe['label_x_pos'] = 0

        # Labels on the left of the pie are right-aligned, on the right of the pie are left-aligned
        # Labels on the top are positioned relative to the bottom of the label
        # Labels on the bottom are positioned relative to the top of the label
        if self.denominator > 0:
            seen_ratio_dataframe['label_align'] = 'center'
            seen_ratio_dataframe['label_baseline'] = 'middle'
            seen_ratio_dataframe.loc[(seen_ratio_dataframe.label_angle < (0.125 * 2 * pi)), ['label_align']] = 'left'
            seen_ratio_dataframe.loc[(seen_ratio_dataframe.label_angle > (0.875 * 2 * pi)), ['label_align']] = 'left'
            idx = ((seen_ratio_dataframe.label_angle >= (0.375 * 2 * pi))
                   & (seen_ratio_dataframe.label_angle <= (0.625 * 2 * pi)))
            seen_ratio_dataframe.loc[idx, ['label_align']] = 'right'
            idx = ((seen_ratio_dataframe.label_angle >= (0.125 * 2 * pi))
                   & (seen_ratio_dataframe.label_angle <= (0.375 * 2 * pi)))
            seen_ratio_dataframe.loc[idx, ['label_baseline']] = 'bottom'
            idx = ((seen_ratio_dataframe.label_angle >= (0.625 * 2 * pi))
                   & (seen_ratio_dataframe.label_angle <= (0.875 * 2 * pi)))
            seen_ratio_dataframe.loc[idx, ['label_baseline']] = 'top'
        else:
            seen_ratio_dataframe['label_align'] = 'left'

        # Create the data point label text
        if self.denominator > 0:
            seen_ratio_dataframe['data_point_label'] = seen_ratio_dataframe['value'].apply(lambda x: str(x))
            idx = (seen_ratio_dataframe['value'] == 0)
            seen_ratio_dataframe.loc[idx, 'data_point_label'] = ''
        else:
            seen_ratio_dataframe['data_point_label'] = ''

        # Store the plot data to be used for rendering
        self.plot_data = seen_ratio_dataframe

        # Either create or update a column data source for the donut chart
        if self.plot_data_source is None:
            self.plot_data_source = ColumnDataSource(seen_ratio_dataframe)
        else:
            self.plot_data_source.data = seen_ratio_dataframe.to_dict(orient="list")

        # Left aligned labels must be in a separate label set layout from the right aligned labels
        idx = (seen_ratio_dataframe.label_align == 'center') & (seen_ratio_dataframe.label_baseline == 'top')
        self.plot_center_top_labels_data = seen_ratio_dataframe.loc[idx]
        if self.plot_center_top_labels_data_source is None:
            self.plot_center_top_labels_data_source = ColumnDataSource(self.plot_center_top_labels_data)
        else:
            self.plot_center_top_labels_data_source.data = self.plot_center_top_labels_data.to_dict(orient="list")

        idx = (seen_ratio_dataframe.label_align == 'center') & (seen_ratio_dataframe.label_baseline == 'bottom')
        self.plot_center_bottom_labels_data = seen_ratio_dataframe.loc[idx]
        if self.plot_center_bottom_labels_data_source is None:
            self.plot_center_bottom_labels_data_source = ColumnDataSource(self.plot_center_bottom_labels_data)
        else:
            self.plot_center_bottom_labels_data_source.data = self.plot_center_bottom_labels_data.to_dict(orient="list")

        idx = (seen_ratio_dataframe.label_align == 'left') & (seen_ratio_dataframe.label_baseline == 'middle')
        self.plot_left_middle_labels_data = seen_ratio_dataframe.loc[idx]
        if self.plot_left_middle_labels_data_source is None:
            self.plot_left_middle_labels_data_source = ColumnDataSource(self.plot_left_middle_labels_data)
        else:
            self.plot_left_middle_labels_data_source.data = self.plot_left_middle_labels_data.to_dict(orient="list")

        idx = (seen_ratio_dataframe.label_align == 'right') & (seen_ratio_dataframe.label_baseline == 'middle')
        self.plot_right_middle_labels_data = seen_ratio_dataframe.loc[idx]
        if self.plot_right_middle_labels_data_source is None:
            self.plot_right_middle_labels_data_source = ColumnDataSource(self.plot_right_middle_labels_data)
        else:
            self.plot_right_middle_labels_data_source.data = self.plot_right_middle_labels_data.to_dict(orient="list")

        # Create a centered label with the ratio
        seen_count = self.ratio_data['value'][0]
        if self.denominator > 0:
            seen_ratio = seen_count / self.denominator
        else:
            seen_ratio = 0.0

        self.seen_ratio_label_data = {'label_x_pos': [0],
                                      'label_y_pos': [0],
                                      'data_point_label': [str(v.half_up_int((seen_ratio * 100.0))) + r'%']}
        if self.seen_ratio_label_data_source is None:
            self.seen_ratio_label_data_source = ColumnDataSource(data=self.seen_ratio_label_data)
        else:
            self.seen_ratio_label_data_source.data = self.seen_ratio_label_data
    # END create_plot_data

    def add_plot(self) -> None:
        """Creates the figure and models that render the visual."""

        x_axis_start = 0.0 - ((self.plot_width - 100.0) / 2.0)
        y_axis_start = 0.0 - (self.plot_height / 2.0)
        x_axis_distance = self.plot_width
        y_axis_distance = self.plot_height
        if self.plot_height < self.plot_width:
            outer_radius = self.plot_height / 2.0
        else:
            outer_radius = self.plot_width / 2.0
        outer_radius = outer_radius - (self.plot_height / 7.0)
        inner_radius = outer_radius - (self.plot_height / 7.0)

        # Create a plot area for the pie and labels
        seen_ratio_plot = figure(height=self.plot_height, width=self.plot_width, title=None, toolbar_location=None,
                                 x_range=Range1d(x_axis_start, x_axis_start + x_axis_distance),
                                 y_range=Range1d(y_axis_start, y_axis_start + y_axis_distance),
                                 output_backend="svg")

        # Create pie wedges for each data point
        seen_ratio_plot.annular_wedge(x=0, y=0, inner_radius=inner_radius, outer_radius=outer_radius,
                                      start_angle='starting_plot_angle', end_angle='ending_plot_angle',
                                      line_color="white", fill_color='color', source=self.plot_data_source,
                                      legend_group='measure')

        # Create label sets for left and right aligned labels and use HTML labels so that
        # browser renders the font in case svg doesn't work
        if self.plot_height < 140:
            label_size = '11pt'
        else:
            label_size = '12pt'

        seen_ratio_left_middle_align_label_set = HTMLLabelSet(x='label_x_pos',
                                                              y='label_y_pos',
                                                              text='data_point_label',
                                                              level='glyph',
                                                              text_align='left',
                                                              text_baseline='middle',
                                                              text_color='#605E5C',
                                                              text_font_size=label_size,
                                                              source=self.plot_left_middle_labels_data_source)
        seen_ratio_plot.add_layout(seen_ratio_left_middle_align_label_set)
        seen_ratio_right_middle_align_label_set = HTMLLabelSet(x='label_x_pos',
                                                               y='label_y_pos',
                                                               text='data_point_label',
                                                               level='glyph',
                                                               text_align='right',
                                                               text_baseline='middle',
                                                               text_color='#605E5C',
                                                               text_font_size=label_size,
                                                               source=self.plot_right_middle_labels_data_source)
        seen_ratio_plot.add_layout(seen_ratio_right_middle_align_label_set)
        seen_ratio_center_top_align_label_set = HTMLLabelSet(x='label_x_pos',
                                                             y='label_y_pos',
                                                             text='data_point_label',
                                                             level='glyph',
                                                             text_align='center',
                                                             text_baseline='top',
                                                             text_color='#605E5C',
                                                             text_font_size=label_size,
                                                             source=self.plot_center_top_labels_data_source)
        seen_ratio_plot.add_layout(seen_ratio_center_top_align_label_set)
        seen_ratio_center_bottom_align_label_set = HTMLLabelSet(x='label_x_pos',
                                                                y='label_y_pos',
                                                                text='data_point_label',
                                                                level='glyph',
                                                                text_align='center',
                                                                text_baseline='bottom',
                                                                text_color='#605E5C',
                                                                text_font_size=label_size,
                                                                source=self.plot_center_bottom_labels_data_source)
        seen_ratio_plot.add_layout(seen_ratio_center_bottom_align_label_set)

        if self.plot_height < 140:
            center_label_size = '12pt'
        else:
            center_label_size = '16pt'

        seen_ratio_center_label_set = HTMLLabelSet(x='label_x_pos',
                                                   y='label_y_pos',
                                                   text='data_point_label',
                                                   level='glyph',
                                                   text_align='center',
                                                   text_baseline='middle',
                                                   text_color='#605E5C',
                                                   text_font_size=center_label_size,
                                                   source=self.seen_ratio_label_data_source)
        seen_ratio_plot.add_layout(seen_ratio_center_label_set)

        # Set style configs
        seen_ratio_plot.legend.location = "right"
        seen_ratio_plot.legend.background_fill_alpha = 0.0
        seen_ratio_plot.legend.border_line_width = 0
        seen_ratio_plot.legend.label_text_font_size = label_size

        seen_ratio_plot.background_fill_alpha = 0
        seen_ratio_plot.outline_line_alpha = 0
        seen_ratio_plot.border_fill_alpha = 0
        seen_ratio_plot.axis.axis_label = None
        seen_ratio_plot.axis.visible = False
        seen_ratio_plot.grid.grid_line_color = None
        seen_ratio_plot.flow_mode = 'inline'
        seen_ratio_plot.sizing_mode = 'fixed'
        seen_ratio_plot.width_policy = 'fixed'

        # Add to document data, this figure name must be embedded to avoid a JS error
        seen_ratio_plot.name = self.plot_name
        self.document.add_root(seen_ratio_plot)
    # END add_plot
# END CLASS SeenRatioPlot
