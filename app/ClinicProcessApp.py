"""
ClinicProcessApp.py
Control script for the clinic process measures Bokeh application.
https://907sjl.github.io/
"""

from jinja2 import Environment, FileSystemLoader

from bokeh.document import Document

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

import model.WaitTimes as wt
import app.common as v
import app.plot.AgeDistributionPlot as adp
import app.plot.ReferralVolumePlot as rvp
import app.plot.ProcessGaugePlot as pgp
import app.plot.SeenRatioPlot as srp
import app.plot.DataLabelPlot as dlp


class ClinicProcessApp:
    """
    This class represents the Bokeh application with referral process measures for a clinic.
    """

    # Class level properties
    app_title = 'Referral Process Report'
    app_template = "referrals.html"
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
        self.label_data_source = dlp.LabelDataSource(doc, 'label_data_source')

        # Seen ratio plots
        self.urgent_seen_ratio_plot = srp.SeenRatioPlot(doc,
                                                        'urgent_seen_donut_chart',
                                                        'Urgent Referrals Aged',
                                                        'Urgent Referrals Seen After 5d',
                                                        'Urgent Referrals Waiting After 5d',
                                                        'Urgent Referrals Not Scheduled After 5d')
        self.routine_seen_ratio_plot = srp.SeenRatioPlot(doc,
                                                         'routine_seen_donut_chart',
                                                         'Routine Referrals Aged',
                                                         'Routine Referrals Seen After 30d',
                                                         'Routine Referrals Waiting After 30d',
                                                         'Routine Referrals Not Scheduled After 30d')
        self.all_seen_ratio_plot = srp.SeenRatioPlot(doc,
                                                     'seen_donut_chart',
                                                     'Referrals Aged',
                                                     'Referrals Seen After 90d',
                                                     'Referrals Waiting After 90d',
                                                     'Referrals Not Scheduled After 90d')
        self.all_seen_ratio_plot.ratio_measures[2] = 'Unmet'

        # Referral volume plots
        self.urgent_volume_plot = rvp.ReferralVolumePlot(doc,
                                                         'urgent_volume_bar_chart',
                                                         'Urgent Referrals Sent',
                                                         'Urgent Referrals Canceled After 5d',
                                                         'Urgent Referrals Rejected After 5d',
                                                         'Urgent Referrals Closed WBS After 5d')
        self.routine_volume_plot = rvp.ReferralVolumePlot(doc,
                                                          'routine_volume_bar_chart',
                                                          'Routine Referrals Sent',
                                                          'Routine Referrals Canceled After 30d',
                                                          'Routine Referrals Rejected After 30d',
                                                          'Routine Referrals Closed WBS After 30d')
        self.all_volume_plot = rvp.ReferralVolumePlot(doc,
                                                      'volume_bar_chart',
                                                      'Referrals Sent',
                                                      'Referrals Canceled After 90d',
                                                      'Referrals Rejected After 90d',
                                                      'Referrals Closed WBS After 90d')
        self.process_volume_plot = rvp.ReferralVolumePlot(doc,
                                                          'process_volume_bar_chart',
                                                          'Referrals Aged',
                                                          'Referrals Accepted After 90d',
                                                          'Referrals Scheduled After 90d',
                                                          'Referrals Completed After 90d')
        self.process_volume_plot.volume_measures = ['Aged', 'Accepted', 'Scheduled', 'Completed']

        # Process aim plots
        self.urgent_aim_plot = pgp.ProcessGaugePlot(doc,
                                                    'urgent_aim_gauge',
                                                    'MOV28 Pct Urgent Referrals Seen in 5d',
                                                    'Target Pct Urgent Referrals Seen in 5d',
                                                    self.percentage_color_mapper)
        self.routine_aim_plot = pgp.ProcessGaugePlot(doc,
                                                     'routine_aim_gauge',
                                                     'MOV28 Pct Routine Referrals Seen in 30d',
                                                     'Target Pct Routine Referrals Seen in 30d',
                                                     self.percentage_color_mapper)

        # Histogram of days to seen
        self.seen_histogram_plot = adp.AgeDistributionPlot(doc,
                                                           'all_distribution_curve',
                                                           'Age Category to Seen',
                                                           ['Urgent', 'Routine'],
                                                           self.age_category_color_mapper,
                                                           self.age_category_label_color_mapper,
                                                           include_curve=True)

        # Inclusion dates data labels
        self.urgent_min_date_plot = dlp.CallbackLabelPlot(doc,
                                                          self.label_data_source,
                                                          'urgent_min_date_plot',
                                                          '01/02/03')
        self.urgent_max_date_plot = dlp.CallbackLabelPlot(doc,
                                                          self.label_data_source,
                                                          'urgent_max_date_plot',
                                                          '01/02/03')
        self.routine_min_date_plot = dlp.CallbackLabelPlot(doc,
                                                           self.label_data_source,
                                                           'routine_min_date_plot',
                                                           '01/02/03')
        self.routine_max_date_plot = dlp.CallbackLabelPlot(doc,
                                                           self.label_data_source,
                                                           'routine_max_date_plot',
                                                           '01/02/03')
        self.all_min_date_plot = dlp.CallbackLabelPlot(doc,
                                                       self.label_data_source,
                                                       'all_min_date_plot',
                                                       '01/02/03')
        self.all_max_date_plot = dlp.CallbackLabelPlot(doc,
                                                       self.label_data_source,
                                                       'all_max_date_plot',
                                                       '01/02/03')

        # Process rate labels
        self.all_accepted_rate_plot = dlp.CallbackLabelPlot(doc,
                                                            self.label_data_source,
                                                            'all_accepted_rate_plot',
                                                            '100%')
        self.all_scheduled_rate_plot = dlp.CallbackLabelPlot(doc,
                                                             self.label_data_source,
                                                             'all_scheduled_rate_plot',
                                                             '100%')
        self.all_completed_rate_plot = dlp.CallbackLabelPlot(doc,
                                                             self.label_data_source,
                                                             'all_completed_rate_plot',
                                                             '100%')
        self.median_days_to_accepted_plot = dlp.CallbackLabelPlot(doc,
                                                                  self.label_data_source,
                                                                  'median_days_to_accepted_plot',
                                                                  '100')
        self.median_days_to_scheduled_plot = dlp.CallbackLabelPlot(doc,
                                                                   self.label_data_source,
                                                                   'median_days_to_scheduled_plot',
                                                                   '100')
        self.median_days_to_completed_plot = dlp.CallbackLabelPlot(doc,
                                                                   self.label_data_source,
                                                                   'median_days_to_completed_plot',
                                                                   '100')
        self.median_days_to_seen_plot = dlp.CallbackLabelPlot(doc,
                                                              self.label_data_source,
                                                              'median_days_to_seen_plot',
                                                              '100')

        # Routine process aim labels
        self.routine_ratio_3_month_plot = dlp.CallbackLabelPlot(doc,
                                                                self.label_data_source,
                                                                'routine_ratio_3_month_plot',
                                                                '100%')
        self.routine_variance_3_month_plot = dlp.CallbackLabelPlot(doc,
                                                                   self.label_data_source,
                                                                   'routine_variance_3_month_plot',
                                                                   '100%')
        self.routine_direction_3_month_plot = dlp.CallbackLabelPlot(doc,
                                                                    self.label_data_source,
                                                                    'routine_direction_3_month_plot',
                                                                    '100%')
        self.routine_improvement_dir_3_month_plot = dlp.CallbackLabelPlot(doc,
                                                                          self.label_data_source,
                                                                          'routine_improvement_dir_3_month_plot',
                                                                          '100%')
        self.routine_ratio_6_month_plot = dlp.CallbackLabelPlot(doc,
                                                                self.label_data_source,
                                                                'routine_ratio_6_month_plot',
                                                                '100%')
        self.routine_variance_6_month_plot = dlp.CallbackLabelPlot(doc,
                                                                   self.label_data_source,
                                                                   'routine_variance_6_month_plot',
                                                                   '100%')
        self.routine_direction_6_month_plot = dlp.CallbackLabelPlot(doc,
                                                                    self.label_data_source,
                                                                    'routine_direction_6_month_plot',
                                                                    '100%')
        self.routine_improvement_dir_6_month_plot = dlp.CallbackLabelPlot(doc,
                                                                          self.label_data_source,
                                                                          'routine_improvement_dir_6_month_plot',
                                                                          '100%')
        self.routine_ratio_12_month_plot = dlp.CallbackLabelPlot(doc,
                                                                 self.label_data_source,
                                                                 'routine_ratio_12_month_plot',
                                                                 '100%')
        self.routine_variance_12_month_plot = dlp.CallbackLabelPlot(doc,
                                                                    self.label_data_source,
                                                                    'routine_variance_12_month_plot',
                                                                    '100%')
        self.routine_direction_12_month_plot = dlp.CallbackLabelPlot(doc,
                                                                     self.label_data_source,
                                                                     'routine_direction_12_month_plot',
                                                                     '100%')
        self.routine_improvement_dir_12_month_plot = dlp.CallbackLabelPlot(doc,
                                                                           self.label_data_source,
                                                                           'routine_improvement_dir_12_month_plot',
                                                                           '100%')

        # Process aim targets
        self.routine_ratio_target_plot = dlp.CallbackLabelPlot(doc,
                                                               self.label_data_source,
                                                               'routine_ratio_target_plot',
                                                               '100%')
        self.urgent_ratio_target_plot = dlp.CallbackLabelPlot(doc,
                                                              self.label_data_source,
                                                              'urgent_ratio_target_plot',
                                                              '100%')

        # Urgent process aim labels
        self.urgent_ratio_3_month_plot = dlp.CallbackLabelPlot(doc,
                                                               self.label_data_source,
                                                               'urgent_ratio_3_month_plot',
                                                               '100%')
        self.urgent_variance_3_month_plot = dlp.CallbackLabelPlot(doc,
                                                                  self.label_data_source,
                                                                  'urgent_variance_3_month_plot',
                                                                  '100%')
        self.urgent_direction_3_month_plot = dlp.CallbackLabelPlot(doc,
                                                                   self.label_data_source,
                                                                   'urgent_direction_3_month_plot',
                                                                   '100%')
        self.urgent_improvement_dir_3_month_plot = dlp.CallbackLabelPlot(doc,
                                                                         self.label_data_source,
                                                                         'urgent_improvement_dir_3_month_plot',
                                                                         '100%')
        self.urgent_ratio_6_month_plot = dlp.CallbackLabelPlot(doc,
                                                               self.label_data_source,
                                                               'urgent_ratio_6_month_plot',
                                                               '100%')
        self.urgent_variance_6_month_plot = dlp.CallbackLabelPlot(doc,
                                                                  self.label_data_source,
                                                                  'urgent_variance_6_month_plot',
                                                                  '100%')
        self.urgent_direction_6_month_plot = dlp.CallbackLabelPlot(doc,
                                                                   self.label_data_source,
                                                                   'urgent_direction_6_month_plot',
                                                                   '100%')
        self.urgent_improvement_dir_6_month_plot = dlp.CallbackLabelPlot(doc,
                                                                         self.label_data_source,
                                                                         'urgent_improvement_dir_6_month_plot',
                                                                         '100%')
        self.urgent_ratio_12_month_plot = dlp.CallbackLabelPlot(doc,
                                                                self.label_data_source,
                                                                'urgent_ratio_12_month_plot',
                                                                '100%')
        self.urgent_variance_12_month_plot = dlp.CallbackLabelPlot(doc,
                                                                   self.label_data_source,
                                                                   'urgent_variance_12_month_plot',
                                                                   '100%')
        self.urgent_direction_12_month_plot = dlp.CallbackLabelPlot(doc,
                                                                    self.label_data_source,
                                                                    'urgent_direction_12_month_plot',
                                                                    '100%')
        self.urgent_improvement_dir_12_month_plot = dlp.CallbackLabelPlot(doc,
                                                                          self.label_data_source,
                                                                          'urgent_improvement_dir_12_month_plot',
                                                                          '100%')
    # END __init__

    def get_app_title(self) -> str:
        return self.clinic + ' ' + self.app_title

    def add_referral_volume_plots(self, month: datetime):
        """
        Add plots for clinic referral volume measures to a Bokeh document.
        :param month: month of performance to visualize
        :return: none
        """

        # Data to calculate volume measures after 5 days
        self.urgent_volume_plot.load_clinic_data(month, self.clinic)
        self.urgent_volume_plot.create_plot_data()
        self.urgent_volume_plot.add_plot()

        # Data to calculate volume measures after 30 days
        self.routine_volume_plot.load_clinic_data(month, self.clinic)
        self.routine_volume_plot.create_plot_data()
        self.routine_volume_plot.add_plot()

        # Data to calculate volume measures after 90 days
        self.all_volume_plot.load_clinic_data(month, self.clinic)
        self.all_volume_plot.create_plot_data()
        self.all_volume_plot.add_plot()

        # Data to calculate volume of referrals by process milestone after 90 days
        self.process_volume_plot.load_clinic_data(month, self.clinic)
        self.process_volume_plot.create_plot_data()
        self.process_volume_plot.add_plot()

        # Dates of urgent referrals counted
        urgent_first_date = month + relativedelta(days=-5)
        urgent_last_date = month + relativedelta(months=1) + relativedelta(days=-6)
        routine_first_date = month + relativedelta(days=-30)
        routine_last_date = month + relativedelta(months=1) + relativedelta(days=-31)
        first_date = month + relativedelta(days=-90)
        last_date = month + relativedelta(months=1) + relativedelta(days=-91)

        # Data driven labels
        self.urgent_min_date_plot.\
            set_label_text(f'{urgent_first_date.month}/{urgent_first_date.day}/{urgent_first_date:%y}')
        self.urgent_max_date_plot.\
            set_label_text(f'{urgent_last_date.month}/{urgent_last_date.day}/{urgent_last_date:%y}')
        self.routine_min_date_plot.\
            set_label_text(f'{routine_first_date.month}/{routine_first_date.day}/{routine_first_date:%y}')
        self.routine_max_date_plot.\
            set_label_text(f'{routine_last_date.month}/{routine_last_date.day}/{routine_last_date:%y}')
        self.all_min_date_plot.\
            set_label_text(f'{first_date.month}/{first_date.day}/{first_date:%y}')
        self.all_max_date_plot.\
            set_label_text(f'{last_date.month}/{last_date.day}/{last_date:%y}')
    # END add_referral_volume_plots

    def update_referral_volume_plots(self, month: datetime):
        """
        Update plots for clinic referral volume measures in a Bokeh document.
        :param month: month of performance to visualize
        :return: none
        """

        # Data to calculate volume measures after 5 days
        self.urgent_volume_plot.load_clinic_data(month, self.clinic)
        self.urgent_volume_plot.create_plot_data()

        # Data to calculate volume measures after 30 days
        self.routine_volume_plot.load_clinic_data(month, self.clinic)
        self.routine_volume_plot.create_plot_data()

        # Data to calculate volume measures after 90 days
        self.all_volume_plot.load_clinic_data(month, self.clinic)
        self.all_volume_plot.create_plot_data()

        # Data to calculate volume of referrals by process milestone after 90 days
        self.process_volume_plot.load_clinic_data(month, self.clinic)
        self.process_volume_plot.create_plot_data()

        # Dates of urgent referrals counted
        urgent_first_date = month + relativedelta(days=-5)
        urgent_last_date = month + relativedelta(months=1) + relativedelta(days=-6)
        routine_first_date = month + relativedelta(days=-30)
        routine_last_date = month + relativedelta(months=1) + relativedelta(days=-31)
        first_date = month + relativedelta(days=-90)
        last_date = month + relativedelta(months=1) + relativedelta(days=-91)

        # Data driven labels
        self.urgent_min_date_plot.\
            set_label_text(f'{urgent_first_date.month}/{urgent_first_date.day}/{urgent_first_date:%y}')
        self.urgent_max_date_plot.\
            set_label_text(f'{urgent_last_date.month}/{urgent_last_date.day}/{urgent_last_date:%y}')
        self.routine_min_date_plot.\
            set_label_text(f'{routine_first_date.month}/{routine_first_date.day}/{routine_first_date:%y}')
        self.routine_max_date_plot.\
            set_label_text(f'{routine_last_date.month}/{routine_last_date.day}/{routine_last_date:%y}')
        self.all_min_date_plot.\
            set_label_text(f'{first_date.month}/{first_date.day}/{first_date:%y}')
        self.all_max_date_plot.\
            set_label_text(f'{last_date.month}/{last_date.day}/{last_date:%y}')
    # END update_referral_volume_plots

    def add_seen_ratio_plots(self, month: datetime):
        """
        Add plots for clinic referral seen ratios to a Bokeh document.
        :param month: month of data to visualize
        :return: none
        """

        # Data to calculate seen ratio measures after 5 days
        self.urgent_seen_ratio_plot.load_clinic_data(month, self.clinic)
        self.urgent_seen_ratio_plot.create_plot_data()
        self.urgent_seen_ratio_plot.add_plot()

        # Data to calculate seen ratio measures after 30 days
        self.routine_seen_ratio_plot.load_clinic_data(month, self.clinic)
        self.routine_seen_ratio_plot.create_plot_data()
        self.routine_seen_ratio_plot.add_plot()

        # Data to calculate seen ratio measures after 90 days
        self.all_seen_ratio_plot.load_clinic_data(month, self.clinic)
        self.all_seen_ratio_plot.create_plot_data()
        self.all_seen_ratio_plot.add_plot()
    # END add_seen_ratio_plots

    def update_seen_ratio_plots(self, month: datetime):
        """
        Updates existing plots for clinic referral seen ratios to a Bokeh document.
        :param month: month of data to visualize
        :return: none
        """

        # Data to calculate seen ratio measures after 5 days
        self.urgent_seen_ratio_plot.load_clinic_data(month, self.clinic)
        self.urgent_seen_ratio_plot.create_plot_data()

        # Data to calculate seen ratio measures after 30 days
        self.routine_seen_ratio_plot.load_clinic_data(month, self.clinic)
        self.routine_seen_ratio_plot.create_plot_data()

        # Data to calculate seen ratio measures after 90 days
        self.all_seen_ratio_plot.load_clinic_data(month, self.clinic)
        self.all_seen_ratio_plot.create_plot_data()
    # END update_seen_ratio_plots

    def add_urgent_referral_process_aim(self, month: datetime):

        self.urgent_aim_plot.load_clinic_data(month, self.clinic)
        self.urgent_aim_plot.create_plot_data()
        self.urgent_aim_plot.add_plot()

        urgent_ratio_3_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'MOV91 Pct Urgent Referrals Seen in 5d')))
        urgent_variance_3_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var Target MOV91 Pct Urgent Referrals Seen in 5d')))
        urgent_direction_3_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var Target MOV91 Pct Urgent Referrals Seen in 5d'))
        urgent_improvement_3_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var MOV91 Pct Urgent Referrals Seen in 5d')))
        urgent_improvement_dir_3_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var MOV91 Pct Urgent Referrals Seen in 5d'))

        urgent_ratio_6_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'MOV182 Pct Urgent Referrals Seen in 5d')))
        urgent_variance_6_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var Target MOV182 Pct Urgent Referrals Seen in 5d')))
        urgent_direction_6_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var Target MOV182 Pct Urgent Referrals Seen in 5d'))
        urgent_improvement_6_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var MOV182 Pct Urgent Referrals Seen in 5d')))
        urgent_improvement_dir_6_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var MOV182 Pct Urgent Referrals Seen in 5d'))
        urgent_ratio_12_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'MOV364 Pct Urgent Referrals Seen in 5d')))
        urgent_variance_12_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var Target MOV364 Pct Urgent Referrals Seen in 5d')))
        urgent_direction_12_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var Target MOV364 Pct Urgent Referrals Seen in 5d'))
        urgent_improvement_12_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var MOV364 Pct Urgent Referrals Seen in 5d')))
        urgent_improvement_dir_12_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var MOV364 Pct Urgent Referrals Seen in 5d'))

        # Data driven labels
        self.urgent_ratio_3_month_plot.set_label_text(str(urgent_ratio_3_month) + '%')
        self.urgent_variance_3_month_plot.set_label_text(str(urgent_variance_3_month) + '%')
        self.urgent_direction_3_month_plot.set_label_text(str(urgent_direction_3_month))
        self.urgent_improvement_dir_3_month_plot.set_label_text(str(urgent_improvement_dir_3_month))

        self.urgent_ratio_6_month_plot.set_label_text(str(urgent_ratio_6_month) + '%')
        self.urgent_variance_6_month_plot.set_label_text(str(urgent_variance_6_month) + '%')
        self.urgent_direction_6_month_plot.set_label_text(str(urgent_direction_6_month))
        self.urgent_improvement_dir_6_month_plot.set_label_text(str(urgent_improvement_dir_6_month))

        self.urgent_ratio_12_month_plot.set_label_text(str(urgent_ratio_12_month) + '%')
        self.urgent_variance_12_month_plot.set_label_text(str(urgent_variance_12_month) + '%')
        self.urgent_direction_12_month_plot.set_label_text(str(urgent_direction_12_month))
        self.urgent_improvement_dir_12_month_plot.set_label_text(str(urgent_improvement_dir_12_month))

        self.urgent_ratio_target_plot.set_label_text(
                str(int(self.urgent_aim_plot.target_data['value'][0] * 100.0)) + '%')

        # Data driven label styles
        if urgent_variance_3_month < 0:
            self.urgent_direction_3_month_plot.set_label_style("table-data-direction-down")
        else:
            self.urgent_direction_3_month_plot.set_label_style("table-data-direction-up")

        if urgent_improvement_3_month < 0:
            self.urgent_improvement_dir_3_month_plot.set_label_style("table-data-direction-down")
        else:
            self.urgent_improvement_dir_3_month_plot.set_label_style("table-data-direction-up")

        if urgent_variance_6_month < 0:
            self.urgent_direction_6_month_plot.set_label_style("table-data-direction-down")
        else:
            self.urgent_direction_6_month_plot.set_label_style("table-data-direction-up")

        if urgent_improvement_6_month < 0:
            self.urgent_improvement_dir_6_month_plot.set_label_style("table-data-direction-down")
        else:
            self.urgent_improvement_dir_6_month_plot.set_label_style("table-data-direction-up")

        if urgent_variance_12_month < 0:
            self.urgent_direction_12_month_plot.set_label_style("table-data-direction-down")
        else:
            self.urgent_direction_12_month_plot.set_label_style("table-data-direction-up")

        if urgent_improvement_12_month < 0:
            self.urgent_improvement_dir_12_month_plot.set_label_style("table-data-direction-down")
        else:
            self.urgent_improvement_dir_12_month_plot.set_label_style("table-data-direction-up")
    # END add_urgent_referral_process_aim

    def update_urgent_referral_process_aim(self, month: datetime):
        self.urgent_aim_plot.load_clinic_data(month, self.clinic)
        self.urgent_aim_plot.create_plot_data()

        urgent_ratio_3_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'MOV91 Pct Urgent Referrals Seen in 5d')))
        urgent_variance_3_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var Target MOV91 Pct Urgent Referrals Seen in 5d')))
        urgent_direction_3_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var Target MOV91 Pct Urgent Referrals Seen in 5d'))
        urgent_improvement_3_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var MOV91 Pct Urgent Referrals Seen in 5d')))
        urgent_improvement_dir_3_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var MOV91 Pct Urgent Referrals Seen in 5d'))

        urgent_ratio_6_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'MOV182 Pct Urgent Referrals Seen in 5d')))
        urgent_variance_6_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var Target MOV182 Pct Urgent Referrals Seen in 5d')))
        urgent_direction_6_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var Target MOV182 Pct Urgent Referrals Seen in 5d'))
        urgent_improvement_6_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var MOV182 Pct Urgent Referrals Seen in 5d')))
        urgent_improvement_dir_6_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var MOV182 Pct Urgent Referrals Seen in 5d'))
        urgent_ratio_12_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'MOV364 Pct Urgent Referrals Seen in 5d')))
        urgent_variance_12_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var Target MOV364 Pct Urgent Referrals Seen in 5d')))
        urgent_direction_12_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var Target MOV364 Pct Urgent Referrals Seen in 5d'))
        urgent_improvement_12_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var MOV364 Pct Urgent Referrals Seen in 5d')))
        urgent_improvement_dir_12_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var MOV364 Pct Urgent Referrals Seen in 5d'))

        # Data driven labels
        self.urgent_ratio_3_month_plot.set_label_text(str(urgent_ratio_3_month) + '%')
        self.urgent_variance_3_month_plot.set_label_text(str(urgent_variance_3_month) + '%')
        self.urgent_direction_3_month_plot.set_label_text(str(urgent_direction_3_month))
        self.urgent_improvement_dir_3_month_plot.set_label_text(str(urgent_improvement_dir_3_month))

        self.urgent_ratio_6_month_plot.set_label_text(str(urgent_ratio_6_month) + '%')
        self.urgent_variance_6_month_plot.set_label_text(str(urgent_variance_6_month) + '%')
        self.urgent_direction_6_month_plot.set_label_text(str(urgent_direction_6_month))
        self.urgent_improvement_dir_6_month_plot.set_label_text(str(urgent_improvement_dir_6_month))

        self.urgent_ratio_12_month_plot.set_label_text(str(urgent_ratio_12_month) + '%')
        self.urgent_variance_12_month_plot.set_label_text(str(urgent_variance_12_month) + '%')
        self.urgent_direction_12_month_plot.set_label_text(str(urgent_direction_12_month))
        self.urgent_improvement_dir_12_month_plot.set_label_text(str(urgent_improvement_dir_12_month))

        self.urgent_ratio_target_plot.set_label_text(
                str(int(self.urgent_aim_plot.target_data['value'][0] * 100.0)) + '%')

        # Data driven label styles
        if urgent_variance_3_month < 0:
            self.urgent_direction_3_month_plot.set_label_style("table-data-direction-down")
        else:
            self.urgent_direction_3_month_plot.set_label_style("table-data-direction-up")

        if urgent_improvement_3_month < 0:
            self.urgent_improvement_dir_3_month_plot.set_label_style("table-data-direction-down")
        else:
            self.urgent_improvement_dir_3_month_plot.set_label_style("table-data-direction-up")

        if urgent_variance_6_month < 0:
            self.urgent_direction_6_month_plot.set_label_style("table-data-direction-down")
        else:
            self.urgent_direction_6_month_plot.set_label_style("table-data-direction-up")

        if urgent_improvement_6_month < 0:
            self.urgent_improvement_dir_6_month_plot.set_label_style("table-data-direction-down")
        else:
            self.urgent_improvement_dir_6_month_plot.set_label_style("table-data-direction-up")

        if urgent_variance_12_month < 0:
            self.urgent_direction_12_month_plot.set_label_style("table-data-direction-down")
        else:
            self.urgent_direction_12_month_plot.set_label_style("table-data-direction-up")

        if urgent_improvement_12_month < 0:
            self.urgent_improvement_dir_12_month_plot.set_label_style("table-data-direction-down")
        else:
            self.urgent_improvement_dir_12_month_plot.set_label_style("table-data-direction-up")
    # END update_urgent_referral_process_aim

    def add_routine_referral_process_aim(self, month: datetime):

        self.routine_aim_plot.load_clinic_data(month, self.clinic)
        self.routine_aim_plot.create_plot_data()
        self.routine_aim_plot.add_plot()

        routine_ratio_3_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'MOV91 Pct Routine Referrals Seen in 30d')))
        routine_variance_3_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var Target MOV91 Pct Routine Referrals Seen in 30d')))
        routine_direction_3_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var Target MOV91 Pct Routine Referrals Seen in 30d'))
        routine_improvement_3_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var MOV91 Pct Routine Referrals Seen in 30d')))
        routine_improvement_dir_3_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var MOV91 Pct Routine Referrals Seen in 30d'))

        routine_ratio_6_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'MOV182 Pct Routine Referrals Seen in 30d')))
        routine_variance_6_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var Target MOV182 Pct Routine Referrals Seen in 30d')))
        routine_direction_6_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var Target MOV182 Pct Routine Referrals Seen in 30d'))
        routine_improvement_6_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var MOV182 Pct Routine Referrals Seen in 30d')))
        routine_improvement_dir_6_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var MOV182 Pct Routine Referrals Seen in 30d'))

        routine_ratio_12_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'MOV364 Pct Routine Referrals Seen in 30d')))
        routine_variance_12_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var Target MOV364 Pct Routine Referrals Seen in 30d')))
        routine_direction_12_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var Target MOV364 Pct Routine Referrals Seen in 30d'))
        routine_improvement_12_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var MOV364 Pct Routine Referrals Seen in 30d')))
        routine_improvement_dir_12_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var MOV364 Pct Routine Referrals Seen in 30d'))

        # Data driven labels
        self.routine_ratio_3_month_plot.set_label_text(str(routine_ratio_3_month) + '%')
        self.routine_variance_3_month_plot.set_label_text(str(routine_variance_3_month) + '%')
        self.routine_direction_3_month_plot.set_label_text(str(routine_direction_3_month))
        self.routine_improvement_dir_3_month_plot.set_label_text(str(routine_improvement_dir_3_month))

        self.routine_ratio_6_month_plot.set_label_text(str(routine_ratio_6_month) + '%')
        self.routine_variance_6_month_plot.set_label_text(str(routine_variance_6_month) + '%')
        self.routine_direction_6_month_plot.set_label_text(str(routine_direction_6_month))
        self.routine_improvement_dir_6_month_plot.set_label_text(str(routine_improvement_dir_6_month))

        self.routine_ratio_12_month_plot.set_label_text(str(routine_ratio_12_month) + '%')
        self.routine_variance_12_month_plot.set_label_text(str(routine_variance_12_month) + '%')
        self.routine_direction_12_month_plot.set_label_text(str(routine_direction_12_month))
        self.routine_improvement_dir_12_month_plot.set_label_text(str(routine_improvement_dir_12_month))

        self.routine_ratio_target_plot.set_label_text(
                str(int(self.routine_aim_plot.target_data['value'][0] * 100.0)) + '%')

        # Data driven label styles
        if routine_variance_3_month < 0:
            self.routine_direction_3_month_plot.set_label_style("table-data-direction-down")
        else:
            self.routine_direction_3_month_plot.set_label_style("table-data-direction-up")

        if routine_improvement_3_month < 0:
            self.routine_improvement_dir_3_month_plot.set_label_style("table-data-direction-down")
        else:
            self.routine_improvement_dir_3_month_plot.set_label_style("table-data-direction-up")

        if routine_variance_6_month < 0:
            self.routine_direction_6_month_plot.set_label_style("table-data-direction-down")
        else:
            self.routine_direction_6_month_plot.set_label_style("table-data-direction-up")

        if routine_improvement_6_month < 0:
            self.routine_improvement_dir_6_month_plot.set_label_style("table-data-direction-down")
        else:
            self.routine_improvement_dir_6_month_plot.set_label_style("table-data-direction-up")

        if routine_variance_12_month < 0:
            self.routine_direction_12_month_plot.set_label_style("table-data-direction-down")
        else:
            self.routine_direction_12_month_plot.set_label_style("table-data-direction-up")

        if routine_improvement_12_month < 0:
            self.routine_improvement_dir_12_month_plot.set_label_style("table-data-direction-down")
        else:
            self.routine_improvement_dir_12_month_plot.set_label_style("table-data-direction-up")
    # END add_routine_referral_process_aim

    def update_routine_referral_process_aim(self, month: datetime):
        self.routine_aim_plot.load_clinic_data(month, self.clinic)
        self.routine_aim_plot.create_plot_data()

        # Updated process aim values
        routine_ratio_3_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'MOV91 Pct Routine Referrals Seen in 30d')))
        routine_variance_3_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var Target MOV91 Pct Routine Referrals Seen in 30d')))
        routine_direction_3_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var Target MOV91 Pct Routine Referrals Seen in 30d'))

        routine_improvement_3_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var MOV91 Pct Routine Referrals Seen in 30d')))

        routine_improvement_dir_3_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var MOV91 Pct Routine Referrals Seen in 30d'))

        routine_ratio_6_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'MOV182 Pct Routine Referrals Seen in 30d')))
        routine_variance_6_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var Target MOV182 Pct Routine Referrals Seen in 30d')))
        routine_direction_6_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var Target MOV182 Pct Routine Referrals Seen in 30d'))
        routine_improvement_6_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var MOV182 Pct Routine Referrals Seen in 30d')))
        routine_improvement_dir_6_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var MOV182 Pct Routine Referrals Seen in 30d'))

        routine_ratio_12_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'MOV364 Pct Routine Referrals Seen in 30d')))
        routine_variance_12_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var Target MOV364 Pct Routine Referrals Seen in 30d')))
        routine_direction_12_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var Target MOV364 Pct Routine Referrals Seen in 30d'))
        routine_improvement_12_month = (
            v.half_up_int(wt.get_clinic_rate_measure(month,
                                                     self.clinic,
                                                     'Var MOV364 Pct Routine Referrals Seen in 30d')))
        routine_improvement_dir_12_month = (
            wt.get_clinic_measure(month,
                                  self.clinic,
                                  'Dir Var MOV364 Pct Routine Referrals Seen in 30d'))

        # Data driven labels
        self.routine_ratio_3_month_plot.set_label_text(str(routine_ratio_3_month) + '%')
        self.routine_variance_3_month_plot.set_label_text(str(routine_variance_3_month) + '%')
        self.routine_direction_3_month_plot.set_label_text(str(routine_direction_3_month))
        self.routine_improvement_dir_3_month_plot.set_label_text(str(routine_improvement_dir_3_month))

        self.routine_ratio_6_month_plot.set_label_text(str(routine_ratio_6_month) + '%')
        self.routine_variance_6_month_plot.set_label_text(str(routine_variance_6_month) + '%')
        self.routine_direction_6_month_plot.set_label_text(str(routine_direction_6_month))
        self.routine_improvement_dir_6_month_plot.set_label_text(str(routine_improvement_dir_6_month))

        self.routine_ratio_12_month_plot.set_label_text(str(routine_ratio_12_month) + '%')
        self.routine_variance_12_month_plot.set_label_text(str(routine_variance_12_month) + '%')
        self.routine_direction_12_month_plot.set_label_text(str(routine_direction_12_month))
        self.routine_improvement_dir_12_month_plot.set_label_text(str(routine_improvement_dir_12_month))

        self.routine_ratio_target_plot.set_label_text(
                str(int(self.routine_aim_plot.target_data['value'][0] * 100.0)) + '%')

        # Data driven label styles
        if routine_variance_3_month < 0:
            self.routine_direction_3_month_plot.set_label_style("table-data-direction-down")
        else:
            self.routine_direction_3_month_plot.set_label_style("table-data-direction-up")

        if routine_improvement_3_month < 0:
            self.routine_improvement_dir_3_month_plot.set_label_style("table-data-direction-down")
        else:
            self.routine_improvement_dir_3_month_plot.set_label_style("table-data-direction-up")

        if routine_variance_6_month < 0:
            self.routine_direction_6_month_plot.set_label_style("table-data-direction-down")
        else:
            self.routine_direction_6_month_plot.set_label_style("table-data-direction-up")

        if routine_improvement_6_month < 0:
            self.routine_improvement_dir_6_month_plot.set_label_style("table-data-direction-down")
        else:
            self.routine_improvement_dir_6_month_plot.set_label_style("table-data-direction-up")

        if routine_variance_12_month < 0:
            self.routine_direction_12_month_plot.set_label_style("table-data-direction-down")
        else:
            self.routine_direction_12_month_plot.set_label_style("table-data-direction-up")

        if routine_improvement_12_month < 0:
            self.routine_improvement_dir_12_month_plot.set_label_style("table-data-direction-down")
        else:
            self.routine_improvement_dir_12_month_plot.set_label_style("table-data-direction-up")
    # END update_routine_referral_process_aim

    def add_referral_process_measures(self, month: datetime):

        # Data to calculate volume measures after 5 days
        self.seen_histogram_plot.load_clinic_data(month, self.clinic)
        self.seen_histogram_plot.create_plot_data()
        self.seen_histogram_plot.add_plot()

        # Data for processing volume measures after 90 days
        volume_values = self.process_volume_plot.volume_data['value']

        # Processing rates
        if volume_values[0] > 0:
            ratio_accepted = volume_values[1] / volume_values[0]
            ratio_scheduled = volume_values[2] / volume_values[0]
            ratio_completed = volume_values[3] / volume_values[0]
        else:
            ratio_accepted = 0.0
            ratio_scheduled = 0.0
            ratio_completed = 0.0

        # Processing Time
        accepted_days = v.half_up_int(
            wt.get_clinic_rate_measure(wt.last_month, self.clinic, 'MOV28 Median Days to Accept'))
        scheduled_days = (
            v.half_up_int(wt.get_clinic_rate_measure(wt.last_month, self.clinic, 'MOV28 Median Days until Scheduled')))
        completed_days = (
            v.half_up_int(wt.get_clinic_rate_measure(wt.last_month, self.clinic, 'MOV28 Median Days until Completed')))
        seen_days = (
            v.half_up_int(wt.get_clinic_rate_measure(wt.last_month, self.clinic, 'MOV28 Median Days until Seen')))

        # Data driven labels
        self.all_accepted_rate_plot.set_label_text(str(v.half_up_int(ratio_accepted * 100.0)) + '%')
        self.all_scheduled_rate_plot.set_label_text(str(v.half_up_int(ratio_scheduled * 100.0)) + '%')
        self.all_completed_rate_plot.set_label_text(str(v.half_up_int(ratio_completed * 100.0)) + '%')
        self.median_days_to_accepted_plot.set_label_text(str(accepted_days))
        self.median_days_to_scheduled_plot.set_label_text(str(scheduled_days))
        self.median_days_to_completed_plot.set_label_text(str(completed_days))
        self.median_days_to_seen_plot.set_label_text(str(seen_days))
    # END add_all_referral_process_measures

    def update_referral_process_measures(self, month: datetime):
        # Data to calculate volume measures after 5 days
        self.seen_histogram_plot.load_clinic_data(month, self.clinic)
        self.seen_histogram_plot.create_plot_data()
        self.seen_histogram_plot.update_plot()

        # Data for processing volume measures after 90 days
        volume_values = self.process_volume_plot.volume_data['value']

        # Processing rates
        if volume_values[0] > 0:
            ratio_accepted = volume_values[1] / volume_values[0]
            ratio_scheduled = volume_values[2] / volume_values[0]
            ratio_completed = volume_values[3] / volume_values[0]
        else:
            ratio_accepted = 0.0
            ratio_scheduled = 0.0
            ratio_completed = 0.0

        # Processing Time
        accepted_days = v.half_up_int(
            wt.get_clinic_rate_measure(wt.last_month, self.clinic, 'MOV28 Median Days to Accept'))
        scheduled_days = (
            v.half_up_int(wt.get_clinic_rate_measure(wt.last_month, self.clinic, 'MOV28 Median Days until Scheduled')))
        completed_days = (
            v.half_up_int(wt.get_clinic_rate_measure(wt.last_month, self.clinic, 'MOV28 Median Days until Completed')))
        seen_days = (
            v.half_up_int(wt.get_clinic_rate_measure(wt.last_month, self.clinic, 'MOV28 Median Days until Seen')))

        # Data driven labels
        self.all_accepted_rate_plot.set_label_text(str(v.half_up_int(ratio_accepted * 100.0)) + '%')
        self.all_scheduled_rate_plot.set_label_text(str(v.half_up_int(ratio_scheduled * 100.0)) + '%')
        self.all_completed_rate_plot.set_label_text(str(v.half_up_int(ratio_completed * 100.0)) + '%')
        self.median_days_to_accepted_plot.set_label_text(str(accepted_days))
        self.median_days_to_scheduled_plot.set_label_text(str(scheduled_days))
        self.median_days_to_completed_plot.set_label_text(str(completed_days))
        self.median_days_to_seen_plot.set_label_text(str(seen_days))
    # END update_referral_process_measures

    def set_clinic(self, clinic: str) -> None:
        self.clinic = clinic

    def clinic_selection_handler(self, attr: str, old, new) -> None:
        self.set_clinic(new)
        self.update_seen_ratio_plots(wt.last_month)
        self.update_referral_volume_plots(wt.last_month)
        self.update_urgent_referral_process_aim(wt.last_month)
        self.update_routine_referral_process_aim(wt.last_month)
        self.update_referral_process_measures(wt.last_month)
        self.label_data_source.update_plot_data()
    # END clinic_selection_handler

    def insert_clinic_process_data(self) -> None:
        # Bokeh application handler to modify a blank document that will be served from a Bokeh
        # server application.  This application will be invoked by the script that is injected into the HTML
        # in the response by Jinja2 when the template is rendered. The Bokeh client script opens
        # a websocket to the Bokeh server application to obtain the contents to render in the browser.  This
        # handler adds content to be rendered into the application document.

        # Grab the clinic name from the HTTP request
        clinic = v.get_clinic_from_request(self.document)
        if len(clinic) > 0:
            self.clinic = clinic

        self.add_referral_volume_plots(wt.last_month)
        self.add_seen_ratio_plots(wt.last_month)
        self.add_urgent_referral_process_aim(wt.last_month)
        self.add_routine_referral_process_aim(wt.last_month)
        self.add_referral_process_measures(wt.last_month)
        v.add_clinic_slicer(self.document, wt.last_month, self.clinic, self.clinic_selection_handler)
        self.label_data_source.update_plot_data()
        self.label_data_source.add_plot()

        # The Bokeh application handlers pass this text through to the HTML page title
        self.document.title = self.get_app_title()

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
        self.document.template_variables['report_month'] = wt.last_month.strftime("%B %Y")
    # END insert_clinic_process_data
# END CLASS ClinicProcessApp


def clinic_process_app_handler(doc: Document) -> None:
    process_app = ClinicProcessApp(doc)
    process_app.insert_clinic_process_data()
# END clinic_process_app_handler
