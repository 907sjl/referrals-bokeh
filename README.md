< [Portfolio](https://907sjl.github.io) | [Full Report](pdf/Referral%20Process%20Measures%20Bokeh.pdf) | [GitHub Repository](https://github.com/907sjl/referrals-bokeh) | [Overview](https://907sjl.github.io/referrals-bokeh/referrals_report)    

One way to measure access to care is timeliness. Long delays to see a healthcare provider can speak to availability issues, either a lack of resources or inefficiencies that result in a less than optimal conversion of referrals into appointments. Long delays can also speak to accommodation issues or accessibility issues if patients have difficulty attending their scheduled appointments.
This project is an example of a report that I created to look at the process times for referred patients at specialty clinics. 

## Technology Stack
<img src="images/tech_stack.jpg?raw=true"/>    

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
<img src="images/package_diagram.jpg?raw=true"/>    

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

<img src="images/source.jpg?raw=true"/>    

Both modules in the model.source package load source data from the CSV files, calculate simple record-level facts, and create date columns that simplify the downstream filtering 
required to calculate measurements.    

### Process Measures    
Measurements of referral processing time are calculated in the model.ProcessTime module. This module imports the modules from the model.source package that 
provide the data that is consumed by this module in order to calculate the measurement data that is surfaced in the Bokeh applications.    

<img src="images/processtime_pack.jpg?raw=true"/>    

The calculations are triggered by top-level code when the module is first imported. Twelve months of measurements are calculated and stored in memory.  The 
measurement data is accessed by the Bokeh applications via top-level variables and provider functions.    

<img src="images/processtime_act.jpg?raw=true"/>    

### Pending Referral Measures    
The model.PendingTime module calculates measures describing how many referrals have been waiting to be scheduled and for how long. Referrals to be scheduled are 
waiting in one of four queues. These referrals are either pending acceptance, on hold, pending reschedule, or sitting in an accepted status but not yet scheduled.    

This module imports the modules from the model.source package that provide the data that is consumed by this module in order to calculate the measurement data that 
is surfaced in the Bokeh applications.    

<img src="images/pendingtime_pack.jpg?raw=true"/>    

The calculations are triggered by top-level code when the module is first imported. All referrals that are currently pending are measured regardless of when those referrals 
where originally sent. This surfaces information about how many referrals are currently pending but without historical tracking. The measurement data is accessed by the 
Bokeh applications via top-level variables and provider functions.    

<img src="images/pendingtime_act.jpg?raw=true"/>    
