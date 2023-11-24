"""
Package: referrals-bokeh.app.plot
A collection of modules that render the visuals for the Bokeh apps.

Modules:
    AgeDistributionPlot.py - Adds a histogram of referrals by age category bins to a Bokeh document
    CategoryBarsPlot.py - Adds a horizontal bar chart of referral counts by category to a Bokeh document
    DataLabelPlot.py - Adds data driven HTML labels that are rendered in the template document not a shadow DOM
    DataTablePlot.py - Adds a data driven HTML table that is rendered in the template document not a shadow DOM
    HorizontalRatioPlot.py - Adds a horizontal bar chart of counts that represent a process ratio
    ProcessGaugePlot.py - Speedometer style gauge representing a process ratio and a target rate
    ReferralVolumePlot.py - Adds a horizontal bar chart of referral counts that represent volume measures
    SeenRatioPlot.py - Adds a donut chart representing the percentage of referrals seen and scheduled
"""