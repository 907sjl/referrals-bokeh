from bokeh.document import Document
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LinearColorMapper
from bokeh.models.ranges import Range1d
from bokeh.models.annotations import HTMLLabelSet

import pandas as pd

from datetime import datetime

from math import pi

from numpy import cos, sin

import model.WaitTimes as wt
import app.common as v


class ProcessGaugePlot:

    def __init__(self,
                 doc: Document,
                 plot_name: str,
                 rate_measure: str,
                 target_measure: str,
                 gradient_color_map: LinearColorMapper,
                 plot_width: int = 140,
                 plot_height: int = 62):
        self.document = doc
        self.plot_name = plot_name
        self.rate_measure = rate_measure
        self.target_measure = target_measure
        self.gradient_color_map = gradient_color_map
        self.ratio_data = {}
        self.target_data = {}
        self.plot_width = plot_width
        self.plot_height = plot_height
        self.plot_data = pd.DataFrame()
        self.plot_data_source = None
        self.target_plot_data = pd.DataFrame()
        self.target_plot_data_source = None
        self.ratio_label_data = {}
        self.ratio_label_data_source = None
        self.outer_radius = 0.0
        self.inner_radius = 0.0
    # END __init__

    def load_clinic_data(self, month: datetime, clinic: str) -> None:
        urgent_pct = wt.get_clinic_rate_measure(month,
                                                clinic,
                                                self.rate_measure)
        urgent_target_pct = wt.get_clinic_rate_measure(month,
                                                       clinic,
                                                       self.target_measure)
        self.ratio_data = {'value': [urgent_pct / 100.0, 1.0]}
        self.target_data = {'value': [urgent_target_pct / 100.0]}
        self.ratio_label_data = {'value': v.half_up_int(urgent_pct)}
    # END load_clinic_data

    def create_plot_data(self) -> None:
        ratio_dataframe = pd.DataFrame(self.ratio_data, index=[0, 1])

        # The half-pie chart will render left-to-right, or backwards from normal angles
        ratio_dataframe['starting_plot_angle'] = pi - (ratio_dataframe.value * pi)

        # Add plot data for the remainder of the half-pie
        ratio_dataframe.loc[0:0, ['ending_plot_angle']] = pi
        ratio_dataframe.loc[1:1, ['ending_plot_angle']] = ratio_dataframe.starting_plot_angle.shift(1)

        # Give the remainder of the half-pie a value below the percentage range to trigger the low color
        ratio_dataframe.loc[1:1, ['value']] = -1

        # Store plot data for later rendering
        self.plot_data = ratio_dataframe

        # Either add or modify the plot data source for the gauge
        if self.plot_data_source is None:
            self.plot_data_source = ColumnDataSource(ratio_dataframe)
        else:
            self.plot_data_source.data = ratio_dataframe.to_dict(orient="list")

        # Calculate the size of the half-donut
        if self.plot_height < self.plot_width:
            self.outer_radius = self.plot_height - (0.15 * self.plot_height)
        else:
            self.outer_radius = self.plot_width / 2.0
        self.inner_radius = self.outer_radius - 20.0

        # Create plotting data for the target marker
        target_dataframe = pd.DataFrame(self.target_data, index=[0])

        # Calculate the location, vector, and length of the target line
        target_dataframe['starting_plot_angle'] = pi - (target_dataframe['value'] * pi)
        target_dataframe['target_y_pos'] = (
            round(sin(target_dataframe['starting_plot_angle']) * (self.inner_radius + (0.06 * self.plot_height)), 2))
        target_dataframe['target_x_pos'] = (
            round(cos(target_dataframe['starting_plot_angle']) * (self.inner_radius + (0.06 * self.plot_height)), 2))
        target_dataframe['target_ball_y_pos'] = (
            round(sin(target_dataframe['starting_plot_angle']) * (self.outer_radius + (0.06 * self.plot_height)), 2))
        target_dataframe['target_ball_x_pos'] = (
            round(cos(target_dataframe['starting_plot_angle']) * (self.outer_radius + (0.06 * self.plot_height)), 2))

        # Store plot data for later rendering
        self.target_plot_data = target_dataframe

        # Either add or modify the plot data source for the gauge
        if self.target_plot_data_source is None:
            self.target_plot_data_source = ColumnDataSource(target_dataframe)
        else:
            self.target_plot_data_source.data = target_dataframe.to_dict(orient="list")

        # Create a data source for the center, ratio label
        label_dataframe = pd.DataFrame(self.ratio_label_data, index=[0])
        label_dataframe['data_point_label'] = label_dataframe['value'].astype('str') + '%'
        label_dataframe['label_x_pos'] = 0
        label_dataframe['label_y_pos'] = -6.0

        # Store plot data for later rendering
        self.ratio_label_data = label_dataframe

        # Either add or modify the plot data source for the gauge
        if self.ratio_label_data_source is None:
            self.ratio_label_data_source = ColumnDataSource(label_dataframe)
        else:
            self.ratio_label_data_source.data = label_dataframe.to_dict(orient="list")
    # END create_plot_data

    def add_plot(self) -> None:
        x_axis_start = 0.0 - (self.plot_width / 2.0)
        y_axis_start = 0.0
        x_axis_distance = self.plot_width
        y_axis_distance = self.plot_height
        x_center = 0
        y_center = 0

        # Create a plot area for the pie and labels
        ratio_plot = figure(height=self.plot_height,
                            width=self.plot_width,
                            x_range=Range1d(x_axis_start, x_axis_start + x_axis_distance),
                            y_range=Range1d(y_axis_start, y_axis_start + y_axis_distance),
                            title=None,
                            toolbar_location=None,
                            match_aspect=True,
                            output_backend="svg")

        # Create pie wedges for each data point
        ratio_plot.annular_wedge(x=x_center,
                                 y=y_center,
                                 inner_radius=self.inner_radius,
                                 outer_radius=self.outer_radius,
                                 start_angle='starting_plot_angle',
                                 end_angle='ending_plot_angle',
                                 line_color="white",
                                 fill_color={'field': 'value', 'transform': self.gradient_color_map},
                                 source=self.plot_data_source)

        # Create a target line on the gauge
        ratio_plot.ray(x='target_x_pos',
                       y='target_y_pos',
                       angle='starting_plot_angle',
                       length=self.outer_radius - self.inner_radius,
                       line_color='#000000',
                       line_width=2,
                       source=self.target_plot_data_source)
        ratio_plot.circle(x='target_ball_x_pos',
                          y='target_ball_y_pos',
                          fill_color='#000000',
                          line_alpha=0,
                          radius=4,
                          radius_units='screen',
                          source=self.target_plot_data_source)

        center_label_set = HTMLLabelSet(x='label_x_pos',
                                        y='label_y_pos',
                                        text='data_point_label',
                                        level='glyph',
                                        text_align='center',
                                        text_baseline='bottom',
                                        text_color='#605E5C',
                                        text_font_size="14pt",
                                        source=self.ratio_label_data_source)
        ratio_plot.add_layout(center_label_set)

        # Set style configs
        ratio_plot.background_fill_alpha = 0
        ratio_plot.outline_line_alpha = 0
        ratio_plot.border_fill_alpha = 0
        ratio_plot.axis.axis_label = None
        ratio_plot.axis.visible = False
        ratio_plot.grid.grid_line_color = None
        ratio_plot.flow_mode = 'inline'
        ratio_plot.sizing_mode = 'fixed'
        ratio_plot.width_policy = 'fixed'

        # Add to document data, this figure name must be embedded to avoid a JS error
        ratio_plot.name = self.plot_name
        self.document.add_root(ratio_plot)
    # END add_plot
# END CLASS ProcessGaugePlot
