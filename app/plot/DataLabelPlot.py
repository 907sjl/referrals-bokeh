"""
DataLabelPlot.py
Class that represents a collection of data driven HTML labels.
https://907sjl.github.io/
"""

from bokeh.document import Document
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.ranges import Range1d
from bokeh.models.annotations import LabelSet


class LabelDataSource:

    def __init__(self,
                 doc: Document,
                 plot_name: str):
        self.document = doc
        self.plot_name = plot_name
        self.label_data = {'empty': ['']}
        self.plot_data_source = None
    # END __init__

    def update_label(self,
                     name: str,
                     value: str) -> None:
        self.label_data[name] = [value]
    # END update_label

    def update_label_style(self,
                           name: str,
                           class_name: str) -> None:
        self.label_data['CLASS:' + name] = [class_name]
    # END update_label

    def update_plot_data(self):
        if self.plot_data_source is None:
            self.plot_data_source = ColumnDataSource(self.label_data)
        else:
            self.plot_data_source.data = self.label_data
    # END update_plot_data

    def add_plot(self):
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
            var text_template;
            var class_name;
            var class_template;
            var element;
            for (var name in source.data) {
                if ((name != "empty") && (name.substring(0, 6) != "CLASS:") && source.data.hasOwnProperty(name)) {
                    text_data = source.data[name][0];
                    element = document.getElementById(name);
                    
                    if (element.hasAttribute("data_label_template")) { 
                        text_template = element.getAttribute("data_label_template");
                    } 
                    else {
                        text_template = element.textContent;
                        element.setAttribute("data_label_template", text_template);
                    } 
                    element.textContent = text_template.replace("[*label*]", text_data);
                    
                    if (source.data.hasOwnProperty("CLASS:" + name)) {
                        class_name = source.data["CLASS:" + name][0];
                        if (element.hasAttribute("data_label_class_template")) { 
                            class_template = element.getAttribute("data_label_class_template");
                        } 
                        else {
                            class_template = element.getAttribute("class");
                            element.setAttribute("data_label_class_template", class_template);
                        } 
                        element.setAttribute("class", class_template.replace("[*class*]", class_name));
                    }
                }
            }
        """
        callback = CustomJS(args=dict(source=self.plot_data_source), code=code)
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
# END CLASS LabelDataSource


class CallbackLabelPlot:

    def __init__(self,
                 doc: Document,
                 label_data_source: LabelDataSource,
                 plot_name: str,
                 label_text: str,
                 class_name: str = ''):

        self.document = doc
        self.label_data_source = label_data_source
        self.plot_name = plot_name
        self.label_text = label_text
        self.class_name = class_name

        label_data_source.update_label(plot_name, label_text)
        if class_name > '':
            label_data_source.update_label_style(plot_name, class_name)
    # END __init__

    def set_label_text(self,
                       value: str) -> None:
        self.label_data_source.update_label(self.plot_name, value)
    # END set_label_text

    def set_label_style(self,
                        class_name: str) -> None:
        self.label_data_source.update_label_style(self.plot_name, class_name)
    # END set_label_text
# END CLASS CallbackLabelPlot
