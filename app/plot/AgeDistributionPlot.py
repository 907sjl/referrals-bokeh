"""
AgeDistributionPlot.py
Class that represents a distribution plot of referrals by age bins.
https://907sjl.github.io/
"""

from bokeh.document import Document
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.ranges import FactorRange, Range1d
from bokeh.models.annotations import HTMLLabelSet
from bokeh.core.property.vectorization import Field

import pandas as pd

from datetime import datetime

import model.WaitTimes as wt
import app.common as v


class AgeDistributionPlot:

    def __init__(self,
                 doc: Document,
                 plot_name: str,
                 category_measure: str,
                 priorities: list[str],
                 bar_color_map: Field,
                 data_point_color_map: Field,
                 plot_width: int = 500,
                 plot_height: int = 180,
                 include_curve: bool = False):

        self.document = doc
        self.figure = None
        self.distribution_y_range = None
        self.plot_name = plot_name
        self.categories = ['7d', '14d', '30d', '60d', '90d', '>90d']
        self.bar_color_map = bar_color_map
        self.data_point_color_map = data_point_color_map
        self.plot_width = plot_width
        self.plot_height = plot_height
        self.category_measure = category_measure
        self.priorities = priorities
        self.distribution_data = {}
        self.distribution_plot_data = pd.DataFrame()
        self.distribution_plot_data_source = None
        self.curve_plot_data = pd.DataFrame()
        self.curve_plot_data_source = None
        self.inside_labels_plot_data = pd.DataFrame()
        self.inside_labels_plot_data_source = None
        self.outside_labels_plot_data = pd.DataFrame()
        self.outside_labels_plot_data_source = None
        self.include_curve = include_curve
        self.under_labels_plot_data = pd.DataFrame()
        self.under_labels_plot_data_source = None
        self.over_labels_plot_data = pd.DataFrame()
        self.over_labels_plot_data_source = None
    # END __init__

    def load_clinic_data(self, month: datetime, clinic: str) -> None:

        # Build list of distribution counts in same order as categories
        all_counts = []
        for category in self.categories:
            category_count = 0
            for priority in self.priorities:
                category_count += wt.get_clinic_distribution_count(month,
                                                                   clinic,
                                                                   self.category_measure,
                                                                   category,
                                                                   priority)
            all_counts.append(category_count)

        # Create a dataframe with the referral distribution data
        self.distribution_data = {'category': self.categories, 'referral_count': all_counts}
    # END load_clinic_data

    def create_plot_data(self) -> None:

        max_data_value = max(self.distribution_data['referral_count'])
        self.distribution_y_range = Range1d(0, ((24.0 / self.plot_height) + 1.0) * max_data_value)

        distribution_dataframe = pd.DataFrame(self.distribution_data, index=list(range(0, len(self.categories))))

        # If a data point is more than 84% of the range the label will be inside the bar
        distribution_dataframe['range_ratio'] = distribution_dataframe.referral_count / max_data_value
        distribution_dataframe.loc[(distribution_dataframe.range_ratio > 0.84), ['bar_data_label_placement']] = 'inside'
        distribution_dataframe.loc[
            (distribution_dataframe.range_ratio <= 0.84), ['bar_data_label_placement']] = 'outside'

        # Create the data label text
        distribution_dataframe['bar_data_point_label'] = (
            distribution_dataframe['referral_count'].apply(lambda x: str(x)))

        # The inside and outside aligned labels must be in separate label sets
        self.inside_labels_plot_data = (
            distribution_dataframe.loc[(distribution_dataframe['bar_data_label_placement'] == 'inside')])
        if self.inside_labels_plot_data_source is None:
            self.inside_labels_plot_data_source = ColumnDataSource(self.inside_labels_plot_data)
        else:
            self.inside_labels_plot_data_source.data = self.inside_labels_plot_data.to_dict(orient="list")

        self.outside_labels_plot_data = (
            distribution_dataframe.loc[(distribution_dataframe['bar_data_label_placement'] == 'outside')])
        if self.outside_labels_plot_data_source is None:
            self.outside_labels_plot_data_source = ColumnDataSource(self.outside_labels_plot_data)
        else:
            self.outside_labels_plot_data_source.data = self.outside_labels_plot_data.to_dict(orient="list")

        # Draw the curve if included
        if self.include_curve:
            # Curve ratios
            total_counts = sum(self.distribution_data['referral_count'])
            distribution_dataframe['cumulative_count'] = distribution_dataframe['referral_count'].cumsum()
            if total_counts > 0:
                distribution_dataframe['throughput_ratio'] = distribution_dataframe.cumulative_count / total_counts
            else:
                distribution_dataframe['throughput_ratio'] = 0.0

            # If a data point is more than 84% of the range the label will be under the line
            # Also try some basic collision avoidance between labels
            distribution_dataframe.loc[(distribution_dataframe.throughput_ratio > 0.84),
                                       ['curve_data_label_placement']] = 'over'
            idx = ((distribution_dataframe['throughput_ratio'] <= 0.84)
                   & ((distribution_dataframe['throughput_ratio'] + 0.25)
                      <= (distribution_dataframe['range_ratio'] - 0.03)))
            distribution_dataframe.loc[idx, 'curve_data_label_placement'] = 'under'
            idx = ((distribution_dataframe['throughput_ratio'] <= 0.84)
                   & ((distribution_dataframe['throughput_ratio'] + 0.25)
                      > (distribution_dataframe['range_ratio'] - 0.03)))
            distribution_dataframe.loc[idx, 'curve_data_label_placement'] = 'over'

            # Create the curve data label text
            distribution_dataframe['curve_data_point_label'] = (
                distribution_dataframe['throughput_ratio'].apply(lambda x: str(v.half_up_int(x * 100.0)) + '%'))

            # The over and under aligned labels must be in separate label sets
            self.under_labels_plot_data = (
                distribution_dataframe.loc[(distribution_dataframe['curve_data_label_placement'] == 'under')])
            if self.under_labels_plot_data_source is None:
                self.under_labels_plot_data_source = ColumnDataSource(self.under_labels_plot_data)
            else:
                self.under_labels_plot_data_source.data = self.under_labels_plot_data.to_dict(orient="list")

            self.over_labels_plot_data = (
                distribution_dataframe.loc[(distribution_dataframe['curve_data_label_placement'] == 'over')])
            if self.over_labels_plot_data_source is None:
                self.over_labels_plot_data_source = ColumnDataSource(self.over_labels_plot_data)
            else:
                self.over_labels_plot_data_source.data = self.over_labels_plot_data.to_dict(orient="list")
        # END if include_curve

        # Store the distribution data for rendering later
        self.distribution_plot_data = distribution_dataframe

        # Either add or update a Bokeh connected data source
        if self.distribution_plot_data_source is None:
            self.distribution_plot_data_source = ColumnDataSource(distribution_dataframe)
        else:
            self.distribution_plot_data_source.data = distribution_dataframe.to_dict(orient="list")
    # END create_plot_data

    def add_plot(self) -> None:

        # Create a categorical range and plot area for the histogram
        distribution_x_range = FactorRange(factors=self.distribution_data['category'])
        self.figure = figure(height=self.plot_height,
                             width=self.plot_width,
                             title=None,
                             toolbar_location=None,
                             x_range=distribution_x_range,
                             y_range=self.distribution_y_range,
                             output_backend="svg")

        # Create histogram bars
        self.figure.vbar(x='category',
                         top='referral_count',
                         color=self.bar_color_map,
                         width=1.0,
                         source=self.distribution_plot_data_source)

        # Create the data point labels and add them to the plot
        distribution_inside_align_label_set = HTMLLabelSet(y='referral_count',
                                                           y_offset=-22,
                                                           x='category',
                                                           text='bar_data_point_label',
                                                           level='glyph',
                                                           text_align='center',
                                                           text_baseline='bottom',
                                                           text_font_size='12pt',
                                                           text_color=self.data_point_color_map,
                                                           source=self.inside_labels_plot_data_source)
        self.figure.add_layout(distribution_inside_align_label_set)
        distribution_outside_align_label_set = HTMLLabelSet(y='referral_count',
                                                            y_offset=18,
                                                            x='category',
                                                            text='bar_data_point_label',
                                                            level='glyph',
                                                            text_align='center',
                                                            text_baseline='top',
                                                            text_font_size='12pt',
                                                            text_color='#000000',
                                                            source=self.outside_labels_plot_data_source)
        self.figure.add_layout(distribution_outside_align_label_set)

        # Draw the curve if included
        if self.include_curve:
            # Secondary y axis
            self.figure.extra_y_ranges['curve'] = Range1d(-0.25, 1.0 + (0.00078125 * self.plot_height))

            # Draw the curve line
            self.figure.line(x='category',
                             y='throughput_ratio',
                             line_width=2,
                             line_dash="dashed",
                             y_range_name='curve',
                             line_color='#666666',
                             source=self.distribution_plot_data_source)

            # Create data point markers
            self.figure.circle(x='category',
                               y='throughput_ratio',
                               size=4,
                               line_color='#666666',
                               fill_color='#666666',
                               y_range_name='curve',
                               source=self.distribution_plot_data_source)

            # Create the data point labels and add them to the plot
            distribution_under_align_label_set = HTMLLabelSet(y='throughput_ratio',
                                                              y_offset=-30,
                                                              x='category',
                                                              text='curve_data_point_label',
                                                              level='glyph',
                                                              text_align='center',
                                                              text_baseline='bottom',
                                                              text_font_size='12pt',
                                                              y_range_name='curve',
                                                              source=self.under_labels_plot_data_source)
            self.figure.add_layout(distribution_under_align_label_set)
            distribution_over_align_label_set = HTMLLabelSet(y='throughput_ratio',
                                                             y_offset=26,
                                                             x='category',
                                                             text='curve_data_point_label',
                                                             level='glyph',
                                                             text_align='center',
                                                             text_baseline='top',
                                                             text_font_size='12pt',
                                                             y_range_name='curve',
                                                             source=self.over_labels_plot_data_source)
            self.figure.add_layout(distribution_over_align_label_set)
        # END if include_curve

        # Set style configs
        self.figure.background_fill_alpha = 0
        self.figure.outline_line_alpha = 0
        self.figure.border_fill_alpha = 0

        self.figure.xgrid.grid_line_color = None
        self.figure.ygrid.grid_line_dash = 'dotted'

        self.figure.yaxis.major_label_text_font_size = '12pt'
        self.figure.yaxis.major_label_text_color = '#000000'
        self.figure.yaxis.axis_line_alpha = 0
        self.figure.yaxis.major_tick_line_alpha = 0
        self.figure.yaxis.minor_tick_line_alpha = 0
        self.figure.yaxis.major_label_standoff = 4

        self.figure.xaxis.axis_line_alpha = 0

        self.figure.xaxis.major_tick_line_alpha = 0
        self.figure.xaxis.minor_tick_line_alpha = 0
        self.figure.xaxis.major_tick_in = 0
        self.figure.xaxis.major_tick_out = 0
        self.figure.xaxis.minor_tick_in = 0
        self.figure.xaxis.minor_tick_out = 0

        self.figure.xaxis.major_label_text_font_size = '12pt'
        self.figure.xaxis.major_label_text_color = '#000000'
        self.figure.xaxis.major_label_standoff = 0
        self.figure.xaxis.major_label_text_baseline = 'top'
        self.figure.xaxis.axis_label_standoff = 0
        self.figure.xaxis.axis_label_text_baseline = 'top'

        self.figure.flow_mode = 'inline'
        self.figure.sizing_mode = 'fixed'
        self.figure.width_policy = 'fixed'

        self.figure.name = self.plot_name
        self.document.add_root(self.figure)
    # END add_plot

    def update_plot(self) -> None:
        self.figure.y_range.start = self.distribution_y_range.start
        self.figure.y_range.end = self.distribution_y_range.end
# END CLASS AgeDistributionPlot
