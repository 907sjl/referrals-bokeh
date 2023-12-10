< [Portfolio](https://907sjl.github.io) | [Full Report](pdf/Referral%20Process%20Measures%20Bokeh.pdf) | [GitHub Repository](https://github.com/907sjl/referrals-bokeh) | [Overview](https://907sjl.github.io/referrals-bokeh/referrals_report)    

One way to measure access to care is timeliness. Long delays to see a healthcare provider can speak to availability issues, either a lack of resources or inefficiencies that result in a less than optimal conversion of referrals into appointments. Long delays can also speak to accommodation issues or accessibility issues if patients have difficulty attending their scheduled appointments.
This project is an example of a report that I created to look at the process times for referred patients at specialty clinics. 

## Why Bokeh?    
Why would I choose Bokeh to create this report? A BI platform can create a process measurement report such as this. I did in fact create this in Power BI, and that example can be found [here](https://907sjl.github.io/referrals_powerbi/). This README is about the Bokeh example though so let's look at some of the strengths that a Python approach brings to this scenario.

### HTML, JavaScript, and CSS    
Three common and pervasive technologies come together to provide an analytics developer with the tools necessary to create any layout they can imagine. 
HTML provides the scaffolding and CSS shapes and styles the layout. JavaScript allows for custom and data-driven logic to fine-tune the final product 
and to implement interactive features. These tools are general purpose. They are vendor agnostic. They have been built to support an industry and are 
supported by a worldwide community of practitioners. Any knowledge about how to apply these technologies is freely available and only a web search away.    

Deliverables created with HTML and CSS are very readable from text files in your source repository. They work well with version control platforms (like Git). 
As does JavaScript, of course. Working with these technologies frees you from the artificially imposed limitations of BI tools that only provide the flexibility 
that they have been created to provide. BI tools must limit flexibility in the interests of enforcing supportable use cases, supporting data governance, 
and providing protection against security vulnerabilities.    

### Python and Pandas    
Flexibility and freedom also define another technology underlying this example, Python. Python is a general purpose programming language used to create 
complex applications, to be the glue that integrates other software platforms, or to automate tasks with scripts. Using Python to create your analytic 
deliverable ensures that you will have opportunities to automate tasks such as data refresh and report generation. Power BI, by comparison, provides these 
capabilities if you publish your dashboards and reports on their cloud service and use Power Automate. BI tools limit your automation possibilities to 
use cases that they have built into their tools, whereas a report developed using Python can be automated using the same programming language used to 
create it. BI tools come with licensing concerns whereas Python does not.    

Pandas is a brilliant data analysis library for Python programs. It provides data aggregation, statistical analysis, and data manipulation in a way 
that is comparable to the R programming language. Using Python and Pandas together frees you from the limitations of software packages. You may sacrifice 
the convenience of connectors for specific data sources, depending on the availability of Python libraries for the data that you have. A custom program 
written in Python and using Pandas can be more elegant and efficient than data pipelines created in commercial software tools. A good example is the 
data firewall that is necessary in Power Query to prevent the data in one source from being used to configure another source dynamically at load time. 
Goodbye data-driven configuration. Such concerns are not a problem using a Python program.  

### Bokeh    
Bokeh provides data visualization and data interaction capabilities to the Python platform, using either notebooks or standalone programs. This example is a 
standalone program written in Python that uses the Bokeh library along with Pandas. A program uses Bokeh to dynamically place glyphs and widgets on 
the canvas of a plot using data sets. It is data art. The placement, size, color, shape, and number of glyphs is totally within your control. This is 
in contrast to commercial BI tools with a set palette of visuals that you can easily drop onto a page-formatted canvas. BI tools limit you to the visuals 
and options that they have built in order to provide speed and convenience.    

Other Python libraries provide similar but Bokeh also has one aspect to its architecture that is compelling. Bokeh uses websockets to open a network 
connection to the server program from the web browser that is rending the visuals. All data and configurations for those visuals are channeled through 
that websocket instead of being downloaded as text content in the HTML page. The data isn't stored in a browser cache. It can't be captured from the 
page source. A JavaScript library programmatically renders the visuals after the websocket is open. Even better, that library automatically updates 
the visuals without reloading the page when the data is changed, or in response to an interaction with the person viewing. Bokeh provides interactivity 
through the browser.    

### In Summary
To sum up the answer to my question, the reasons to choose Bokeh are a mix of flexibility, freedom, free licensing, portability, and those immediately 
responsive websockets that help control the propagation of data.  

This approach isn't all roses. It can be a lot of detail work and especially the first time. Something that is commonplace in a BI tool, 
such as paper size page formatting, requires specialized tricks in this approach. You can't match the speed and convenience of a BI tool for iterative 
re-prototyping measures and dashboard layouts. This is more true when faced with a new scenario and few previously built assets. 
My Power BI example README has good things to say about that approach. Bokeh has good documentation and a monitored community forum, if somewhat grumpy. 
That still doesn't compare to the free training and public domain posts related to Power BI.    

## Overview
Click [here](https://907sjl.github.io/referrals-bokeh/referrals_report) for an overview of the report.  The numerical values in these reports are fabricated and do not represent any real healthcare organization.  The script that created the data for this example can be found [in the create_referral_data folder](https://github.com/907sjl/referrals_powerbi/tree/main/create_referral_data).    
