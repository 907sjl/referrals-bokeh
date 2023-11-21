"""
CRMUsageApp.py
Control script for the measures of clinic referral management usage Bokeh application.
https://907sjl.github.io/

Classes:
    NotAcceptedStatusPlot - Overrides CategoryBarsPlot to show a similar visualization for referrals not accepted.
    CRMUsageApp - Implements the Bokeh application with measures of Clinic Referral Management system usage.

Functions:
    crm_usage_app_handler - Bokeh app handler function that instantiates the class and initializes.
"""

from jinja2 import Environment, FileSystemLoader

from bokeh.document import Document

from datetime import date, datetime

import model.WaitTimes as wt
import model.CRM as c
import app.common as v
import app.plot.CategoryBarsPlot as cbp
import app.plot.HorizontalRatioPlot as hrp
import app.plot.DataLabelPlot as dlp
import app.plot.DataTablePlot as dtp


class NotAcceptedStatusPlot(cbp.CategoryBarsPlot):
    """
    This class is an override of CategoryBarsPlot to show a similar visualization for
    referrals not accepted by their current status.

    Overrides plot.CategoryBarsPlot

    Public Methods:
        load_clinic_data - Override - Loads the data used to render visualizations.
    """

    def __init__(self,
                 doc: Document,
                 plot_name: str):
        """
        Initialize instances.
        :param doc: The Bokeh document for an instance of this application.
        :param plot_name: The name of the plot in the HTML document
        """
        super().__init__(doc,
                         plot_name,
                         '', 'Referral Status', 'Referrals Aged',
                         plot_width=300)
    # END __init__

    def load_clinic_data(self, month: datetime, clinic: str) -> None:
        """
        Loads the data used to render visualizations.
        :param month: The month to query data from
        :param clinic: The name of the clinic to query data for
        """
        volume_values = c.get_counts_by_not_accepted_referral_status(month, clinic).copy()
        self.ratio_data = {'measure': volume_values[self.category_column].tolist(),
                           'value': volume_values[self.values_column].tolist()}
    # END load_clinic_data
# END CLASS NotAcceptedStatusPlot


class CRMUsageApp:
    """
    This class represents the Bokeh application with measures of clinic referral management usage.

    Public Attributes:
        app_title - The page title for the Bokeh application
        app_template - The html template file used by this application
        app_root - The route through the HTTP server that is the root of HTTP resource requests
        clinic - The currently selected clinic used to collect and render data
        document - The Bokeh document for an instance of this application
        percentage_color_mapper - The gradient color mapper for process wait times
        age_category_color_mapper - The category color mapper for wait time bin backgrounds
        age_category_label_color_mapper - The category color mapper for wait time bin text

    Public Methods:
        get_app_title - Returns the application title prefixed with the selected clinic name
        set_clinic - Sets the currently selected clinic
        insert_clinic_process_data - Sequences the data collection and rendering in the application document
    """

    # Class level properties
    app_title = 'CRM Usage Report'
    app_template = 'crm.html'
    app_root = 'referrals'
    _app_env = Environment(loader=FileSystemLoader('templates'))

    def __init__(self, doc: Document):
        """
        Initialize instances.
        :param doc: The Bokeh document for an instance of this application.
        """
        self.clinic = 'Immunology'
        self.document = doc
        percentage_color_mapper, age_category_color_mapper, age_category_label_color_mapper = (
            v.create_color_mappers(v.HEAT_MAP_PALETTE, v.AGE_CATEGORY_COLOR_MAP, v.AGE_CATEGORY_LABEL_COLOR_MAP))
        self.percentage_color_mapper = percentage_color_mapper
        self.age_category_color_mapper = age_category_color_mapper
        self.age_category_label_color_mapper = age_category_label_color_mapper

        self._label_data_source = dlp.LabelDataSource(doc, 'label_data_source')
        self._not_accepted_status_plot = NotAcceptedStatusPlot(doc, 'not_accepted_status_bar_chart')
        self._dsm_import_ratio_plot = hrp.HorizontalRatioPlot(doc,
                                                              'dsm_to_crm_ratio_bar_chart',
                                                              'Patients with DSM and CRM Referrals After 90d',
                                                              'Also in CRM',
                                                              '', '',
                                                              'Patients with DSMs After 90d',
                                                              'DSM Referrals')
        self._linked_ratio_plot = hrp.HorizontalRatioPlot(doc,
                                                          'linked_ratio_bar_chart',
                                                          'Appointments Linked After 90d',
                                                          'Linked in CRM',
                                                          '', '',
                                                          'Referrals Scheduled After 90d',
                                                          'Scheduled')
        self._tagged_ratio_plot = hrp.HorizontalRatioPlot(doc,
                                                          'crm_seen_ratio_bar_chart',
                                                          'Referrals Seen in CRM After 90d',
                                                          'Seen in CRM',
                                                          'Referrals Completed and Seen After 90d',
                                                          'Completed',
                                                          'Referrals Seen After 90d',
                                                          'All Seen')

        # Process rate labels
        self._kept_referral_count_plot = dlp.CallbackLabelPlot(doc,
                                                               self._label_data_source,
                                                               'kept_referral_count_plot',
                                                               '100')
        self._accepted_ratio_plot = dlp.CallbackLabelPlot(doc,
                                                          self._label_data_source,
                                                          'accepted_ratio_plot',
                                                          '100%')
        self._scheduled_referral_count_plot = dlp.CallbackLabelPlot(doc,
                                                                    self._label_data_source,
                                                                    'scheduled_referral_count_plot',
                                                                    '100')
        self._linked_appointment_ratio_plot = dlp.CallbackLabelPlot(doc,
                                                                    self._label_data_source,
                                                                    'linked_appointment_ratio_plot',
                                                                    '100%')
        self._seen_referral_count_plot = dlp.CallbackLabelPlot(doc,
                                                               self._label_data_source,
                                                               'seen_referral_count_plot',
                                                               '100')
        self._crm_seen_referral_ratio_plot = dlp.CallbackLabelPlot(doc,
                                                                   self._label_data_source,
                                                                   'crm_seen_referral_ratio_plot',
                                                                   '100%')
        self._seen_and_completed_ratio_plot = dlp.CallbackLabelPlot(doc,
                                                                    self._label_data_source,
                                                                    'seen_and_completed_ratio_plot',
                                                                    '100%')
        self._dsm_referral_count_plot = dlp.CallbackLabelPlot(doc,
                                                              self._label_data_source,
                                                              'dsm_referral_count_plot',
                                                              '100')
        self._dsm_to_crm_referral_ratio_plot = dlp.CallbackLabelPlot(doc,
                                                                     self._label_data_source,
                                                                     'dsm_to_crm_referral_ratio_plot',
                                                                     '100%')
        self._total_test_score_plot = dlp.CallbackLabelPlot(doc,
                                                            self._label_data_source,
                                                            'total_test_score_plot',
                                                            '99.99')
        self._total_test_value_plot = dlp.CallbackLabelPlot(doc,
                                                            self._label_data_source,
                                                            'total_test_value_plot',
                                                            '99.99')
        self._total_test_percent_plot = dlp.CallbackLabelPlot(doc,
                                                              self._label_data_source,
                                                              'total_test_percent_plot',
                                                              '100%')

        # Data table
        self._crm_usage_score_table = dtp.DataTablePlot(doc,
                                                        'crm_usage_score_table',
                                                        {'columns': ['Title', 'Result %', 'Point Value', 'Score'],
                                                         'classes': ['text-data',
                                                                     'percent-data',
                                                                     'numeric-data',
                                                                     'numeric-data']})
    # END __init__

    def _add_measures_of_dsm_imports(self, month: datetime) -> None:
        """
        Collects and renders data showing the rate at which direct secure
        messages are converted to referrals.
        :param month: The month to query data in
        """
        self._dsm_import_ratio_plot.load_clinic_data(month, self.clinic)
        self._dsm_import_ratio_plot.create_plot_data()
        self._dsm_import_ratio_plot.add_plot()

        if self._dsm_import_ratio_plot.ratio_data['DSM Referrals'] == 0:
            crm_referral_ratio = 1.0
        else:
            crm_referral_ratio = (self._dsm_import_ratio_plot.ratio_data['Also in CRM'] /
                                  self._dsm_import_ratio_plot.ratio_data['DSM Referrals'])

        # Add a point score to the import milestone test of CRM use
        c.set_crm_usage_score_for_clinic(month, self.clinic, 'Import', crm_referral_ratio)

        # Data driven labels
        self._dsm_to_crm_referral_ratio_plot.set_label_text(str(v.half_up_int(crm_referral_ratio * 100.0)) + '%')
        self._dsm_referral_count_plot.set_label_text(str(self._dsm_import_ratio_plot.ratio_data['DSM Referrals']))
    # END add_measures_of_dsm_imports

    def _update_measures_of_dsm_imports(self, month: datetime) -> None:
        """
        Collects and updates data showing the rate at which direct secure
        messages are converted to referrals.  This is called to update a
        previously rendered document.
        :param month: The month to query data in
        """
        self._dsm_import_ratio_plot.load_clinic_data(month, self.clinic)
        self._dsm_import_ratio_plot.create_plot_data()
        self._dsm_import_ratio_plot.change_plot()

        if self._dsm_import_ratio_plot.ratio_data['DSM Referrals'] == 0:
            crm_referral_ratio = 1.0
        else:
            crm_referral_ratio = (self._dsm_import_ratio_plot.ratio_data['Also in CRM'] /
                                  self._dsm_import_ratio_plot.ratio_data['DSM Referrals'])

        # Add a point score to the import milestone test of CRM use
        c.set_crm_usage_score_for_clinic(month, self.clinic, 'Import', crm_referral_ratio)

        # Data driven labels
        self._dsm_to_crm_referral_ratio_plot.set_label_text(str(v.half_up_int(crm_referral_ratio * 100.0)) + '%')
        self._dsm_referral_count_plot.set_label_text(str(self._dsm_import_ratio_plot.ratio_data['DSM Referrals']))
    # END update_measures_of_dsm_imports

    def _add_measures_of_referrals_tagged_as_seen(self, month: datetime) -> None:
        """
        Collects and renders data showing the rate at which referrals are tagged
        as seen when the patient is seen.
        :param month: The month to query data in
        """
        self._tagged_ratio_plot.load_clinic_data(month, self.clinic)
        self._tagged_ratio_plot.create_plot_data()
        self._tagged_ratio_plot.add_plot()

        if self._tagged_ratio_plot.ratio_data['All Seen'] > 0:
            crm_seen_referral_ratio = (self._tagged_ratio_plot.ratio_data['Seen in CRM'] /
                                       self._tagged_ratio_plot.ratio_data['All Seen'])
        else:
            crm_seen_referral_ratio = 0.0

        # Seen referrals completed ratio
        if self._tagged_ratio_plot.ratio_data['All Seen'] > 0:
            seen_and_completed_ratio = (self._tagged_ratio_plot.ratio_data['Completed'] /
                                        self._tagged_ratio_plot.ratio_data['All Seen'])
        else:
            seen_and_completed_ratio = 0.0

        # Add a point score to the seen milestone test of CRM use
        c.set_crm_usage_score_for_clinic(month, self.clinic, 'Seen', crm_seen_referral_ratio)

        # Add a point score to the completed milestone test of CRM use
        c.set_crm_usage_score_for_clinic(month, self.clinic, 'Completed', seen_and_completed_ratio)

        # Data driven labels
        self._crm_seen_referral_ratio_plot.set_label_text(str(v.half_up_int(crm_seen_referral_ratio * 100.0)) + '%')
        self._seen_and_completed_ratio_plot.set_label_text(str(v.half_up_int(seen_and_completed_ratio * 100.0)) + '%')
        self._seen_referral_count_plot.set_label_text(str(self._tagged_ratio_plot.ratio_data['All Seen']))
    # END add_measures_of_referrals_tagged_as_seen

    def _update_measures_of_referrals_tagged_as_seen(self, month: datetime) -> None:
        """
        Collects and updates data showing the rate at which referrals are tagged
        as seen when the patient is seen.  This is called to update a
        previously rendered document.
        :param month: The month to query data in
        """
        self._tagged_ratio_plot.load_clinic_data(month, self.clinic)
        self._tagged_ratio_plot.create_plot_data()
        self._tagged_ratio_plot.change_plot()

        if self._tagged_ratio_plot.ratio_data['All Seen'] > 0:
            crm_seen_referral_ratio = (self._tagged_ratio_plot.ratio_data['Seen in CRM'] /
                                       self._tagged_ratio_plot.ratio_data['All Seen'])
        else:
            crm_seen_referral_ratio = 0.0

        # Seen referrals completed ratio
        if self._tagged_ratio_plot.ratio_data['All Seen'] > 0:
            seen_and_completed_ratio = (self._tagged_ratio_plot.ratio_data['Completed'] /
                                        self._tagged_ratio_plot.ratio_data['All Seen'])
        else:
            seen_and_completed_ratio = 0.0

        # Add a point score to the seen milestone test of CRM use
        c.set_crm_usage_score_for_clinic(month, self.clinic, 'Seen', crm_seen_referral_ratio)

        # Add a point score to the completed milestone test of CRM use
        c.set_crm_usage_score_for_clinic(month, self.clinic, 'Completed', seen_and_completed_ratio)

        # Data driven labels
        self._crm_seen_referral_ratio_plot.set_label_text(str(v.half_up_int(crm_seen_referral_ratio * 100.0)) + '%')
        self._seen_and_completed_ratio_plot.set_label_text(str(v.half_up_int(seen_and_completed_ratio * 100.0)) + '%')
        self._seen_referral_count_plot.set_label_text(str(self._tagged_ratio_plot.ratio_data['All Seen']))
    # END update_measures_of_referrals_tagged_as_seen

    def add_measures_of_linked_appointments(self, month: datetime) -> None:
        """
        Collects and renders data showing the rate at which appointments are linked
        to referrals when the patient is scheduled.
        :param month: The month to query data in
        """
        self._linked_ratio_plot.load_clinic_data(month, self.clinic)
        self._linked_ratio_plot.create_plot_data()
        self._linked_ratio_plot.add_plot()

        if self._linked_ratio_plot.ratio_data['Scheduled'] > 0:
            linked_appointment_ratio = (self._linked_ratio_plot.ratio_data['Linked in CRM'] /
                                        self._linked_ratio_plot.ratio_data['Scheduled'])
        else:
            linked_appointment_ratio = 0.0

        # Add a point score to the linked milestone test of CRM use
        c.set_crm_usage_score_for_clinic(month, self.clinic, 'Linked', linked_appointment_ratio)

        # Data driven labels
        self._linked_appointment_ratio_plot.set_label_text(str(v.half_up_int(linked_appointment_ratio * 100.0)) + '%')
        self._scheduled_referral_count_plot.set_label_text(str(self._linked_ratio_plot.ratio_data['Scheduled']))
    # END add_measures_of_linked_appointments

    def update_measures_of_linked_appointments(self, month: datetime) -> None:
        """
        Collects and updates data showing the rate at which appointments are linked
        to referrals when the patient is scheduled.  This is called to update a
        previously rendered document.
        :param month: The month to query data in
        """
        self._linked_ratio_plot.load_clinic_data(month, self.clinic)
        self._linked_ratio_plot.create_plot_data()
        self._linked_ratio_plot.change_plot()

        if self._linked_ratio_plot.ratio_data['Scheduled'] > 0:
            linked_appointment_ratio = (self._linked_ratio_plot.ratio_data['Linked in CRM'] /
                                        self._linked_ratio_plot.ratio_data['Scheduled'])
        else:
            linked_appointment_ratio = 0.0

        # Add a point score to the linked milestone test of CRM use
        c.set_crm_usage_score_for_clinic(month, self.clinic, 'Linked', linked_appointment_ratio)

        # Add data as Jinja2 variables to render via HTML
        self._linked_appointment_ratio_plot.set_label_text(str(v.half_up_int(linked_appointment_ratio * 100.0)) + '%')
        self._scheduled_referral_count_plot.set_label_text(str(self._linked_ratio_plot.ratio_data['Scheduled']))
    # END update_measures_of_linked_appointments

    def add_measures_referrals_not_accepted(self, month: datetime) -> None:
        """
        Collects and renders data showing the rate at which referrals are accepted
        by the clinic.
        :param month: The month to query data in
        """
        self._not_accepted_status_plot.load_clinic_data(month, self.clinic)
        self._not_accepted_status_plot.create_plot_data()
        self._not_accepted_status_plot.add_plot()

        # Accepted ratio
        accepted_count = v.half_up_int(
            wt.get_clinic_count_measure(month, self.clinic, 'Referrals Accepted After 90d'))
        kept_referral_count = v.half_up_int(
            wt.get_clinic_count_measure(month, self.clinic, 'Referrals Aged'))
        if kept_referral_count > 0:
            accepted_ratio = accepted_count / kept_referral_count
        else:
            accepted_ratio = 0.0

        # Add a point score to the accept milestone test of CRM use
        c.set_crm_usage_score_for_clinic(month, self.clinic, 'Accepted', accepted_ratio)

        # Data driven labels
        self._accepted_ratio_plot.set_label_text(str(v.half_up_int(accepted_ratio * 100.0)) + '%')
        self._kept_referral_count_plot.set_label_text(str(kept_referral_count))
    # END add_measures_referrals_not_accepted

    def update_measures_referrals_not_accepted(self, month: datetime) -> None:
        """
        Collects and updates data showing the rate at which referrals are accepted
        by the clinic.  This is called to update a previously rendered document.
        :param month: The month to query data in
        """
        self._not_accepted_status_plot.load_clinic_data(month, self.clinic)
        self._not_accepted_status_plot.create_plot_data()
        self._not_accepted_status_plot.update_plot()

        # Accepted ratio
        accepted_count = v.half_up_int(
            wt.get_clinic_count_measure(month, self.clinic, 'Referrals Accepted After 90d'))
        kept_referral_count = v.half_up_int(
            wt.get_clinic_count_measure(month, self.clinic, 'Referrals Aged'))
        if kept_referral_count > 0:
            accepted_ratio = accepted_count / kept_referral_count
        else:
            accepted_ratio = 0.0

        # Add a point score to the accept milestone test of CRM use
        c.set_crm_usage_score_for_clinic(month, self.clinic, 'Accepted', accepted_ratio)

        # Data driven labels
        self._accepted_ratio_plot.set_label_text(str(v.half_up_int(accepted_ratio * 100.0)) + '%')
        self._kept_referral_count_plot.set_label_text(str(kept_referral_count))
    # END update_measures_referrals_not_accepted

    def set_clinic(self, clinic: str) -> None:
        """Sets the currently selected clinic."""
        self.clinic = clinic

    def _clinic_selection_handler(self, attr: str, old, new) -> None:
        """
        This function queries new data when the clinic selection changes. This function
        signature matches the requirements for a Bokeh callback in Python.
        :param attr: Not used
        :param old: The previous clinic value before the selection changes
        :param new: The new clinic value after the selection changes
        """
        self.set_clinic(new)
        self.update_measures_referrals_not_accepted(wt.last_month)
        self.update_measures_of_linked_appointments(wt.last_month)
        self._update_measures_of_referrals_tagged_as_seen(wt.last_month)
        self._update_measures_of_dsm_imports(wt.last_month)

        # Data driven HTML table
        tests_vw = c.get_crm_usage_test_results(c.last_month, self.clinic).copy()
        tests_vw['Result %'] = tests_vw['Result'].astype('string') + '%'

        # Data driven labels
        total_test_value = tests_vw['Point Value'].sum()
        total_test_score = tests_vw['Score'].sum()
        self._total_test_value_plot.set_label_text(str(round(total_test_value, 2)))
        self._total_test_score_plot.set_label_text(str(round(total_test_score, 2)))
        (self._total_test_percent_plot.
         set_label_text(str(v.half_up_int((total_test_score / total_test_value) * 100.0)) + '%'))
        self._crm_usage_score_table.create_plot_data(tests_vw)
        self._label_data_source.update_plot_data()
    # END clinic_selection_handler

    def insert_crm_usage_data(self) -> None:
        """
        Sequences the load of data and rendering of visuals for this Bokeh application in response
        to a new document being created for a new Bokeh session.
        """

        # Grab the clinic name from the HTTP request
        clinic = v.get_clinic_from_request(self.document)
        if len(clinic) > 0:
            self.clinic = clinic

        self.add_measures_referrals_not_accepted(c.last_month)
        self.add_measures_of_linked_appointments(c.last_month)
        self._add_measures_of_referrals_tagged_as_seen(c.last_month)
        self._add_measures_of_dsm_imports(c.last_month)
        v.add_clinic_slicer(self.document, wt.last_month, self.clinic, self._clinic_selection_handler)

        # Data driven table
        tests_vw = c.get_crm_usage_test_results(c.last_month, self.clinic).copy()
        tests_vw['Result %'] = tests_vw['Result'].astype('string') + '%'
        self._crm_usage_score_table.create_plot_data(tests_vw)
        self._crm_usage_score_table.add_plot()

        # Data driven labels
        total_test_value = tests_vw['Point Value'].sum()
        total_test_score = tests_vw['Score'].sum()
        self._total_test_value_plot.set_label_text(str(round(total_test_value, 2)))
        self._total_test_score_plot.set_label_text(str(round(total_test_score, 2)))
        (self._total_test_percent_plot.
         set_label_text(str(v.half_up_int((total_test_score / total_test_value) * 100.0)) + '%'))
        self._label_data_source.update_plot_data()
        self._label_data_source.add_plot()

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
        self.document.template_variables['clinic_name'] = self.clinic
        self.document.template_variables['report_month'] = c.last_month.strftime("%B %Y")
    # END insert_crm_usage_data
# END CLASS CRMUsageApp


def crm_usage_app_handler(doc: Document) -> None:
    """
    Bokeh application handler to modify a blank document that will be served from a Bokeh
    server application.  This handler adds content to be rendered into the application document.
    :param doc: The Bokeh document to add content to
    """

    crm_use_app = CRMUsageApp(doc)
    crm_use_app.insert_crm_usage_data()
# END crm_usage_app_handler
