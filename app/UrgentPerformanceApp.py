"""
UrgentPerformanceApp.py
Control script for the measures of urgent referral process aim performance Bokeh application.
https://907sjl.github.io/
"""

from jinja2 import Environment, FileSystemLoader

from bokeh.document import Document

from datetime import date

import model.WaitTimes as wt
import app.common as v


class UrgentPerformanceApp:
    """
    This class represents the Bokeh application with urgent referral process aim performance measures.
    """

    # Class level properties

    # Urgent referral performance data pre-sorted by clinic name
    clinics = wt.CLINIC_MEASURES[wt.last_month].copy()
    clinics.sort_values(by='Clinic', ascending=True, inplace=True)
    clinics.reset_index(drop=True, inplace=True)
    clinics = clinics.loc[clinics['Clinic'] != '*ALL*']

    # App page configuration
    app_title = 'Urgent Referral Performance'
    app_template = 'urgent.html'
    app_root = 'referrals'
    app_env = Environment(loader=FileSystemLoader('templates'))

    def __init__(self, doc: Document):
        self.document = doc

    # Methods

    def insert_urgent_performance_data(self) -> None:
        # Bokeh application handler to modify a blank document that will be served from a Bokeh
        # server application.  This application will be invoked by the script that is injected into the HTML
        # in the response by Jinja2 when the template is rendered. The Bokeh client script opens
        # a websocket to the Bokeh server application to obtain the contents to render in the browser.  This
        # handler adds content to be rendered into the application document.

        # The Bokeh application handlers pass this text through to the HTML page title
        self.document.title = self.app_title

        # This line would override the default template with... the default template
        # This shows how to get the core bokeh template text using the bokeh Tornado environment paths
        #    doc.template = get_env().get_template("file.html")

        # This line overrides the Jinja2 template with text from a custom template file
        # in the app templates directory using a Tornado environment set up as a global
        # in this script module above.
        self.document.template = self.app_env.get_template(self.app_template)

        # The Bokeh application handlers automatically pass this dictionary into the
        # Jina2 template as parameters.  The parameters appear as variables to the
        # template code.
        self.document.template_variables['app_root'] = self.app_root
        self.document.template_variables['today_long'] = date.today().strftime("%A, %B %d, %Y")
        self.document.template_variables['report_month'] = wt.last_month.strftime("%B %Y")

        self.document.template_variables["m28_percent_seen_in_5"] = (
            v.half_up_int(wt.get_overall_rate_measure(wt.last_month, 'MOV28 Pct Urgent Referrals Seen in 5d')))

        variance = (
            v.half_up_int(wt.get_overall_rate_measure(wt.last_month, 'Var MOV91 Pct Urgent Referrals Seen in 5d')))
        self.document.template_variables["var_m28_percent_seen_in_5"] = variance
        self.document.template_variables["dir_m28_percent_seen_in_5"] = (
            wt.get_overall_measure(wt.last_month, 'Dir Var MOV91 Pct Urgent Referrals Seen in 5d'))
        if variance < 0:
            self.document.template_variables["dir_m28_percent_seen_in_5_style"] = "card-data-direction-down-sm"
        else:
            self.document.template_variables["dir_m28_percent_seen_in_5_style"] = "card-data-direction-up-sm"

        self.document.template_variables["m91_percent_seen_in_5"] = (
            v.half_up_int(wt.get_overall_rate_measure(wt.last_month, 'MOV91 Pct Urgent Referrals Seen in 5d')))

        variance = (
            v.half_up_int(wt.get_overall_rate_measure(wt.last_month, 'Var MOV182 Pct Urgent Referrals Seen in 5d')))
        self.document.template_variables["var_m91_percent_seen_in_5"] = variance
        self.document.template_variables["dir_m91_percent_seen_in_5"] = (
            wt.get_overall_measure(wt.last_month, 'Dir Var MOV182 Pct Urgent Referrals Seen in 5d'))
        if variance < 0:
            self.document.template_variables["dir_m91_percent_seen_in_5_style"] = "card-data-direction-down-sm"
        else:
            self.document.template_variables["dir_m91_percent_seen_in_5_style"] = "card-data-direction-up-sm"

        self.document.template_variables["m182_percent_seen_in_5"] = (
            v.half_up_int(wt.get_overall_rate_measure(wt.last_month, 'MOV182 Pct Urgent Referrals Seen in 5d')))

        variance = (
            v.half_up_int(wt.get_overall_rate_measure(wt.last_month, 'Var MOV364 Pct Urgent Referrals Seen in 5d')))
        self.document.template_variables["var_m182_percent_seen_in_5"] = variance
        self.document.template_variables["dir_m182_percent_seen_in_5"] = (
            wt.get_overall_measure(wt.last_month, 'Dir Var MOV364 Pct Urgent Referrals Seen in 5d'))
        if variance < 0:
            self.document.template_variables["dir_m182_percent_seen_in_5_style"] = "card-data-direction-down-sm"
        else:
            self.document.template_variables["dir_m182_percent_seen_in_5_style"] = "card-data-direction-up-sm"

        self.document.template_variables["m364_percent_seen_in_5"] = (
            v.half_up_int(wt.get_overall_rate_measure(wt.last_month, 'MOV364 Pct Urgent Referrals Seen in 5d')))

        self.document.template_variables["clinics"] = self.clinics
        self.document.template_variables["age_category_color_map"] = v.AGE_CATEGORY_COLOR_MAP
        self.document.template_variables["age_category_label_color_map"] = v.AGE_CATEGORY_LABEL_COLOR_MAP
    # END insert_urgent_performance_data
# END CLASS UrgentPerformanceApp


def urgent_performance_app_handler(doc: Document) -> None:
    urgent_app = UrgentPerformanceApp(doc)
    urgent_app.insert_urgent_performance_data()
# END urgent_performance_app_handler
