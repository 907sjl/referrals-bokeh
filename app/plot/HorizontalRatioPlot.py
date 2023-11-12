import pandas as pd

from bokeh.document import Document
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.ranges import FactorRange
from bokeh.models.annotations import HTMLLabelSet

from datetime import datetime

import model.WaitTimes as wt
import model.CRM as c
import model.DSMs as d
import app.common as v


class HorizontalRatioPlot:

    def __init__(self,
                 doc: Document,
                 plot_name: str,
                 numerator_measure: str,
                 numerator_name: str,
                 numerator2_measure: str,
                 numerator2_name: str,
                 denominator_measure: str,
                 denominator_name: str,
                 plot_width: int = 280,
                 plot_height: int = 56):
        self.document = doc
        self.figure = None
        self.volume_y_range = None
        self.plot_name = plot_name
        self.numerator_measure = numerator_measure
        self.numerator_name = numerator_name
        self.numerator2_measure = numerator2_measure
        self.numerator2_name = numerator2_name
        self.denominator_measure = denominator_measure
        self.denominator_name = denominator_name
        self.ratio_data = {}
        self.plot_data = pd.DataFrame()
        self.plot_data_source = None
        self.left_label_data = pd.DataFrame()
        self.left_label_data_source = None
        self.right_label_data = pd.DataFrame()
        self.right_label_data_source = None
        self.plot_width = plot_width
        self.plot_height = plot_height
    # END __init__

    def load_clinic_data(self, month: datetime, clinic: str) -> None:
        if self.numerator_measure == 'Patients with DSM and CRM Referrals After 90d':
            pk = d
        else:
            pk = c
        numerator_count = v.half_up_int(
            pk.get_clinic_count_measure(month, clinic, self.numerator_measure))

        if self.denominator_measure == 'Patients with DSMs After 90d':
            pk = d
        else:
            pk = wt
        denominator_count = v.half_up_int(
            pk.get_clinic_count_measure(month, clinic, self.denominator_measure))

        if self.numerator2_measure != '':
            numerator2_count = v.half_up_int(
                wt.get_clinic_count_measure(month, clinic, self.numerator2_measure))
        else:
            numerator2_count = 0

        self.ratio_data = {self.numerator_name: numerator_count,
                           self.denominator_name: denominator_count,
                           self.numerator2_name: numerator2_count}
    # END load_clinic_data

    def create_plot_data(self) -> None:
        # Data for volume measures
        volume_measures = [self.denominator_name, self.numerator_name]
        if self.numerator2_name != '':
            volume_measures.append(self.numerator2_name)

        volume_values = [self.ratio_data[self.denominator_name], self.ratio_data[self.numerator_name]]
        if self.numerator2_name != '':
            volume_values.append(self.ratio_data[self.numerator2_name])

        bar_colors = ['#808080', '#EB895F']
        if self.numerator2_name != '':
            bar_colors.append('#EB895F')

        plot_dict = {'measure': volume_measures,
                     'value': volume_values,
                     'bar_color': bar_colors}
        self.plot_data = pd.DataFrame.from_dict(plot_dict, orient='columns')

        # If a data point is more than 75% of the range the label will be right-aligned inside the bar
        max_data_value = max(volume_values)
        self.plot_data['range_ratio'] = self.plot_data['value'] / max_data_value
        self.plot_data.loc[(self.plot_data['range_ratio'] > 0.75), ['data_label_align']] = 'right'
        self.plot_data.loc[(self.plot_data['range_ratio'] <= 0.75), ['data_label_align']] = 'left'

        # Create the data label text
        self.plot_data['data_point_label'] = self.plot_data['value'].apply(lambda x: str(x))

        if self.plot_data_source is None:
            self.plot_data_source = ColumnDataSource(self.plot_data)
        else:
            self.plot_data_source.data = self.plot_data.to_dict(orient="list")

        # The left and right aligned labels must be in separate label sets
        self.left_label_data = self.plot_data.loc[(self.plot_data['data_label_align'] == 'left')]
        if self.left_label_data_source is None:
            self.left_label_data_source = ColumnDataSource(self.left_label_data)
        else:
            self.left_label_data_source.data = self.left_label_data.to_dict(orient="list")

        self.right_label_data = self.plot_data.loc[(self.plot_data['data_label_align'] == 'right')]
        if self.right_label_data_source is None:
            self.right_label_data_source = ColumnDataSource(self.right_label_data)
        else:
            self.right_label_data_source.data = self.right_label_data.to_dict(orient="list")
    # END create_plot_data

    def add_plot(self) -> None:
        if (self.numerator2_name != '') and (self.plot_height < 78):
            self.plot_height = 78

        # Reverse the measures for the chart range so that the first measure is on top (higher y value)
        self.volume_y_range = FactorRange(factors=self.plot_data['measure'].to_list()[::-1])

        # Create a plot area with the custom range, plot horizontal bars for each measure
        self.figure = figure(y_range=self.volume_y_range,
                             title=None,
                             toolbar_location=None,
                             height=self.plot_height,
                             width=280,
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
                                                   source=self.left_label_data_source)
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
                                                    source=self.right_label_data_source)
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

    def change_plot(self) -> None:
        self.figure.height = self.plot_height
        self.figure.y_range.factors = self.plot_data['measure'].to_list()[::-1]
    # END update_plot
# END CLASS HorizontalRatioPlot
