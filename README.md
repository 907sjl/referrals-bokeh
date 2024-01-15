< [Portfolio](https://907sjl.github.io) | [Full Report](pdf/Referral%20Process%20Measures%20Bokeh.pdf) | [GitHub Repository](https://github.com/907sjl/referrals-bokeh) | [Overview](https://907sjl.github.io/referrals-bokeh/referrals_report)    

One way to measure access to care is timeliness. Long delays to see a healthcare provider can speak to availability issues, either a lack of resources or inefficiencies that result in a less than optimal conversion of referrals into appointments. Long delays can also speak to accommodation issues or accessibility issues if patients have difficulty attending their scheduled appointments.
This project is an example of a report that I created to look at the process times for referred patients at specialty clinics. 

## Technology Stack
<img src="images/tech_stack.svg?raw=true" width="582" height="192" alt="SVG image: technology stack"/>    

These technologies are used by application layers that manage the data model, application content, and data visualization.    

<img src="images/app_layers.svg?raw=true" width="362" height="372" alt="SVG image: application layers"/>    

### HTML, JavaScript, and CSS    
Three common and pervasive technologies come together to provide an analytics developer with the tools necessary to create any layout they can imagine. 
HTML provides the scaffolding and CSS shapes and styles the layout. JavaScript allows for custom and data-driven logic to fine-tune the final product 
and to implement interactive features. These tools are general purpose. They are vendor agnostic. They have been built to support an industry and are 
supported by a worldwide community of practitioners. Any knowledge about how to apply these technologies is freely available and only a web search away.    

Deliverables created with HTML and CSS are very readable from text files in your source repository. They work well with version control platforms (like Git). 
As does JavaScript, of course. Working with these technologies frees you from the artificially imposed limitations of BI tools that only provide the flexibility 
that they have been created to provide.    

### Python and Pandas    
Flexibility and freedom also define another technology underlying this example, Python. Python is a general purpose programming language used to create 
complex applications, to be the glue that integrates other software platforms, or to automate tasks with scripts. Using Python to create your analytic 
deliverable ensures that you will have opportunities to automate tasks such as data refresh and report generation. BI tools limit your automation possibilities to 
predetermined use cases. A report or dashboard developed using Python can be automated using Python. There are few licensing concerns with Python itself 
and no paid subscriptions necessary.    

Pandas is a data analysis library for Python programs. It provides data aggregation, statistical analysis, and data manipulation within the Python framework. 
Using Python and Pandas together frees you from the limitations of software packages. You may sacrifice 
the convenience of connectors for specific data sources, depending on the availability of Python libraries for the data that you have. A custom program 
written in Python and using Pandas can be more elegant, efficient, and configurable than data pipelines created in commercial software tools.    

### Bokeh    
Bokeh provides data visualization and data interaction capabilities to the Python platform, using either notebooks or standalone programs. This example is a 
standalone program written in Python that uses the Bokeh library along with Pandas. A program uses Bokeh to dynamically place glyphs and widgets on 
the canvas of a plot using data sets. The placement, size, color, shape, and number of glyphs is totally within your control. This is 
in contrast to commercial BI tools with a set palette of visuals that you can easily drop onto a page-formatted canvas. BI tools limit you to the visuals 
and options that they have built in order to provide speed and convenience.    

Other Python libraries provide similar but Bokeh also has one aspect to its architecture that is compelling. Bokeh uses websockets to open a network 
connection to the server program from the web browser that is rending the visuals. All data and configurations for those visuals are channeled through 
that websocket instead of being downloaded as text content in the HTML page. The data isn't stored in a browser cache. It can't be captured from the 
page source. A JavaScript library programmatically renders the visuals after the websocket is open. Even better, that library automatically updates 
the visuals without reloading the page when the data is changed, or in response to an interaction with the person viewing. Bokeh provides interactivity 
through the browser.    

## Report Overview
Click [here](https://907sjl.github.io/referrals-bokeh/referrals_report) for an overview of the report.    

## Data Sources
The numerical values in these reports are fabricated and do not represent any real healthcare organization.  The script that created the data for this 
example can be found [in the create_referral_data folder](https://github.com/907sjl/referrals_powerbi/tree/main/create_referral_data). This script creates two Comma Separated Values files that are the source of data for 
this report:    

- Referrals.csv
: A file containing one row for each referral and columns with the dates when each referral reached a process milestone.    

- DirectSecureMessages.csv
: A file containing one row for each Direct Secure Message about a patient that was sent to a referral inbox. These are used to measure how often messages are used in place of referrals.     

## Program Structure    
<img src="images/package_diagram.svg?raw=true" alt="SVG image: package diagram"/>    

This example is a standalone Python application using the Bokeh library. The Bokeh library, in turn, uses the Tornado library as a lightweight HTTP 
server to host the HTML pages that contain the Bokeh visuals.    

The Python program divides application logic from data provisioning using separate internal packages.    

* App
: The App package contains classes that respond to requests for Bokeh documents, render visuals, and respond to interactive events.    
    <br>*- ClinicProcessApp.py - common.py - CRMUsageApp.py - PendingReferralsApp.py - RoutinePerformanceApp.py - ScheduleTimesApp.py - SeenTimesApp.py - UrgentPerformanceApp.py*    

* Plot
: The Plot package contains classes that render specific types of visuals placed on the Bokeh documents.    
    <br>*- AgeDistributionPlot.py - CategoryBarsPlot.py - DataLabelPlot.py - DataTablePlot.py - HorizontalRatioPlot.py - ProcessGaugePlot.py - ReferralVolumePlot.py - SeenRatioPlot.py*

* Model
: The Model package calculates process measures at load and contains functions that provide data for visuals.    
    <br>*- CRMUse.py - DSMUse.py - PendingTime.py - ProcessTime.py*

* Source
: The Source package loads the source data when the package loads and contains functions that provide data for calculating process measures.    
    <br>*- DSMs.py - Referrals.py*

Other assets such as HTML templates and CSS style sheets facilitate the delivery of the human interface via the Tornado web server.    

* css
: The css folder contains cascading style sheets used by the HTML templates.    
<br>*- printstyles.css - printstyles_rotated.css - screenstyles.css - styles.css*

* fonts
: The fonts folder contains font definition files loaded into the HTML document with the style sheets.
 
* templates
: The templates folder contains HTML template pages for each of the Bokeh documents, and a master layout page that uses IFRAMEs to swap between documents.    
<br>*- cover.html - crm.html - index.html - pending.html - referrals.html - routine.html - scheduled.html - seen.html - toc.html - urgent.html*    

## Pandas ELT    

### Data Load    
The data load is initiated by the top-level code within the model.source package modules when they are first loaded. The referral data and calculated 
measurement data remain resident in memory as long as the Python server program is running.    

<img src="images/source.svg?raw=true" alt="SVG image: model.source package diagram"/>    

Both modules in the model.source package load source data from the CSV files. The CSV files are loaded directly into Pandas DataFrame objects with 
typecasting and date parsing.    

```
return pd.read_csv('referrals.csv', dtype=column_types, parse_dates=date_columns)
```    

After loading the data the modules calculate simple record-level facts and create calculated date columns that simplify 
the downstream filtering required to calculate measurements.

### Process Measures    
Measurements of referral processing time are calculated in the model.ProcessTime module. This module imports the modules from the model.source package that 
provide the data that is consumed by this module in order to calculate the measurement data that is surfaced in the Bokeh applications.    

<img src="images/processtime_pack.svg?raw=true" alt="SVG image: model.ProcessTime package diagram"/>    

The calculations are triggered by top-level code when the module is first imported. Twelve months of measurements are calculated and stored in memory.  The 
measurement data is accessed by the Bokeh applications via top-level variables and provider functions.    

<img src="images/processtime_act.svg?raw=true" alt="SVG image: model.ProcessTime activity diagram"/>    

Process measurements are stored in a Pandas DataFrame that has a granularity of one row for each clinic that is being measured. The DataFrame is created 
by sampling the referral data to create a data set of unique clinics that have referrals.    
```
process_measures_df = pd.DataFrame({'Clinic': np.sort(referral_df['Clinic'].unique())})
process_measures_df = (
    pd.concat([pd.DataFrame({'Clinic': '*ALL*'}, index=[0]), process_measures_df]).reset_index(drop=True))
```    
Each of these DataFrame instances holds measurement data for a single month. A top-level list provides access to the data for every month that is 
calculated when the module loads.    
```
clinic_measures[curr_month] = curr_month_clinic_df
```    
Referral records from the model.source package are collected into calculation data sets using the first and last dates in each month, and also by 
taking advantage of extra convenience date columns that are calculated for each referral when the data is first loaded from the source.    
```
idx = (referrals_df['Clinic'].isin(clinics_df['Clinic'])
       & (referrals_df['Reporting Date 5 Day Lag'] >= start_date)
       & (referrals_df['Reporting Date 5 Day Lag'] < end_date))
source_df = referrals_df.loc[idx].copy()
```    
Individual measures at the clinic level of granularity are successively calculated from these calculation data sets and merged into the master 
data set of process measurements for the month.    
```
by_clinic_df = source_df.loc[source_df['Referral Priority'] == 'Urgent'] \
    .groupby('Clinic') \
    .agg(rid=pd.NamedAgg(column="Referral ID", aggfunc="count"),
         aged=pd.NamedAgg(column="Referral Aged Yn", aggfunc="sum")) \
    .rename(columns={'rid': prefix + 'Urgent Referrals Sent',
                     'aged': prefix + 'Urgent Referrals Aged'})
```    

### Pending Referral Measures    
The model.PendingTime module calculates measures describing how many referrals have been waiting to be scheduled and for how long. Referrals to be scheduled are 
waiting in one of four queues. These referrals are either pending acceptance, on hold, pending reschedule, or sitting in an accepted status but not yet scheduled.    

This module imports the modules from the model.source package that provide the data that is consumed by this module in order to calculate the measurement data that 
is surfaced in the Bokeh applications.    

<img src="images/pendingtime_pack.svg?raw=true" alt="SVG image: model.PendingTime package diagram"/>    

The calculations are triggered by top-level code when the module is first imported. All referrals that are currently pending are measured regardless of when those referrals 
where originally sent. This surfaces information about how many referrals are currently pending but without historical tracking. The measurement data is accessed by the 
Bokeh applications via top-level variables and provider functions.    

<img src="images/pendingtime_act.svg?raw=true" alt="SVG image: model.PendingTime activity diagram"/>    

The calculation of measures for pending referrals follows the same general pattern as the process measure calculations described above.    

### Measures of CRM Use    
The model.CRMUse module calculates measures describing how often the Clinic Referral Management system was used vs. only scheduling patients in the schedule book. 
This report compares the referral management milestones of accepting, scheduling, and seeing patients against scheduled appointments for patients at the same clinic.    

This module imports the modules from the model.source package that provide the data that is consumed by this module in order to calculate the measurement data that 
is surfaced in the Bokeh applications.    

<img src="images/crmuse_pack.svg?raw=true" alt="SVG image: CRMUse.py package diagram"/>    

The calculations are triggered by top-level code when the module is first imported. The measurement data is accessed by the Bokeh applications via top-level variables 
and provider functions.    

<img src="images/crmuse_act.svg?raw=true" alt="SVG image: CRMUse.py activity diagram"/> 

The calculation of measures for CRM use follow the same general pattern as the process measure calculations described above.    

### Measures of DSM Use    
The model.DSMUse module calculates measures describing how many patients are discussed using Direct Secure Messaging only vs. being entered into the Clinic Referral 
Management system as a referral.    

This module imports the modules from the model.source package that provide the data that is consumed by this module in order to calculate the measurement data that 
is surfaced in the Bokeh applications.    

<img src="images/dsmuse_pack.svg?raw=true" alt="SVG image: DSMUse.py package diagram"/>    

The calculations are triggered by top-level code when the module is first imported. The measurement data is accessed by the Bokeh applications via top-level variables 
and provider functions.    

<img src="images/dsmuse_act.svg?raw=true" alt="SVG image: DSMUse.py activity diagram"/>    

The calculation of measures for DSM use follows the same general pattern as the process measure calculations described above.    

## Application Control Layer    
The pages in this report utilize Jinja2 templates to generate HTML for the browser that renders them. Jinja2 is a text templating library that is included and used 
by Bokeh to embed interactive scripts. Some of the pages in this report only use Jinja2 to generate data-driven HTML content and provide no interactivity. Other pages 
embed Bokeh scripts to render visuals and to allow the viewer to select one clinic or another.    

### Bokeh Application Pages    
Three of the pages in this report focus on one clinic at a time and display more detailed process measures that look into processing milestones, referrals on-hold, and 
how often the clinic makes use of the referral management system. These pages render visuals using the Bokeh library and respond to changes to the clinic selector widget.    

- ClinicProcessApp.py
: Creates content for a report page focusing on referral processing milestones and referral ages for one clinic. Responds to clinic selections.    

- PendingReferralsApp.py
: Creates content for a report page focusing on all referrals still in a pending status. Responds to clinic selections.    

- CRMUsageApp.py
: Creates content for a report page focusing on the relative use of the Clinic Referral Management system vs. the schedule book to process referrals. Responds to clinic selections.    

The applications are built into Python modules and classes, one module and one class for each application. The application class instance acquires measurement data from 
the top-level variables and provider functions within the model package. Those variables persist while the Bokeh server remains running to listen for HTTP requests. Helper 
classes within the app.plot package generate the plots that are added to the Bokeh documents by the application classes. These plot classes are instantiated within the 
application class objects and are given specific data from the model package.    

<img src="images/clinicprocessapp_pack.svg?raw=true" alt="SVG image: ClinicProcessApp.py package diagram" />    

Bokeh uses Tornado to route requests for pages and reply with HTML content. Bokeh applications can typically be thought of as pages. The app modules 
each include an application request handler function that must be top-level in order to work with the Bokeh library. The handler function instantiates a class for 
the application session and invokes a method that adds Bokeh plots to a Bokeh document that will be used to serve content for the application session. The document and 
class instance is specific to the application session and persists until the Bokeh session is closed by the browser, by navigating to another application or by closing 
the tab. 

<img src="images/clinicprocessapp_act.svg?raw=true" alt="SVG image: ClinicProcessApp.py package diagram" /> 

The Bokeh visuals are injected into the HTML content using Jinja2 and template files. The templates are HTML files with the Jinja2 templating syntax included. The 
instructions within the template sections are parsed by the Jinja2 library to dynamically add HTML content. The template file to use for each app is set as a class 
level variable when the module loads.    

```
app_template = 'referrals.html'
```    

Then the template file is loaded and added to the Bokeh document.    

```
self.document.template = self._app_env.get_template(self.app_template)
```    

Plots are added to the Bokeh document by creating Bokeh figures. Figures are a canvas on which visuals are drawn. Bokeh supports using Scalable Vector Graphics to render 
visuals. This is a must-have for documents that are intended for printing or PDF distribution. This example project is a report and is used in conjunction with another 
Python script that automates the export of multiple pages to PDF files. Using SVG avoids the blocky, raster graphics look when the low DPI screen image is exported to 
a high DPI output format. It also increases accessibility by allowing viewers to zoom into the page.    

```
seen_ratio_plot = figure(height=self.plot_height, width=self.plot_width, title=None, toolbar_location=None,
                         x_range=Range1d(x_axis_start, x_axis_start + x_axis_distance),
                         y_range=Range1d(y_axis_start, y_axis_start + y_axis_distance),
                         output_backend="svg")
```    

The Python code that runs on the server doesn't actually draw the visuals, it creates configuration data that is streamed to the browser over a websocket.  The browser 
renders the visuals from this configuration data within a shadow DOM using Javascript. The Javascript libraries are included as links within the Jinja2 template file.    

Visuals are applied to plots as data-driven glyphs.    

```
seen_ratio_plot.annular_wedge(x=0, y=0, inner_radius=inner_radius, outer_radius=outer_radius,
                              start_angle='starting_plot_angle', end_angle='ending_plot_angle',
                              line_color='white', fill_color='color', source=self.plot_data_source,
                              legend_group='measure')
```    

This example draws wedge glyphs using data from the *plot_data_source* DataFrame and the columns *starting_plot_angle* and *ending_plot_angle*. It creates one wedge for 
every row in the source data.    

The plot is named and added to the Bokeh document after all required glyphs are added. A reference pointer for the plot is added to the Jinja2 template using the 
name given to the plot. Instructions within the template inject the visual into the HTML content so that the BokehJS library can render the visual in the browser.    

```
seen_ratio_plot.name = self.plot_name
self.document.add_root(seen_ratio_plot)
```    

### Jinja2 Template Pages    
Four of the pages in this report tabulate referral process measures for all clinics. These pages have no interactivity. They render with the measurements from the most 
recent month. These pages are only using Bokeh to leverage the Tornado HTTP server and the Jinja2 text templating libraries that come with Bokeh.    

- SeenTimesApp.py
: Creates content for a report page listing the median wait times for referrals to be seen by clinic.    

- ScheduleTimesApp.py
: Creates content for a report page listing the median wait times for referrals to be scheduled by clinic.    

- UrgentPerformanceApp.py
: Creates content for a report page listing the rate that urgent referrals are seen by the target number of days.    

- RoutinePerformanceApp.py
: Creates content for a report page listing the rate that routine referrals are seen by the target number of days.    

These pages are still Bokeh applications with a Bokeh document. They are implemented in similar fashion to the pages that use Bokeh visuals but without using any 
helper classes from the app.plot package. 

<img src="images/urgentperformanceapp_pack.svg?raw=true" alt="SVG image: UrgentPerformanceApp.py package diagram"/>    

The requests and responses are also handled the same. The Tornado HTTP server calls a top-level handler function that instantiates a class for the application session 
and calls a method that adds data into the document.    

<img src="images/urgentperformanceapp_act.svg?raw=true" alt="SVG image: UrgentPerformanceApp.py activity diagram"/>    

The data to be rendered with these simpler pages is injected into the HTML stream using Jinja2 and templates. The templates are HTML files with the Jinja2 templating 
syntax included. The instructions within the template sections are parsed by the Jinja2 library to dynamically add HTML content. The template file to use for each app 
is set as a class level variable when the module loads.    

```
app_template = 'urgent.html'
```    

Then the template file is loaded and added to the Bokeh document.    

```
self.document.template = self._app_env.get_template(self.app_template)
```    

Data is added to the template so that it is accessible from the template instructions that are coded into the template file.    

```
self.document.template_variables["clinics"] = self.clinics
```    

In this example the DataFrame with the measurement data for all clinics is added by reference into a template variable named *clinics*. The DataFrame is then accessible 
within the Jinja2 template.    

## Visualization Layer    
Bokeh uses Jinja2 templates to inject HTML content dynamically into an HTTP response message. A Bokeh visual is sent as configuration data that is used by the BokehJS 
library in the client browser. BokehJS opens a websocket to the Python server app to collect data while the page renders. The BokehJS library is a Javascript library 
that is linked within the Jinja2 template and sent as part of the HTML page. Bokeh applications can also use Jinja2 directly to either: use data on the server to 
dynamically construct HTML structures, or inject data into the HTML content to be rendered normally by the browser.    

The visualization layer of this report is a collection of HTML template files with embedded Jinja2 instructions. Each page in the report has an individual HTML template. 
The templates are all similar boilerplates with different visual layouts. The templates use the following techniques to render data or allow viewers to 
select a clinic.    

### Embedded Bokeh Visuals    
A template that contains a Bokeh visual will inject the visual's configuration using a Jinja2 command block and the **embed** macro.    
```
{% raw %}
<div>{{ embed(roots.urgent_aim_gauge) }}</div>
{% endraw %}
```    
The Bokeh application handler adds content to a Document instance that is associated with the viewer's session and the application. The Document has a collection named 
*roots* that provides access to each of the named visuals that have been added to the Document. The **embed** macro replaces the Jinja2 command block from the template 
HTML with an HTML placeholder element that is specific to one of the visuals, *urgent_aim_gauge* in this case. This dynamically customized HTML is then sent to the 
viewer's browser with script that renders the visual, be it a graph, table, or something else, on an HTML canvas in a shadow DOM. The rendering happens in the client 
browser.    

The data and styling for the embedded Bokeh visuals is configured programmatically in the Python server application handlers. Data is communicated with the BokehJS script 
on the client browser over a websocket connection during rendering. Styles are passed to the script to be applied to the elements that the script creates in the HTML 
canvas. Stylesheets cannot be used effectively with Bokeh visuals, unfortunately. The support for custom stylesheets is too limited.    

### Embedded Feedback Widgets    
Interactive widgets can be placed into application pages. They enable the viewer to pan, scroll, or zoom charts, sort tables, and other similar actions on the rendered 
data to enhance the experience of exploring the data. There are also widgets that allow the viewer to send requests back to the application server to modify the data 
or the configuration of the visuals in order to see something else.    
```
{% raw %}
<div class="slicer-embed-block" id="clinic_slicer">{{ embed(roots.clinic_slicer) }}</div>
{% endraw %}
```    
This example report places a drop-down list of clinic names on three pages that focus on one clinic at a time in detail. Embedding the drop-down widget into the HTML page is 
the same as embedding a visual by using the Jinja2 **embed** macro. The difference is that instead of adding a plot of glyphs to the document, the application handler adds 
a Bokeh widget instance to the document.    
```
select = Select(value=clinic, options=wt.get_clinics(month))
select.on_change("value", *callback)
```    
This example creates a Select widget instance and assigns a list of unique clinic names to the widget. A callback function is also assigned to be invoked when the selected 
clinic name changes. The function causes the data for the selected clinic to be fetched and sent to the visuals on the page via the websocket, along with new axis 
ranges. The widget and the callback are added by Python code in the application handler on the server. BokehJS handles the communication to invoke the callback in the 
server application.    
```
select.name = 'clinic_slicer'
doc.add_root(select)
```    
The Select instance is given a name. This is the name that is used to embed it into the Jinja2 template. Adding the widget to the document makes it available to the 
template. Since the clinic drop-down list is the same in each of the application pages, it is added by a utility function **add_clinic_slicer** in the module **common.py**.    

### Direct Data Injection    
Sometimes a simpler approach will do. Summary values can be directly injected into the HTML content using Jinja2. This is suitable when there are no concerns about 
how portable the data is and the volume of the data is exactly the same as the amount of HTML content within the page. For example, a label with a median wait time 
across all clinics. That single number will be downloaded and displayed one way or another. As an aggregate value it may not be considered very sensitive. The upside 
to this approach is that top-level style sheets can be applied to the data.    
```
{% raw %}
<span class="card-data-value">{{ m28_median_to_seen }}</span>
{% endraw %}
```    
In this example the 28-day median wait time to be seen is stored in a template variable. The template variable is directly referenced within in Jinja2 code block. This 
results in the value of the variable being rendered as text into the HTML page content in place of the code block.    
```
self.document.template_variables["m28_median_to_seen"] = (
    v.half_up_int(wt.get_overall_rate_measure(wt.last_month, 'MOV28 Median Days until Seen')))
```    
The application handler in **SeenTimesApp.py** adds this value to a document collection named **template_variables** and gives the value a name. This name is referenced 
by the template to inject the value into the HTML content. In this example a specific measure value, *MOV28 Median Days until Seen*, is collected from the *model* 
package and filtered by the utility function *half_up_int* in **common.py** before being assigned as a template variable in the document.    

### Dynamically Scripted Labels    
Directly injecting data as HTML content has a big drawback in that it isn't interactive. The page must be reloaded in order to change the displayed values. Bokeh 
applications load once and respond to events through a websocket connection between BokehJS running on the client browser and the application server. One way to 
address this is to use Bokeh **HTMLLabelSet** or **HTMLLabel** glyphs in a plot. Those are data-driven and can respond to events. These seem to fall short or are 
just too difficult to manipulate when the layout and style is important. Plots have extra padding and the style sheet support in those glyphs is limited.    

To get around the challenges with the Bokeh HTML labels I created the **LabelDataSource** and **CallbackLabelPlot** classes in **DataLabelPlot.py**. These 
are plot helper classes in the app.plots package. The **LabelDataSource** class adds a plot to the document.      
```
def add_plot(self):
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
```    
The plot is a zero pixel figure containing the labels as rows in a data source. This plot facilitates the communication of label data to the page.    
```
callback = CustomJS(args=dict(source=self.plot_data_source), code=code)
self.plot_data_source.js_on_change('data', callback)
self.document.js_on_event('document_ready', callback)
```    
The plot is also assigned a custom Javascript callback that is invoked when the server changes the data or when the document is ready in the client browser. Javascript 
callbacks execute within the client browser. This callback searches the HTML document object model for elements that contain dynamic labels. It updates the content 
within those elements and updates the style sheet class. Updating the style sheet class dynamically can help with contextual color coding.    
```
label_plot.name = self.plot_name
self.document.add_root(label_plot)
```    
The **LabelDataSource** plot is named and added to the Bokeh document.    
```
{% raw %}
<div class="label-data-source-hidden">{{ embed(roots.label_data_source) }}</div>
{% endraw %}
```    
This enables the HTML template to hide the **LabelDataSource** plot somewhere on the page.    
```
<span class="[*class*]" id="urgent_improvement_dir_3_month_plot">[*label*]</span>
```    
The HTML template page includes elements that are meant to be found by the callback script using the element id. The callback places text in place of special tokens in 
the element's content and class name. This has a slight drawback in that the tokens are briefly flashed by the client browser before the document is ready and the 
callback executes.    

The **CallbackLabelPlot** class can be instantiated to hold a single label value and style sheet class name. It simply adds or updates these values in the data source 
of the **LabelDataSource** instance.    

There is another variant of this same approach in the **DataTablePlot.py** module. The **DataTablePlot** class dynamically renders an HTML table using Javascript. The 
data source for the table is passed to the page in the client browser using the Bokeh websocket connection.    

This approach allows the application server to change the data sources in response to events, and those changes are automatically rendered in the browser page. This 
also allows top-level CSS style sheets to be applied to tables and labels.    

### Dynamic HTML Structures    
The last data visualization technique in this example report is to use Jinja2 to dynamically create HTML elements within the application server before sending the 
HTML content to the client browser.    
```
{% raw %}
{% for index, row in clinics.iterrows() %}
    <tr>
        <td class="text-data"><nobr>{{ row['Clinic'] }}</nobr></td>
        <td class="numeric-data"><nobr>{{ row['Referrals Sent']|int }}</nobr></td>
        <td class="percent-data"><nobr>{{ row['Pct Referrals Seen After 90d']|int }}%</nobr></td>
        <td class="numeric-data">{{ age_category_color(row, 'MOV28 Median Days until Seen', row['Age Category to Seen']) }}</td>
        <td>{{ direction_symbol(row, 'Var MOV91 Median Days until Seen') }}</td>
        <td class="numeric-data">{{ '%0.2f'|format(row['Var MOV91 Median Days until Seen']|float) }}</td>
        <td class="numeric-data">{{ age_category_color(row, 'MOV91 Median Days until Seen', row['Age Category to Seen']) }}</td>
    </tr>
{% endfor %}
{% endraw %}
```    
Command blocks in the template instruct Jinja2 to use data from the template variables in conjunction with flow control statements to make decisions or iteratively 
construct the HTML content. In this example the *clinics* DataFrame was passed to Jinja2 as a template variable. Jinja2 uses Python to iterate through the DataFrame 
and create an HTML table row for every record in *clinics*.    

The benefits of this approach are simplicity and the ability to apply top-level style sheets to the content. The main drawback of this approach is the lack of 
interaction with the page that Bokeh visuals enable.    

## Report Automation    
The intent for this project was to create a report package as a PDF document. The report delivery is automated by running the Bokeh application and exporting the pages 
to PDF using the Playwright test harness. Playwright drives Chromium and supports pages that rely on Javascript.    

### Running the Server    
The Bokeh application server program uses a **__main__.py** module to start the server. The top-level code configures the Bokeh server with application paths and 
handler functions then starts the server.    
```
apps = {'/referrals/scheduled': Application(FunctionHandler(scta.schedule_times_app_handler)),
        '/referrals/seen': Application(FunctionHandler(sta.seen_times_app_handler)),
        '/referrals/routine': Application(FunctionHandler(rpa.routine_performance_app_handler)),
```    
```
routes = [('/referrals/cover', CoverHandler),
          ('/', IndexHandler),
          ('/referrals', IndexHandler),
          (r'/referrals/css/(.*)', StaticFileHandler, {'path': os.path.normpath(os.path.dirname(__file__) + '/css')}),
```
```
server = Server(apps, port=5005, extra_patterns=routes)
server.start()
```    
and begins an endless polling loop to respond to HTTP requests for application pages.
```
server.io_loop.start()
```    
The server hosts a default page with links to each of the application pages. With the Bokeh server application running, open **localhost:5005** in your browser to see 
the pages.    

<img src="images/default_page.jpg?raw=true" alt="default server page"/>    

The default page is an IFRAME with buttons across the top. Each button loads a different application page into the IFRAME. Three pages provide a drop-down list of 
clinics. The selected clinic will carry across to the other pages by way of cookies stored in the browser.    
```
cookies = doc.session_context.request.cookies
if 'clinic' in cookies:
    clinic = cookies['clinic']
    if len(clinic) > 0:
        return clinic
```    
Bokeh surfaces the cookies from the HTTP request to the Python server application, allowing application state to be stored and retrieved between sessions.    

### Printed Page Formatting    
Some tricks must be employed to make the HTML page output compatible with a printed page output, even if the medium is PDF. Both the browser and the PDF renderer will 
try to fit the output to a printed page size. If the HTML output isn't already constrained to a standard page size then one of those rendering layers will make decisions 
that may not be optimal. It is common for printed HTML pages to either overflow a page boundary or be shrunk down to an unreadable size.    

Cascading Style Sheets provides a convenient method to constrain the application page content to a 
printed page size.    
```
/* landscape */
.reportpage-rotated {
    width: 13.5in !important;
    height: 7.5in !important;
    overflow: hidden;
    background: #70BBFF;
    display: block;
    float: none;
    page-break-after: always;
    break-after: page;
}
/* Remove page break from last page */
.reportpage-rotated:last-of-type {
    width: 13.5in !important;
    height: 7.5in !important;
    overflow: hidden;
    background: #70BBFF;
    display: block;
    float: none;
    page-break-after: avoid;
    break-after: avoid;
}
```    
This is opposite the usual requirement to make pages responsive to device screen 
sizes. A style class is created to override the height and width of a DIV element and to control the 
placement of page breaks when printing the page.    
```
{% raw %}
{% block contents %}
<div class="reportpage-rotated">
{% endraw %}
```    
The page content is placed within the DIV.    

The browser may still need a hint about the page size and margins when printing and so a print media only 
style sheet is linked to the page with a @page directive.    
```
/* Landscape page */ 
@page {
    size: 14in 8.5in;
    margin-top: 0.5in;
    margin-bottom: 0.5in;
    margin-left: 0.25in;
    margin-right: 0.25in;
}
```    
The challenge with printing visuals to PDF or paper is DPI, Dots Per Inch. Graphs, images, and even text labels 
that are rendered by Bokeh will appear blocky and blurry when printed. Content that looks fine on a screen at 96 DPI 
will look awful at 300 DPI. Similarly, content generated at 300 DPI and displayed on a screen at 96 DPI will lose 
fidelity when it is squeezed down into a smaller space. This is also a challenge for accessibility. The same problem 
arises trying to zoom into a 96 DPI image in the browser page.    
```
seen_ratio_plot = figure(height=self.plot_height, width=self.plot_width, title=None, toolbar_location=None,
                         x_range=Range1d(x_axis_start, x_axis_start + x_axis_distance),
                         y_range=Range1d(y_axis_start, y_axis_start + y_axis_distance),
                         output_backend="svg")
```    
Scalable Vector Graphics to the rescue! Bokeh supports drawing visuals and text in SVG format instead of as a raster 
image. SVG is actually instructions to the browser about what to draw in real time when rendering the page. Browsers 
also support drawing SVG images at different zoom levels with the same crisp lines as the original zoom. When the page is 
printed the SVG images will be drawn at the target DPI of the output media.    

Another approach used by this report is to push as much text as possible into the HTML layer instead of asking Bokeh 
to draw text in a plot.    

### Scripted Page Output    
A Python script creates a PDF report from this Bokeh application. This script is in the [page-capture-utility](https://github.com/907sjl/page-capture-utility) 
repository. It is a general purpose script that loads URLs from a table of contents file and prints the page content 
to PDF files.    
```
browser = await p.chromium.launch()

for index, row in toc.iterrows():
    folder_name = row['Folder']
    file_name = row['File Name']
    page_url = row['URL']
    width = row['Width'] + 'in'
    height = row['Height'] + 'in'
```    
The page-capture-utility script loads the table of contents into a DataFrame and iterates through the records. Each record 
has an URL, a destination file name, and the intended width and height of the page. The script loads Chromium using the 
Playwright library and loads each page.    
```
page = await browser.new_page()
await page.emulate_media(media="print")
await page.goto(page_url)
await page.wait_for_timeout(5000)
await page.pdf(width=width, height=height, print_background=True, path=target_file)
```    
Chromium is configured to render each page in print media mode. This causes Chromium to select the print media style sheet 
when loading each Bokeh application page. A timeout of 5 seconds per page allows the page to load and execute the client 
side Javascript in BokeJS and custom callbacks.    

The PDF report package is a compilation of pages that focus on individual clinics. If someone where manually printing 
these pages they must use the clinic selection drop-down widget to choose each clinic in turn. The automation 
script needs a way to select the clinic for each page of the report.    
```
args = doc.session_context.request.arguments
if 'Clinic' in args:
    clinic = args['Clinic'][0]
    if len(clinic) > 0:
        clinic = clinic.decode("utf-8")
        return clinic
```    
When the application handlers are invoked in response to an HTTP request they check the request arguments for the clinic 
name. If the clinic name is sent via an HTTP argument that overrides the clinic name found in browser cookies. This 
allows automated scripts to select the clinic as part of the URL for the page, and to iterate through clinics to 
export a page for each one.    

The page-capture-utility script creates a single PDF file for each URL. Another utility, [pdf-splicer](https://github.com/907sjl/pdf-splicer), 
compiles the report packages from the individual PDF files using a similar approach of loading a table of 
contents file and exporting PDF files using PyPDF2.    