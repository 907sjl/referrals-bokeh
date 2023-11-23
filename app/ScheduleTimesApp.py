"""
ScheduleTimesApp.py
Control script for the measures of time to schedule referrals Bokeh application.
https://907sjl.github.io/

Classes:
    ScheduleTimesApp - Implements the Bokeh application with measures of time to schedule referrals across clinics.

Functions:
    schedule_times_app_handler - Bokeh app handler function that instantiates the class and initializes.
"""

from jinja2 import Environment, FileSystemLoader

from bokeh.document import Document

from datetime import date

import model.WaitTimes as wt
import app.common as v


class ScheduleTimesApp:
    """
    This class represents the Bokeh application with measures of time to schedule referrals across clinics.

    Public Attributes:
        app_title - The page title for the Bokeh application
        app_template - The html template file used by this application
        app_root - The route through the HTTP server that is the root of HTTP resource requests
        clinics - The data set of performance data for all clinics
        document - The Bokeh document for an instance of this application

    Public Methods:
        insert_wait_to_schedule_data - Sequences the data collection and rendering in the application document
    """

    # Class level properties

    # Routine referral performance data pre-sorted by clinic name
    clinics = wt.CLINIC_MEASURES[wt.last_month].copy()
    clinics.sort_values(by='Clinic', ascending=True, inplace=True)
    clinics.reset_index(drop=True, inplace=True)
    clinics = clinics.loc[clinics['Clinic'] != '*ALL*']

    # App page configuration
    app_title = 'Wait Times to Schedule Referrals'
    app_template = 'scheduled.html'
    app_root = 'referrals'
    _app_env = Environment(loader=FileSystemLoader('templates'))

    def __init__(self, doc: Document):
        """
        Initialize instances.
        :param doc: The Bokeh document for an instance of this application.
        """
        self.document = doc

    # Methods

    def insert_wait_to_schedule_data(self) -> None:
        """
        Sequences the load of data and rendering of visuals for this Bokeh application in response
        to a new document being created for a new Bokeh session.
        """

        # The Bokeh application handlers pass this text through to the HTML page title
        self.document.title = self.app_title

        # This line would override the default template with... the default template
        # This shows how to get the core bokeh template text using the bokeh Tornado environment paths
        #    doc.template = get_env().get_template("file.html")

        # This line overrides the Jinja2 template with text from a custom template file
        # in the app templates directory using a Tornado environment set up as a global
        # in this script module above.
        self.document.template = self._app_env.get_template(self.app_template)

        # The Bokeh application handlers automatically pass this dictionary into the
        # Jina2 template as parameters.  The parameters appear as variables to the
        # template code.
        self.document.template_variables['app_root'] = self.app_root
        self.document.template_variables['today_long'] = date.today().strftime("%A, %B %d, %Y")
        self.document.template_variables['report_month'] = wt.last_month.strftime("%B %Y")

        self.document.template_variables["m28_median_to_scheduled"] = (
            v.half_up_int(wt.get_overall_rate_measure(wt.last_month, 'MOV28 Median Days until Scheduled')))

        variance = (
            v.half_up_int(wt.get_overall_rate_measure(wt.last_month, 'Var MOV91 Median Days until Scheduled')))
        self.document.template_variables["var_m28_median_to_scheduled"] = variance
        self.document.template_variables["dir_m28_median_to_scheduled"] = (
            wt.get_overall_measure(wt.last_month, 'Dir Var MOV91 Median Days until Scheduled'))
        if variance < 0:
            self.document.template_variables["dir_m28_median_to_scheduled_style"] = "card-data-direction-down-sm"
        else:
            self.document.template_variables["dir_m28_median_to_scheduled_style"] = "card-data-direction-up-sm"

        self.document.template_variables["m91_median_to_scheduled"] = (
            v.half_up_int(wt.get_overall_rate_measure(wt.last_month, 'MOV91 Median Days until Scheduled')))

        variance = (
            v.half_up_int(wt.get_overall_rate_measure(wt.last_month, 'Var MOV182 Median Days until Scheduled')))
        self.document.template_variables["var_m91_median_to_scheduled"] = variance
        self.document.template_variables["dir_m91_median_to_scheduled"] = (
            wt.get_overall_measure(wt.last_month, 'Dir Var MOV182 Median Days until Scheduled'))
        if variance < 0:
            self.document.template_variables["dir_m91_median_to_scheduled_style"] = "card-data-direction-down-sm"
        else:
            self.document.template_variables["dir_m91_median_to_scheduled_style"] = "card-data-direction-up-sm"

        self.document.template_variables["m182_median_to_scheduled"] = (
            v.half_up_int(wt.get_overall_rate_measure(wt.last_month, 'MOV182 Median Days until Scheduled')))

        variance = (
            v.half_up_int(wt.get_overall_rate_measure(wt.last_month, 'Var MOV364 Median Days until Scheduled')))
        self.document.template_variables["var_m182_median_to_scheduled"] = variance
        self.document.template_variables["dir_m182_median_to_scheduled"] = (
            wt.get_overall_measure(wt.last_month, 'Dir Var MOV364 Median Days until Scheduled'))
        if variance < 0:
            self.document.template_variables["dir_m182_median_to_scheduled_style"] = "card-data-direction-down-sm"
        else:
            self.document.template_variables["dir_m182_median_to_scheduled_style"] = "card-data-direction-up-sm"

        self.document.template_variables["m364_median_to_scheduled"] = (
            v.half_up_int(wt.get_overall_rate_measure(wt.last_month, 'MOV364 Median Days until Scheduled')))

        self.document.template_variables["clinics"] = self.clinics
        self.document.template_variables["age_category_color_map"] = v.AGE_CATEGORY_COLOR_MAP
        self.document.template_variables["age_category_label_color_map"] = v.AGE_CATEGORY_LABEL_COLOR_MAP
    # END insert_wait_to_schedule_data
# END CLASS ScheduleTimesApp


def schedule_times_app_handler(doc: Document) -> None:
    """
    Bokeh application handler to modify a blank document that will be served from a Bokeh
    server application.  This handler adds content to be rendered into the application document.
    :param doc: The Bokeh document to add content to
    """
    schedule_app = ScheduleTimesApp(doc)
    schedule_app.insert_wait_to_schedule_data()
# END schedule_times_app_handler
