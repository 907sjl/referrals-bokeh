"""
PendingReferralsApp.py
Control script for the pending referrals measures Bokeh application.
https://907sjl.github.io/
"""

from jinja2 import Environment, FileSystemLoader

from bokeh.document import Document
from bokeh.core.property.vectorization import Field

from datetime import date, datetime

import model.WaitTimes as wt
import model.Pending as p
import app.common as v
import app.plot.AgeDistributionPlot as adp
import app.plot.CategoryBarsPlot as cbp


class PendingAgeDistributionPlot(adp.AgeDistributionPlot):
    """
    This class is an override of AgeDistributionPlot to show a similar visualization for
    the ages of referrals that are pending to be seen.
    """

    def __init__(self,
                 doc: Document,
                 plot_name: str,
                 category_measure: str,
                 bar_color_map: Field,
                 data_point_color_map: Field,
                 plot_width: int = 500,
                 plot_height: int = 180,
                 include_curve: bool = False):
        super().__init__(doc,
                         plot_name,
                         category_measure,
                         [],
                         bar_color_map,
                         data_point_color_map,
                         plot_width,
                         plot_height,
                         include_curve)
    # END __init__

    def load_clinic_data(self, month: datetime, clinic: str) -> None:
        # Build list of distribution counts in same order as categories
        all_counts = []
        for category in self.categories:
            if self.category_measure == 'get_on_hold_age_by_category':
                category_count = p.get_on_hold_age_by_category(clinic, category)
            elif self.category_measure == 'get_pending_reschedule_age_by_category':
                category_count = p.get_pending_reschedule_age_by_category(clinic, category)
            elif self.category_measure == 'get_pending_acceptance_age_by_category':
                category_count = p.get_pending_acceptance_age_by_category(clinic, category)
            elif self.category_measure == 'get_accepted_referral_age_by_category':
                category_count = p.get_accepted_referral_age_by_category(clinic, category)
            else:
                category_count = 0
            all_counts.append(category_count)

        # Create a dataframe with the referral distribution data
        self.distribution_data = {'category': self.categories, 'referral_count': all_counts}
    # END load_clinic_data
# END CLASS PendingAgeDistributionPlot


class PendingReferralsApp:
    """
    This class represents the Bokeh application with pending referrals measures.
    """

    # Class level properties
    app_title = 'Pending Referrals Report'
    app_template = "pending.html"
    app_root = 'referrals'
    app_env = Environment(loader=FileSystemLoader('templates'))

    def __init__(self, doc: Document):
        self.clinic = 'Immunology'
        self.document = doc
        percentage_color_mapper, age_category_color_mapper, age_category_label_color_mapper = (
            v.create_color_mappers(v.HEAT_MAP_PALETTE, v.AGE_CATEGORY_COLOR_MAP, v.AGE_CATEGORY_LABEL_COLOR_MAP))
        self.percentage_color_mapper = percentage_color_mapper
        self.age_category_color_mapper = age_category_color_mapper
        self.age_category_label_color_mapper = age_category_label_color_mapper
        self.on_hold_distribution_plot = PendingAgeDistributionPlot(doc,
                                                                    'on_hold_distribution_histogram',
                                                                    'get_on_hold_age_by_category',
                                                                    self.age_category_color_mapper,
                                                                    self.age_category_label_color_mapper,
                                                                    272, 236)
        self.reschedule_distribution_plot = PendingAgeDistributionPlot(doc,
                                                                       'reschedule_distribution_histogram',
                                                                       'get_pending_reschedule_age_by_category',
                                                                       self.age_category_color_mapper,
                                                                       self.age_category_label_color_mapper,
                                                                       272, 236)
        self.pending_distribution_plot = PendingAgeDistributionPlot(doc,
                                                                    'acceptance_distribution_histogram',
                                                                    'get_pending_acceptance_age_by_category',
                                                                    self.age_category_color_mapper,
                                                                    self.age_category_label_color_mapper,
                                                                    272, 236)
        self.accepted_distribution_plot = PendingAgeDistributionPlot(doc,
                                                                     'accepted_distribution_histogram',
                                                                     'get_accepted_referral_age_by_category',
                                                                     self.age_category_color_mapper,
                                                                     self.age_category_label_color_mapper,
                                                                     272, 236)
        self.on_hold_category_plot = cbp.CategoryBarsPlot(doc,
                                                          'on_hold_reason_bar_chart',
                                                          'get_counts_by_on_hold_reason',
                                                          'Reason for Hold',
                                                          'Referrals Aged')
        self.reschedule_category_plot = cbp.CategoryBarsPlot(doc,
                                                             'reschedule_status_bar_chart',
                                                             'get_counts_by_pending_reschedule_sub_status',
                                                             'Referral Sub-Status',
                                                             'Referrals Aged')
        self.pending_category_plot = cbp.CategoryBarsPlot(doc,
                                                          'acceptance_status_bar_chart',
                                                          'get_counts_by_pending_acceptance_sub_status',
                                                          'Referral Sub-Status',
                                                          'Referrals Aged')
        self.accepted_category_plot = cbp.CategoryBarsPlot(doc,
                                                           'accepted_status_bar_chart',
                                                           'get_counts_by_accepted_referral_sub_status',
                                                           'Referral Sub-Status',
                                                           'Referrals Aged')
    # END __init__

    # Methods

    def add_on_hold_referral_measures(self, month: datetime) -> None:
        self.on_hold_category_plot.load_clinic_data(month, self.clinic)
        self.on_hold_category_plot.create_plot_data()
        self.on_hold_category_plot.add_plot()
    # END add_on_hold_referral_measures

    def update_on_hold_referral_measures(self, month: datetime) -> None:
        self.on_hold_category_plot.load_clinic_data(month, self.clinic)
        self.on_hold_category_plot.create_plot_data()
        self.on_hold_category_plot.update_plot()
    # END update_on_hold_referral_measures

    def add_on_hold_age_distribution(self, month: datetime) -> None:

        self.on_hold_distribution_plot.load_clinic_data(month, self.clinic)
        self.on_hold_distribution_plot.create_plot_data()
        self.on_hold_distribution_plot.add_plot()

        on_hold_referral_count = sum(self.on_hold_distribution_plot.distribution_data['referral_count'])

        # Add data as Jinja2 variables to render via HTML
        self.document.template_variables["on_hold_referral_count"] = str(on_hold_referral_count)
    # END add_on_hold_age_distribution

    def update_on_hold_age_distribution(self, month: datetime) -> None:
        self.on_hold_distribution_plot.load_clinic_data(month, self.clinic)
        self.on_hold_distribution_plot.create_plot_data()
        self.on_hold_distribution_plot.update_plot()
    # END update_on_hold_age_distribution

    def add_pending_reschedule_referral_measures(self, month: datetime) -> None:
        self.reschedule_category_plot.load_clinic_data(month, self.clinic)
        self.reschedule_category_plot.create_plot_data()
        self.reschedule_category_plot.add_plot()
    # END add_pending_reschedule_referral_measures

    def update_pending_reschedule_referral_measures(self, month: datetime) -> None:
        self.reschedule_category_plot.load_clinic_data(month, self.clinic)
        self.reschedule_category_plot.create_plot_data()
        self.reschedule_category_plot.update_plot()
    # END add_pending_reschedule_referral_measures

    def add_pending_reschedule_age_distribution(self, month: datetime) -> None:

        self.reschedule_distribution_plot.load_clinic_data(month, self.clinic)
        self.reschedule_distribution_plot.create_plot_data()
        self.reschedule_distribution_plot.add_plot()

        reschedule_referral_count = sum(self.reschedule_distribution_plot.distribution_data['referral_count'])

        # Add data as Jinja2 variables to render via HTML
        self.document.template_variables["reschedule_referral_count"] = str(reschedule_referral_count)
    # END add_pending_reschedule_age_distribution

    def update_pending_reschedule_age_distribution(self, month: datetime) -> None:
        self.reschedule_distribution_plot.load_clinic_data(month, self.clinic)
        self.reschedule_distribution_plot.create_plot_data()
        self.reschedule_distribution_plot.update_plot()
    # END update_pending_reschedule_age_distribution

    def add_pending_acceptance_referral_measures(self, month: datetime) -> None:
        self.pending_category_plot.load_clinic_data(month, self.clinic)
        self.pending_category_plot.create_plot_data()
        self.pending_category_plot.add_plot()
    # END add_pending_acceptance_referral_measures

    def update_pending_acceptance_referral_measures(self, month: datetime) -> None:
        self.pending_category_plot.load_clinic_data(month, self.clinic)
        self.pending_category_plot.create_plot_data()
        self.pending_category_plot.update_plot()
    # END update_pending_acceptance_referral_measures

    def add_pending_acceptance_age_distribution(self, month: datetime) -> None:

        self.pending_distribution_plot.load_clinic_data(month, self.clinic)
        self.pending_distribution_plot.create_plot_data()
        self.pending_distribution_plot.add_plot()

        pending_referral_count = sum(self.pending_distribution_plot.distribution_data['referral_count'])

        # Add data as Jinja2 variables to render via HTML
        self.document.template_variables["acceptance_referral_count"] = str(pending_referral_count)
    # END add_pending_acceptance_age_distribution

    def update_pending_acceptance_age_distribution(self, month: datetime) -> None:
        self.pending_distribution_plot.load_clinic_data(month, self.clinic)
        self.pending_distribution_plot.create_plot_data()
        self.pending_distribution_plot.update_plot()
    # END update_pending_acceptance_age_distribution

    def add_accepted_status_referral_measures(self, month: datetime) -> None:
        self.accepted_category_plot.load_clinic_data(month, self.clinic)
        self.accepted_category_plot.create_plot_data()
        self.accepted_category_plot.add_plot()
    # END add_accepted_status_referral_measures

    def update_accepted_status_referral_measures(self, month: datetime) -> None:
        self.accepted_category_plot.load_clinic_data(month, self.clinic)
        self.accepted_category_plot.create_plot_data()
        self.accepted_category_plot.update_plot()
    # END update_accepted_status_referral_measures

    def add_accepted_status_age_distribution(self, month: datetime) -> None:

        self.accepted_distribution_plot.load_clinic_data(month, self.clinic)
        self.accepted_distribution_plot.create_plot_data()
        self.accepted_distribution_plot.add_plot()

        accepted_referral_count = sum(self.accepted_distribution_plot.distribution_data['referral_count'])

        # Add data as Jinja2 variables to render via HTML
        self.document.template_variables["accepted_referral_count"] = str(accepted_referral_count)
    # END add_accepted_status_age_distribution

    def update_accepted_status_age_distribution(self, month: datetime) -> None:
        self.accepted_distribution_plot.load_clinic_data(month, self.clinic)
        self.accepted_distribution_plot.create_plot_data()
        self.accepted_distribution_plot.update_plot()
    # END update_accepted_status_age_distribution

    def set_clinic(self, clinic: str) -> None:
        self.clinic = clinic

    def clinic_selection_handler(self, attr: str, old, new) -> None:
        self.set_clinic(new)
        self.update_accepted_status_age_distribution(wt.last_month)
        self.update_accepted_status_referral_measures(wt.last_month)
        self.update_pending_acceptance_age_distribution(wt.last_month)
        self.update_pending_acceptance_referral_measures(wt.last_month)
        self.update_pending_reschedule_age_distribution(wt.last_month)
        self.update_pending_reschedule_referral_measures(wt.last_month)
        self.update_on_hold_age_distribution(wt.last_month)
        self.update_on_hold_referral_measures(wt.last_month)
    # END clinic_selection_handler

    def insert_pending_referrals_data(self) -> None:
        # Bokeh application handler to modify a blank document that will be served from a Bokeh
        # server application.  This application will be invoked by the script that is injected into the HTML
        # in the response by Jinja2 when the template is rendered. The Bokeh client script opens
        # a websocket to the Bokeh server application to obtain the contents to render in the browser.  This
        # handler adds content to be rendered into the application document.

        # Grab the clinic name from the HTTP request
        clinic = v.get_clinic_from_request(self.document)
        if len(clinic) > 0:
            self.clinic = clinic

        self.add_on_hold_referral_measures(p.last_month)
        self.add_on_hold_age_distribution(p.last_month)
        self.add_pending_reschedule_referral_measures(p.last_month)
        self.add_pending_reschedule_age_distribution(p.last_month)
        self.add_pending_acceptance_referral_measures(p.last_month)
        self.add_pending_acceptance_age_distribution(p.last_month)
        self.add_accepted_status_referral_measures(p.last_month)
        self.add_accepted_status_age_distribution(p.last_month)
        v.add_clinic_slicer(self.document, wt.last_month, self.clinic, self.clinic_selection_handler)

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
        self.document.template_variables['clinic_name'] = self.clinic
        self.document.template_variables['report_month'] = p.last_month.strftime("%B %Y")
    # END insert_pending_referrals_data
# END CLASS PendingReferralsApp:


def pending_referrals_app_handler(doc: Document) -> None:
    pending_app = PendingReferralsApp(doc)
    pending_app.insert_pending_referrals_data()
# END pending_referrals_app_handler
