"""
DataTablePlot.py
Class that represents a data driven HTML table.
https://907sjl.github.io/

Classes:
    DataTablePlot - Adds an HTML data driven table to a Bokeh document
"""

import pandas as pd

from pandas import DataFrame

from bokeh.document import Document
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.ranges import Range1d
from bokeh.models.annotations import LabelSet


class DataTablePlot:
    """
    Class that represents a data driven HTML table.  It renders the table using a javascript
    callback.  The actual plot for instances of this class is 1 pixel that should be embedded as
    hidden and floating.

    Public Methods:
        create_plot_data - Creates or updates the Bokeh ColumnDataSource using the clinic data collected.
        add_plot - Creates the figure and models that render the visual.
    """

    def __init__(self,
                 doc: Document,
                 plot_name: str,
                 columns: dict[str, list[str]]):
        """
        Initialize instances.
        :param doc: The Bokeh document for an instance of this application
        :param plot_name: The name of the plot in the HTML document
        :param columns: A dictionary with the list of column names in the table and the list of column css classes
        """
        self.document = doc
        self.plot_name = plot_name
        self.columns = columns
        self.ratio_data = {}
        self.plot_data = pd.DataFrame()
        self.plot_data_source = None
    # END __init__

    def create_plot_data(self, df: DataFrame) -> None:
        """Creates or updates the Bokeh ColumnDataSource using the given DataFrame with clinic data."""

        df['empty'] = ''
        self.plot_data = df
        if self.plot_data_source is None:
            self.plot_data_source = ColumnDataSource(self.plot_data)
        else:
            self.plot_data_source.data = self.plot_data
    # END update_plot_data

    def add_plot(self) -> None:
        """Creates the figure and models that render the visual."""

        label_plot = figure(title=None,
                            toolbar_location=None,
                            min_border=0,
                            y_range=Range1d(0, 0),
                            x_range=Range1d(0, 0),
                            x_axis_type=None,
                            y_axis_type=None,
                            height=0, width=0,
                            output_backend="svg")

        label = LabelSet(x=0, y=0,
                         source=self.plot_data_source,
                         text='empty',
                         visible=False)
        label_plot.add_layout(label)

        code = """
                var text_data;
                var text_value;
                var name;
                var cell_class;
                const element = document.getElementById(plot_name);
                const rows = source.data["empty"].length;
                text_data="";
                for (let i = 0; i < rows; i++) {
                    text_data += "<tr>";
                    for (let j = 0; j < columns.length; j++) {
                        name = columns[j];
                        cell_class = classes[j];
                        text_value = source.data[name][i];
                        text_data += "<td class='" + cell_class + "'>" + text_value + "</td>";
                    } 
                    text_data += "</tr>";
                } 
                element.innerHTML = text_data;
            """
        callback = CustomJS(args=dict(source=self.plot_data_source,
                                      plot_name=self.plot_name,
                                      columns=self.columns['columns'],
                                      classes=self.columns['classes']), code=code)
        self.plot_data_source.js_on_change('data', callback)
        self.document.js_on_event('document_ready', callback)

        # Set style configs
        label_plot.background_fill_alpha = 0
        label_plot.outline_line_alpha = 0
        label_plot.border_fill_alpha = 0
        label_plot.flow_mode = 'inline'
        label_plot.sizing_mode = 'fixed'
        label_plot.width_policy = 'fixed'

        label_plot.xgrid.grid_line_color = None
        label_plot.ygrid.grid_line_color = None

        label_plot.name = self.plot_name
        self.document.add_root(label_plot)
    # END add_plot
