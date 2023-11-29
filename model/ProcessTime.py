"""
ProcessTime.py
Provides data for process aim performance and process timing for conversion of referrals into attended appointments
https://907sjl.github.io/

Top-Level Variables:
    last_month - The first day of the previous month at time 00:00:00
    clinic_measures[month] - Calculated measurement data by month by clinic
    distribution_data[month] - Calculated counts by category by month and clinic

Functions:
    get_overall_measure - Returns a measure value for the given month across all clinics regardless of datatype
    get_overall_rate_measure - Returns a float measure value for the given month across all clinics
    get_overall_count_measure - Returns an integer measure value for the given month across all clinics
    get_clinic_measure - Returns a measure value for the given clinic and month regardless of datatype
    get_clinic_rate_measure - Returns a float measure value for the given clinic and month
    get_clinic_count_measure - Returns an integer measure value for the given clinic and month
    get_clinics - Returns a list of unique clinic names
    get_clinic_distribution_count - Returns the distribution count for a clinic, category, and bin name combination
"""

import pandas as pd
from pandas import DataFrame
import numpy as np

from datetime import datetime
from dateutil.relativedelta import relativedelta

import model.source.Referrals as r


# Effective as-of date for data
_AS_OF_DATE = datetime(2023, 3, 1)

# Configurations to auto-calculate measures dependent on other measures
_DEPENDENT_VARIANCES = [
    {'measure': 'Var MOV91 Pct Routine Referrals Seen in 30d',
     'value': 'MOV28 Pct Routine Referrals Seen in 30d',
     'standard': 'MOV91 Pct Routine Referrals Seen in 30d',
     'is-percent': True},
    {'measure': 'Var MOV182 Pct Routine Referrals Seen in 30d',
     'value': 'MOV91 Pct Routine Referrals Seen in 30d',
     'standard': 'MOV182 Pct Routine Referrals Seen in 30d',
     'is-percent': True},
    {'measure': 'Var MOV364 Pct Routine Referrals Seen in 30d',
     'value': 'MOV182 Pct Routine Referrals Seen in 30d',
     'standard': 'MOV364 Pct Routine Referrals Seen in 30d',
     'is-percent': True},
    {'measure': 'Var Target Pct Routine Referrals Seen in 30d',
     'value': 'Pct Routine Referrals Seen in 30d',
     'standard': 'Target Pct Routine Referrals Seen in 30d',
     'is-percent': True},
    {'measure': 'Var Target MOV91 Pct Routine Referrals Seen in 30d',
     'value': 'MOV91 Pct Routine Referrals Seen in 30d',
     'standard': 'Target Pct Routine Referrals Seen in 30d',
     'is-percent': True},
    {'measure': 'Var Target MOV182 Pct Routine Referrals Seen in 30d',
     'value': 'MOV182 Pct Routine Referrals Seen in 30d',
     'standard': 'Target Pct Routine Referrals Seen in 30d',
     'is-percent': True},
    {'measure': 'Var Target MOV364 Pct Routine Referrals Seen in 30d',
     'value': 'MOV364 Pct Routine Referrals Seen in 30d',
     'standard': 'Target Pct Routine Referrals Seen in 30d',
     'is-percent': True},
    {'measure': 'Var MOV91 Pct Urgent Referrals Seen in 5d',
     'value': 'MOV28 Pct Urgent Referrals Seen in 5d',
     'standard': 'MOV91 Pct Urgent Referrals Seen in 5d',
     'is-percent': True},
    {'measure': 'Var MOV182 Pct Urgent Referrals Seen in 5d',
     'value': 'MOV91 Pct Urgent Referrals Seen in 5d',
     'standard': 'MOV182 Pct Urgent Referrals Seen in 5d',
     'is-percent': True},
    {'measure': 'Var MOV364 Pct Urgent Referrals Seen in 5d',
     'value': 'MOV182 Pct Urgent Referrals Seen in 5d',
     'standard': 'MOV364 Pct Urgent Referrals Seen in 5d',
     'is-percent': True},
    {'measure': 'Var Target Pct Urgent Referrals Seen in 5d',
     'value': 'Pct Urgent Referrals Seen in 5d',
     'standard': 'Target Pct Urgent Referrals Seen in 5d',
     'is-percent': True},
    {'measure': 'Var Target MOV91 Pct Urgent Referrals Seen in 5d',
     'value': 'MOV91 Pct Urgent Referrals Seen in 5d',
     'standard': 'Target Pct Urgent Referrals Seen in 5d',
     'is-percent': True},
    {'measure': 'Var Target MOV182 Pct Urgent Referrals Seen in 5d',
     'value': 'MOV182 Pct Urgent Referrals Seen in 5d',
     'standard': 'Target Pct Urgent Referrals Seen in 5d',
     'is-percent': True},
    {'measure': 'Var Target MOV364 Pct Urgent Referrals Seen in 5d',
     'value': 'MOV364 Pct Urgent Referrals Seen in 5d',
     'standard': 'Target Pct Urgent Referrals Seen in 5d',
     'is-percent': True},
    {'measure': 'Var MOV91 Median Days until Seen',
     'value': 'MOV28 Median Days until Seen',
     'standard': 'MOV91 Median Days until Seen',
     'is-percent': True},
    {'measure': 'Var MOV182 Median Days until Seen',
     'value': 'MOV91 Median Days until Seen',
     'standard': 'MOV182 Median Days until Seen',
     'is-percent': True},
    {'measure': 'Var MOV364 Median Days until Seen',
     'value': 'MOV182 Median Days until Seen',
     'standard': 'MOV364 Median Days until Seen',
     'is-percent': True},
    {'measure': 'Var MOV91 Median Days until Scheduled',
     'value': 'MOV28 Median Days until Scheduled',
     'standard': 'MOV91 Median Days until Scheduled',
     'is-percent': True},
    {'measure': 'Var MOV182 Median Days until Scheduled',
     'value': 'MOV91 Median Days until Scheduled',
     'standard': 'MOV182 Median Days until Scheduled',
     'is-percent': True},
    {'measure': 'Var MOV364 Median Days until Scheduled',
     'value': 'MOV182 Median Days until Scheduled',
     'standard': 'MOV364 Median Days until Scheduled',
     'is-percent': True}]

_VARIANCE_CATEGORIES = [
    {'category': 'Routine Performance vs. Target',
     'near-term': 'Var Target MOV91 Pct Routine Referrals Seen in 30d',
     'mid-term': 'Var Target MOV182 Pct Routine Referrals Seen in 30d',
     'long-term': 'Var Target MOV364 Pct Routine Referrals Seen in 30d',
     'rubric': {111: 'Consistent Performer',
                11: 'Rising Recovery',
                110: 'Performer',
                10: 'Setback Recovery',
                101: 'Bouncing Back',
                1: 'Turning Upward',
                100: 'Falling',
                0: 'Consistently Under'}},
    {'category': 'Routine Improvement Direction',
     'near-term': 'Var MOV91 Pct Routine Referrals Seen in 30d',
     'mid-term': 'Var MOV182 Pct Routine Referrals Seen in 30d',
     'long-term': 'Var MOV364 Pct Routine Referrals Seen in 30d',
     'rubric': {111: 'Rising',
                11: 'Rising Recovery',
                110: 'Rising',
                10: 'Setback Recovery',
                101: 'Bouncing Back',
                1: 'Turning Upward',
                100: 'Falling',
                0: 'Falling'}},
    {'category': 'Urgent Performance vs. Target',
     'near-term': 'Var Target MOV91 Pct Urgent Referrals Seen in 5d',
     'mid-term': 'Var Target MOV182 Pct Urgent Referrals Seen in 5d',
     'long-term': 'Var Target MOV364 Pct Urgent Referrals Seen in 5d',
     'rubric': {111: 'Consistent Performer',
                11: 'Rising Recovery',
                110: 'Performer',
                10: 'Setback Recovery',
                101: 'Bouncing Back',
                1: 'Turning Upward',
                100: 'Falling',
                0: 'Consistently Under'}},
    {'category': 'Urgent Improvement Direction',
     'near-term': 'Var MOV91 Pct Urgent Referrals Seen in 5d',
     'mid-term': 'Var MOV182 Pct Urgent Referrals Seen in 5d',
     'long-term': 'Var MOV364 Pct Urgent Referrals Seen in 5d',
     'rubric': {111: 'Rising',
                11: 'Rising Recovery',
                110: 'Rising',
                10: 'Setback Recovery',
                101: 'Bouncing Back',
                1: 'Turning Upward',
                100: 'Falling',
                0: 'Falling'}}]


# Memory resident storage for monthly process measurements
clinic_measures = {}
distribution_data = {}


def _calculate_measures_after_5_days(referrals_df: DataFrame,
                                     clinics_df: DataFrame,
                                     start_date: datetime,
                                     end_date: datetime,
                                     prefix: str = '') -> DataFrame:
    """
    Calculates measures of referral processing using a 5 day lookback.
    :param referrals_df: a dataframe of referrals
    :param clinics_df: a dataframe of clinic names to calculate measures for
    :param start_date: the first date in the period
    :param end_date: the day after the last date in the period
    :param prefix: prefix to add to the measure name
    :return: a dataframe of clinics and calculated measures
    """

    # Limit the source data to the given clinic names and the referrals that reached
    # 5 days of age in the given period.
    idx = (referrals_df['Clinic'].isin(clinics_df['Clinic'])
           & (referrals_df['Reporting Date 5 Day Lag'] >= start_date)
           & (referrals_df['Reporting Date 5 Day Lag'] < end_date))
    source_df = referrals_df.loc[idx].copy()

    # Create a dataframe of aggregations by clinic starting with independent measures
    # MEASURE: Count of urgent referrals sent after 5 days
    # MEASURE: Count of urgent referrals kept after 5 days
    by_clinic_df = source_df.loc[source_df['Referral Priority'] == 'Urgent'] \
        .groupby('Clinic') \
        .agg(rid=pd.NamedAgg(column="Referral ID", aggfunc="count"),
             aged=pd.NamedAgg(column="Referral Aged Yn", aggfunc="sum")) \
        .rename(columns={'rid': prefix + 'Urgent Referrals Sent',
                         'aged': prefix + 'Urgent Referrals Aged'})

    # MEASURE: Count of referrals rejected after 5 days
    idx = ((source_df['Referral Status'] == 'Rejected')
           & (source_df['Referral Sent Yn'] == 1)
           & (source_df['Referral Priority'] == 'Urgent'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Urgent Referrals Rejected After 5d'})

    # Merge count of referrals rejected into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals canceled after 5 days
    idx = ((source_df['Referral Status'] == 'Cancelled')
           & (source_df['Referral Sent Yn'] == 1)
           & (source_df['Referral Priority'] == 'Urgent'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Urgent Referrals Canceled After 5d'})

    # Merge count of referrals canceled into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals closed without being seen after 5 days
    idx = (~(source_df['Referral Status'] == 'Cancelled')
           & ~(source_df['Referral Status'] == 'Rejected')
           & (source_df['Referral Aged Yn'] == 0)
           & (source_df['Referral Sent Yn'] == 1)
           & (source_df['Referral Priority'] == 'Urgent'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Urgent Referrals Closed WBS After 5d'})

    # Merge count of referrals closed without being seen into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals seen after 5 days
    idx = ((source_df['Referral Seen or Checked In Yn'] == 1)
           & (source_df['Referral Aged Yn'] == 1)
           & (source_df['Referral Priority'] == 'Urgent'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Urgent Referrals Seen After 5d'})

    # Merge count of referrals seen into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals scheduled after 5 days
    idx = (((source_df['Patient Scheduled Yn'] + source_df['Appointment Linked Yn']) > 0)
           & (source_df['Referral Aged Yn'] == 1)
           & (source_df['Referral Priority'] == 'Urgent'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Urgent Referrals Scheduled After 5d'})

    # Merge count of referrals scheduled into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals scheduled and waiting to be seen after 5 days
    idx = ((source_df['Referral Seen or Checked In Yn'] == 0)
           & ((source_df['Patient Scheduled Yn'] + source_df['Appointment Linked Yn']) > 0)
           & (source_df['Referral Aged Yn'] == 1)
           & (source_df['Referral Priority'] == 'Urgent'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Urgent Referrals Waiting After 5d'})

    # Merge count of referrals waiting into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals not scheduled after 5 days
    idx = (((source_df['Patient Scheduled Yn'] + source_df['Appointment Linked Yn']) == 0)
           & (source_df['Referral Aged Yn'] == 1)
           & (source_df['Referral Priority'] == 'Urgent'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Urgent Referrals Not Scheduled After 5d'})

    # Merge count of referrals not scheduled into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of urgent referrals seen in 5 days by clinic
    idx = ((source_df['Days until Patient Seen or Check In'] <= 5.0)
           & (source_df['Referral Aged Yn'] == 1)
           & (source_df['Referral Priority'] == 'Urgent'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Urgent Referrals Seen in 5d'})

    # Merge count of referrals seen by 5 days into dataframe of measures by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # Create a single row dataframe to hold global measures across all clinics
    # using the *ALL* clinic name 
    global_df = clinics_df.loc[(clinics_df['Clinic'] == '*ALL*')].copy()

    # MEASURE: Count of urgent referrals seen within 5 days
    measure_df = source_df.loc[idx, ['Referral ID']] \
        .count().to_frame().transpose() \
        .rename(columns={'Referral ID': prefix + 'Urgent Referrals Seen in 5d'})
    measure_df['Clinic'] = '*ALL*'

    # Merge count of all referrals seen within 5 days into global ages dataframe 
    global_df = pd.merge(global_df, measure_df, how='inner', on=['Clinic'])

    # MEASURE: Count of urgent referrals kept after 5 days
    idx = ((source_df['Referral Aged Yn'] == 1)
           & (source_df['Referral Priority'] == 'Urgent'))
    measure_df = source_df.loc[idx, ['Referral ID']] \
        .count().to_frame().transpose() \
        .rename(columns={'Referral ID': prefix + 'Urgent Referrals Aged'})
    measure_df['Clinic'] = '*ALL*'

    # Merge count of all referrals kept after 5 days into global measures dataframe
    global_df = pd.merge(global_df, measure_df, how='inner', on=['Clinic'])

    # Merge global measures into a seamless table of measures by clinic using the *ALL* clinic
    by_clinic_df = pd.merge(by_clinic_df, global_df, how='outer',
                            on=['Clinic', prefix + 'Urgent Referrals Aged', prefix + 'Urgent Referrals Seen in 5d'])

    # Clean up missing data from clinics by replacing with zero
    by_clinic_df = by_clinic_df.fillna(0)

    # Calculate dependent measures using table of measures by clinic
    # MEASURE: Percent of urgent referrals seen after 5 days
    by_clinic_df[prefix + 'Pct Urgent Referrals Seen in 5d'] = (
        ((by_clinic_df[prefix + 'Urgent Referrals Seen in 5d']
          .div(by_clinic_df[prefix + 'Urgent Referrals Aged'])
          .fillna(0) * 100.0) + 0.5)
        .astype(int))

    return by_clinic_df
# END calculate_measures_after_5_days


def _calculate_distributions_after_90_days(referrals_df: DataFrame,
                                           clinics_df: DataFrame,
                                           start_date: datetime,
                                           end_date: datetime) -> DataFrame:
    """
    Calculates measures of referral processing using a 90 day lookback.
    :param referrals_df: a dataframe of referrals
    :param clinics_df: a dataframe of clinic names to calculate measures for
    :param start_date: the first date in the period
    :param end_date: the day after the last date in the period
    :return: a dataframe of clinics and calculated measures,
             a dataframe of referral counts by priority and age category
    """

    # Limit the source data to the given clinic names and the referrals that reached
    # 90 days of age in the given period.
    idx = (referrals_df['Clinic'].isin(clinics_df['Clinic'])
           & (referrals_df['Reporting Date 90 Day Lag'] >= start_date)
           & (referrals_df['Reporting Date 90 Day Lag'] < end_date))
    source_df = referrals_df.loc[idx].copy()

    # Categorize the days to seen for referrals after 90 days
    r.calculate_age_category(source_df, 'Age Category to Seen', 'Days until Patient Seen or Check In')

    # Create a data set of referral counts by priority and age category to seen
    distribution_df = source_df.groupby(['Clinic', 'Referral Priority', 'Age Category to Seen']) \
        .agg({'Referral Aged Yn': 'sum'}) \
        .rename(columns={'Referral Aged Yn': 'Referrals Aged'}) \
        .reset_index()

    return distribution_df
# END calculate_distributions_after_90_days


def _calculate_measures_after_90_days(referrals_df: DataFrame,
                                      clinics_df: DataFrame,
                                      start_date: datetime,
                                      end_date: datetime,
                                      prefix: str = '') -> DataFrame:
    """
    Calculates measures of referral processing using a 90 day lookback.
    :param referrals_df: a dataframe of referrals
    :param clinics_df: a dataframe of clinic names to calculate measures for
    :param start_date: the first date in the period
    :param end_date: the day after the last date in the period
    :param prefix: prefix to add to the measure name
    :return: a dataframe of clinics and calculated measures,
             a dataframe of referral counts by priority and age category
    """

    # Limit the source data to the given clinic names and the referrals that reached
    # 90 days of age in the given period.
    idx = (referrals_df['Clinic'].isin(clinics_df['Clinic'])
           & (referrals_df['Reporting Date 90 Day Lag'] >= start_date)
           & (referrals_df['Reporting Date 90 Day Lag'] < end_date))
    source_df = referrals_df.loc[idx].copy()

    # Create a dataframe of aggregations by clinic starting with independent measures
    # MEASURE: Count of referrals sent after 90 days
    # MEASURE: Count of referrals kept after 90 days
    by_clinic_df = source_df \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count', 'Referral Aged Yn': 'sum'}) \
        .rename(columns={'Referral ID': prefix + 'Referrals Sent', 'Referral Aged Yn': prefix + 'Referrals Aged'})

    # MEASURE: Count of referrals rejected after 90 days
    idx = ((source_df['Referral Status'] == 'Rejected')
           & (source_df['Referral Sent Yn'] == 1))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Referrals Rejected After 90d'})

    # Merge count of referrals rejected into count of all referrals by clinic 
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals canceled after 90 days
    idx = ((source_df['Referral Status'] == 'Cancelled')
           & (source_df['Referral Sent Yn'] == 1))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Referrals Canceled After 90d'})

    # Merge count of referrals canceled into count of all referrals by clinic 
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals closed without being seen after 90 days
    idx = (~(source_df['Referral Status'] == 'Cancelled')
           & ~(source_df['Referral Status'] == 'Rejected')
           & (source_df['Referral Aged Yn'] == 0)
           & (source_df['Referral Sent Yn'] == 1))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Referrals Closed WBS After 90d'})

    # Merge count of referrals closed without being seen into count of all referrals by clinic 
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals seen after 90 days
    idx = ((source_df['Referral Seen or Checked In Yn'] == 1)
           & (source_df['Referral Aged Yn'] == 1))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Referrals Seen After 90d'})

    # Merge count of referrals seen into count of all referrals by clinic 
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals scheduled after 90 days
    idx = (((source_df['Patient Scheduled Yn'] + source_df['Appointment Linked Yn']) > 0)
           & (source_df['Referral Aged Yn'] == 1))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Referrals Scheduled After 90d'})

    # Merge count of referrals scheduled into count of all referrals by clinic 
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals scheduled and waiting to be seen after 90 days
    idx = ((source_df['Referral Seen or Checked In Yn'] == 0)
           & ((source_df['Patient Scheduled Yn'] + source_df['Appointment Linked Yn']) > 0)
           & (source_df['Referral Aged Yn'] == 1))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Referrals Waiting After 90d'})

    # Merge count of referrals waiting into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals not scheduled after 90 days
    idx = (((source_df['Patient Scheduled Yn'] + source_df['Appointment Linked Yn']) == 0)
           & (source_df['Referral Aged Yn'] == 1))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Referrals Not Scheduled After 90d'})

    # Merge count of referrals not scheduled into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals accepted after 90 days
    idx = ((source_df['Referral Accepted Yn'] > 0)
           & (source_df['Referral Aged Yn'] == 1))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Referrals Accepted After 90d'})

    # Merge count of referrals accepted into count of all referrals by clinic 
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals completed after 90 days
    idx = ((source_df['Referral Completed Yn'] == 1)
           & (source_df['Referral Aged Yn'] == 1))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Referrals Completed After 90d'})

    # Merge count of referrals completed into count of all referrals by clinic 
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals seen and completed after 90 days
    idx = ((source_df['Referral Completed Yn'] == 1)
           & (source_df['Referral Seen or Checked In Yn'] == 1)
           & (source_df['Referral Aged Yn'] == 1))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Referrals Completed and Seen After 90d'})

    # Merge count of referrals seen and completed into count of all referrals by clinic 
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Median days to see referral
    # MEASURE: Median days to schedule referral
    # MEASURE: Median days to accept referral
    # MEASURE: Median days to complete referral
    measure_df = source_df.loc[(source_df['Referral Aged Yn'] == 1)] \
        .groupby('Clinic') \
        .agg({'Days until Patient Seen or Check In': 'median',
              'Days until Referral or Patient Scheduled': 'median',
              'Days until Referral Completed': 'median',
              'Days until Referral Accepted': 'median'}) \
        .rename(columns={'Days until Patient Seen or Check In': prefix + 'Median Days until Seen',
                         'Days until Referral or Patient Scheduled': prefix + 'Median Days until Scheduled',
                         'Days until Referral Completed': prefix + 'Median Days until Completed',
                         'Days until Referral Accepted': prefix + 'Median Days to Accept'})

    # Merge ages into count of all referrals by clinic 
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # Create a single row dataframe to hold measures across all clinics
    # using the placeholder clinic name *ALL*
    global_df = clinics_df.loc[(clinics_df['Clinic'] == '*ALL*')].copy()

    # MEASURE: Median days to see all referrals
    # Calculate the global median age to see all referrals using *ALL* clinic
    measure_df = source_df.loc[(source_df['Referral Aged Yn'] == 1), ['Days until Patient Seen or Check In']] \
        .median().to_frame().transpose().rename(
        columns={'Days until Patient Seen or Check In': prefix + 'Median Days until Seen'})
    measure_df['Clinic'] = '*ALL*'

    # Merge median age to see into a single view of global ages 
    global_df = pd.merge(global_df, measure_df, how='inner', on=['Clinic'])

    # MEASURE: Median days to schedule all referrals
    measure_df = source_df.loc[(source_df['Referral Aged Yn'] == 1), ['Days until Referral or Patient Scheduled']] \
        .median().to_frame().transpose().rename(
        columns={'Days until Referral or Patient Scheduled': prefix + 'Median Days until Scheduled'})
    measure_df['Clinic'] = '*ALL*'

    # Merge median age to schedule into a single view of global ages 
    global_df = pd.merge(global_df, measure_df, how='inner', on=['Clinic'])

    # Merge global measures into a seamless table of measures by clinic using the *ALL*
    # placeholder clinic name
    by_clinic_df = pd.merge(by_clinic_df, global_df, how='outer',
                            on=['Clinic', prefix + 'Median Days until Scheduled', prefix + 'Median Days until Seen'])

    # Clean up missing data from clinics without counts 
    by_clinic_df = by_clinic_df.fillna(0)

    # Calculate the dependent measures using the table of measures by clinic
    # MEASURE: Percent of referrals seen after 90 days
    by_clinic_df[prefix + 'Pct Referrals Seen After 90d'] = (
        ((by_clinic_df[prefix + 'Referrals Seen After 90d']
          .div(by_clinic_df[prefix + 'Referrals Aged'])
          .fillna(0) * 100.0) + 0.5)
        .astype(int))

    # MEASURE: Percent of referrals scheduled after 90 days
    # Calculate rate of referrals scheduled by clinic
    by_clinic_df[prefix + 'Pct Referrals Scheduled After 90d'] = (
        ((by_clinic_df[prefix + 'Referrals Scheduled After 90d']
          .div(by_clinic_df[prefix + 'Referrals Aged'])
          .fillna(0) * 100.0) + 0.5)
        .astype(int))

    return by_clinic_df
# END calculate_measures_after_90_days


def _calculate_measures_after_30_days(referrals_df: DataFrame,
                                      clinics_df: DataFrame,
                                      start_date: datetime,
                                      end_date: datetime,
                                      prefix: str = '') -> DataFrame:
    """
    Calculates measures of referral processing using a 30 day lookback.
    :param referrals_df: a dataframe of referrals
    :param clinics_df: a dataframe of clinic names to calculate measures for
    :param start_date: the first date in the period
    :param end_date: the day after the last date in the period
    :param prefix: prefix to add to the measure name
    :return: a dataframe of clinics and calculated measures
    """

    # Limit the source data to the given clinic names and the referrals that reached
    # 30 days of age in the given period.
    idx = (referrals_df['Clinic'].isin(clinics_df['Clinic'])
           & (referrals_df['Reporting Date 30 Day Lag'] >= start_date)
           & (referrals_df['Reporting Date 30 Day Lag'] < end_date))
    source_df = referrals_df.loc[idx].copy()

    # Create a dataframe of aggregations by clinic starting with independent measures
    # MEASURE: Count of routine referrals sent after 30 days 
    # MEASURE: Count of routine referrals kept after 30 days 
    by_clinic_df = source_df.loc[source_df['Referral Priority'] == 'Routine'] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count', 'Referral Aged Yn': 'sum'}) \
        .rename(columns={'Referral ID': prefix + 'Routine Referrals Sent',
                         'Referral Aged Yn': prefix + 'Routine Referrals Aged'})

    # MEASURE: Count of referrals rejected after 30 days
    idx = ((source_df['Referral Status'] == 'Rejected')
           & (source_df['Referral Sent Yn'] == 1)
           & (source_df['Referral Priority'] == 'Routine'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Routine Referrals Rejected After 30d'})

    # Merge count of referrals rejected into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals canceled after 30 days
    idx = ((source_df['Referral Status'] == 'Cancelled')
           & (source_df['Referral Sent Yn'] == 1)
           & (source_df['Referral Priority'] == 'Routine'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Routine Referrals Canceled After 30d'})

    # Merge count of referrals canceled into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals closed without being seen after 30 days
    idx = (~(source_df['Referral Status'] == 'Cancelled')
           & ~(source_df['Referral Status'] == 'Rejected')
           & (source_df['Referral Aged Yn'] == 0)
           & (source_df['Referral Sent Yn'] == 1)
           & (source_df['Referral Priority'] == 'Routine'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Routine Referrals Closed WBS After 30d'})

    # Merge count of referrals closed without being seen into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals seen after 30 days
    idx = ((source_df['Referral Seen or Checked In Yn'] == 1)
           & (source_df['Referral Aged Yn'] == 1)
           & (source_df['Referral Priority'] == 'Routine'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Routine Referrals Seen After 30d'})

    # Merge count of referrals seen into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals scheduled after 30 days
    idx = (((source_df['Patient Scheduled Yn'] + source_df['Appointment Linked Yn']) > 0)
           & (source_df['Referral Aged Yn'] == 1)
           & (source_df['Referral Priority'] == 'Routine'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Routine Referrals Scheduled After 30d'})

    # Merge count of referrals scheduled into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals scheduled and waiting to be seen after 30 days
    idx = ((source_df['Referral Seen or Checked In Yn'] == 0)
           & ((source_df['Patient Scheduled Yn'] + source_df['Appointment Linked Yn']) > 0)
           & (source_df['Referral Aged Yn'] == 1)
           & (source_df['Referral Priority'] == 'Routine'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Routine Referrals Waiting After 30d'})

    # Merge count of referrals waiting into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals not scheduled after 30 days
    idx = (((source_df['Patient Scheduled Yn'] + source_df['Appointment Linked Yn']) == 0)
           & (source_df['Referral Aged Yn'] == 1)
           & (source_df['Referral Priority'] == 'Routine'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Routine Referrals Not Scheduled After 30d'})

    # Merge count of referrals not scheduled into count of all referrals by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # MEASURE: Count of routine referrals seen within 30 days by clinic
    idx = ((source_df['Days until Patient Seen or Check In'] <= 30.0)
           & (source_df['Referral Aged Yn'] == 1)
           & (source_df['Referral Priority'] == 'Routine'))
    measure_df = source_df.loc[idx] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': prefix + 'Routine Referrals Seen in 30d'})

    # Merge count of referrals seen by 30 days into dataframe by clinic
    by_clinic_df = pd.merge(by_clinic_df, measure_df, how='left', on=['Clinic'])

    # Create a single row dataframe to hold global ages across all referrals 
    # using the *ALL* clinic name 
    global_df = clinics_df.loc[(clinics_df['Clinic'] == '*ALL*')].copy()

    # MEASURE: Count of routine referrals seen within 30 days across all clinics
    measure_df = source_df.loc[idx, ['Referral ID']] \
        .count().to_frame().transpose() \
        .rename(columns={'Referral ID': prefix + 'Routine Referrals Seen in 30d'})
    measure_df['Clinic'] = '*ALL*'

    # Merge count of referrals seen within 30 days into dataframe of global measures
    global_df = pd.merge(global_df, measure_df, how='inner', on=['Clinic'])

    # MEASURE: Count of routine referrals kept after 30 days across all clinics
    idx = ((source_df['Referral Aged Yn'] == 1)
           & (source_df['Referral Priority'] == 'Routine'))
    measure_df = source_df.loc[idx, ['Referral ID']] \
        .count().to_frame().transpose() \
        .rename(columns={'Referral ID': prefix + 'Routine Referrals Aged'})
    measure_df['Clinic'] = '*ALL*'

    # Merge count of referrals kept after 30 days into dataframe of global measures
    global_df = pd.merge(global_df, measure_df, how='inner', on=['Clinic'])

    # Merge global measures with measures by clinic into one seamless table using the *ALL* clinic
    by_clinic_df = pd.merge(by_clinic_df, global_df, how='outer',
                            on=['Clinic', prefix + 'Routine Referrals Aged', prefix + 'Routine Referrals Seen in 30d'])

    # Clean up missing data from clinics by replacing with zero
    by_clinic_df = by_clinic_df.fillna(0)

    # Calculate dependent measures using from table of measures by clinic
    # MEASURE: Percent of referrals seen in 30 days by clinic and overall
    by_clinic_df[prefix + 'Pct Routine Referrals Seen in 30d'] = (
        by_clinic_df[prefix + 'Routine Referrals Seen in 30d']
        .div(by_clinic_df[prefix + 'Routine Referrals Aged']) * 100.0)

    return by_clinic_df
# END calculate_measures_after_30_days


def _calculate_process_measures_for_month(referral_df: DataFrame,
                                          report_month: datetime) -> (DataFrame, DataFrame):
    """
    Returns the wait time data for one reporting month.  A reporting month includes
    measure data that looks back the appropriate amount of time for each measure.
    :param referral_df: a dataframe of referrals
    :param report_month: the first day of the month to return measures for @(00:00:00)
    :return: a dataframe of process measures for the month,
             a dataframe of referral distributions by days to seen
    """

    next_month = report_month + relativedelta(months=1)
    moving_28_day_start = next_month + relativedelta(days=-28)
    moving_91_day_start = next_month + relativedelta(days=-91)
    moving_182_day_start = next_month + relativedelta(days=-182)
    moving_364_day_start = next_month + relativedelta(days=-364)

    # Create master list of clinics to calculate measures for, and add a placeholder clinic name for measures
    # across all clinics
    process_measures_df = pd.DataFrame({'Clinic': np.sort(referral_df['Clinic'].unique())})
    process_measures_df = (
        pd.concat([pd.DataFrame({'Clinic': '*ALL*'}, index=[0]), process_measures_df]).reset_index(drop=True))

    # Calculate measures of referral processing that use different lookback periods of time
    after_5d_df = _calculate_measures_after_5_days(referral_df, process_measures_df, report_month, next_month)
    after_5d_m28_df = _calculate_measures_after_5_days(referral_df,
                                                       process_measures_df,
                                                       moving_28_day_start,
                                                       next_month,
                                                       'MOV28 ')
    after_5d_m91_df = _calculate_measures_after_5_days(referral_df,
                                                       process_measures_df,
                                                       moving_91_day_start,
                                                       next_month,
                                                       'MOV91 ')
    after_5d_m182_df = _calculate_measures_after_5_days(referral_df,
                                                        process_measures_df,
                                                        moving_182_day_start,
                                                        next_month,
                                                        'MOV182 ')
    after_5d_m364_df = _calculate_measures_after_5_days(referral_df,
                                                        process_measures_df,
                                                        moving_364_day_start,
                                                        next_month,
                                                        'MOV364 ')
    after_30d_df = _calculate_measures_after_30_days(referral_df, process_measures_df, report_month, next_month)
    after_30d_m28_df = _calculate_measures_after_30_days(referral_df,
                                                         process_measures_df,
                                                         moving_28_day_start,
                                                         next_month,
                                                         'MOV28 ')
    after_30d_m91_df = _calculate_measures_after_30_days(referral_df,
                                                         process_measures_df,
                                                         moving_91_day_start,
                                                         next_month,
                                                         'MOV91 ')
    after_30d_m182_df = _calculate_measures_after_30_days(referral_df,
                                                          process_measures_df,
                                                          moving_182_day_start,
                                                          next_month,
                                                          'MOV182 ')
    after_30d_m364_df = _calculate_measures_after_30_days(referral_df,
                                                          process_measures_df,
                                                          moving_364_day_start,
                                                          next_month,
                                                          'MOV364 ')
    after_90d_df = (
        _calculate_measures_after_90_days(referral_df, process_measures_df, report_month, next_month))
    after_90d_m28_df = _calculate_measures_after_90_days(referral_df,
                                                         process_measures_df,
                                                         moving_28_day_start,
                                                         next_month,
                                                         'MOV28 ')
    after_90d_m91_df = _calculate_measures_after_90_days(referral_df,
                                                         process_measures_df,
                                                         moving_91_day_start,
                                                         next_month,
                                                         'MOV91 ')
    after_90d_m182_df = _calculate_measures_after_90_days(referral_df,
                                                          process_measures_df,
                                                          moving_182_day_start,
                                                          next_month,
                                                          'MOV182 ')
    after_90d_m364_df = _calculate_measures_after_90_days(referral_df,
                                                          process_measures_df,
                                                          moving_364_day_start,
                                                          next_month,
                                                          'MOV364 ')
    after_90d_distribution_df = (
        _calculate_distributions_after_90_days(referral_df, process_measures_df, report_month, next_month))

    # Create one data set of referral performance measures by clinic
    process_measures_df = pd.merge(process_measures_df, after_5d_df, how='left', on=['Clinic'])
    process_measures_df = pd.merge(process_measures_df, after_5d_m28_df, how='left', on=['Clinic'])
    process_measures_df = pd.merge(process_measures_df, after_5d_m91_df, how='left', on=['Clinic'])
    process_measures_df = pd.merge(process_measures_df, after_5d_m182_df, how='left', on=['Clinic'])
    process_measures_df = pd.merge(process_measures_df, after_5d_m364_df, how='left', on=['Clinic'])
    process_measures_df = pd.merge(process_measures_df, after_30d_df, how='left', on=['Clinic'])
    process_measures_df = pd.merge(process_measures_df, after_30d_m28_df, how='left', on=['Clinic'])
    process_measures_df = pd.merge(process_measures_df, after_30d_m91_df, how='left', on=['Clinic'])
    process_measures_df = pd.merge(process_measures_df, after_30d_m182_df, how='left', on=['Clinic'])
    process_measures_df = pd.merge(process_measures_df, after_30d_m364_df, how='left', on=['Clinic'])
    process_measures_df = pd.merge(process_measures_df, after_90d_df, how='left', on=['Clinic'])
    process_measures_df = pd.merge(process_measures_df, after_90d_m28_df, how='left', on=['Clinic'])
    process_measures_df = pd.merge(process_measures_df, after_90d_m91_df, how='left', on=['Clinic'])
    process_measures_df = pd.merge(process_measures_df, after_90d_m182_df, how='left', on=['Clinic'])
    process_measures_df = pd.merge(process_measures_df, after_90d_m364_df, how='left', on=['Clinic'])

    # Clean up missing data from clinics by replacing with zero 
    process_measures_df = process_measures_df.fillna(0)

    # Tag the calculated ages to schedule with a category name 
    r.calculate_age_category(process_measures_df, 'Age Category to Scheduled', 'Median Days until Scheduled')

    # Tag the calculated ages to seen with a category name 
    r.calculate_age_category(process_measures_df, 'Age Category to Seen', 'Median Days until Seen')

    return process_measures_df, after_90d_distribution_df
# End calculate_process_measures_for_month


def get_overall_measure(report_month: datetime, measure: str) -> object:
    """Returns the value of the given measure for the given month across all clinics regardless of datatype."""
    return get_clinic_measure(report_month, '*ALL*', measure)
# END get_overall_measure


def get_overall_rate_measure(report_month: datetime, measure: str) -> float:
    """Returns a floating point value for the given measure for the given month across all clinics."""
    return get_clinic_rate_measure(report_month, '*ALL*', measure)
# END get_overall_rate_measure


def get_overall_count_measure(report_month: datetime, measure: str) -> int:
    """Returns an integer count value for the given measure for the given month across all clinics."""
    return get_clinic_count_measure(report_month, '*ALL*', measure)
# END get_overall_count_measure


def get_clinic_measure(report_month: datetime, clinic: str, measure: str) -> object:
    """Returns the value of the given measure for the given month for a given clinic regardless of datatype."""
    df = clinic_measures[report_month]
    view = df.loc[(df['Clinic'] == clinic)]
    if view.empty:
        return 0
    else:
        return view.at[min(view.index), measure]
# END get_clinic_measure


def get_clinic_rate_measure(report_month: datetime, clinic: str, measure: str, month_offset: int = 0) -> float:
    """
    Returns a measured value as a float for the given month offset by the given
    number of offset months.
    :param report_month: month being measured
    :param month_offset: number of months prior or after the month being measured
    :param clinic: name of clinic to return the measurement for
    :param measure: name of the measure to return
    :return: the measure value as a float, or 0.0 if measure is not numeric
    """
    offset_month = report_month + relativedelta(months=month_offset)
    df = clinic_measures[offset_month]
    if measure in df.select_dtypes(include=['int64', 'int32', 'float64']).columns:
        view = df.loc[(df['Clinic'] == clinic)]
        if view.empty:
            return 0.0
        else:
            return float(view.at[min(view.index), measure])
# END get_clinic_rate_measure


def get_clinic_count_measure(report_month: datetime, clinic: str, measure: str, month_offset: int = 0) -> int:
    """
    Returns a measured value as an int for the given month offset by the given
    number of offset months.
    :param report_month: month being measured
    :param month_offset: number of months prior or after the month being measured
    :param clinic: name of clinic to return the measurement for
    :param measure: name of the measure to return
    :return: the measure value as an int, or 0 if measure is not numeric
    """
    offset_month = report_month + relativedelta(months=month_offset)
    df = clinic_measures[offset_month]
    if measure in df.select_dtypes(include=['int64', 'int32', 'float64']).columns:
        view = df.loc[(df['Clinic'] == clinic)]
        if view.empty:
            return 0
        else:
            return int(view.at[min(view.index), measure])
# END get_clinic_count_measure


def get_clinics(report_month: datetime) -> list[str]:
    """
    Returns an array of clinic names from the referral measures data.
    :param report_month: month being measured
    :return: a list of unique clinic names
    """
    df = clinic_measures[report_month]
    return df.loc[(df['Clinic'] != '*ALL*'), 'Clinic'].unique().tolist()[::1]
# END get_clinics


def get_clinic_distribution_count(report_month: datetime,
                                  clinic: str,
                                  measure: str,
                                  category: str,
                                  priority: str) -> int:
    """
    Returns the distribution count for a clinic, category, and bin name combination
    :param report_month: effective month for the count
    :param clinic: name of the clinic to get the count for
    :param measure: the name of the distribution category
    :param category: the name of the distribution bin within the category
    :param priority: the priority of the referrals in the distribution
    :return: a count of referrals
    """

    df = distribution_data[report_month]
    view = df.loc[(df['Clinic'] == clinic)
                  & (df['Referral Priority'] == priority)
                  & (df[measure] == category)]
    if len(view.index) == 0:
        return 0
    else:
        return int(view.at[min(view.index), 'Referrals Aged'])
# END get_clinic_distribution_count


def _up_or_down(x: float) -> str:
    """
    Helper function to return a directional indicator based on the given
    number being positive or negative.  Applied to Pandas series.
    :param x: A numeric value
    :return: A directional indicator string
    """
    if x < 0.0:
        return "\u25BC"
    elif x > 0.0:
        return "\u25B2"
    else:
        return "-"
# END up_or_down


def _calculate_dependent_variances(curr_month_df: DataFrame,
                                   measures: list[dict]) -> DataFrame:
    """
    Calculates variances that are dependent upon measure calculations or rolling sums.
    :param curr_month_df: process measure data for the current month
    :param measures: a list of dictionary nodes that describe variances to calculate
    :return: the new current month dataframe
    """

    for measure in measures:
        variances = curr_month_df[measure['value']] - curr_month_df[measure['standard']]

        directions = variances.apply(_up_or_down)

        curr_month_df[measure['measure']] = variances
        curr_month_df['Dir ' + measure['measure']] = directions

    # Return a copy to automagically clean up dataframe fragmentation caused by
    # adding lots of individual columns
    return curr_month_df.copy()
# END calculate_dependent_variances


def _add_targets(curr_month_df: DataFrame) -> DataFrame:
    """
    Adds columns with measure targets to the monthly process measurement data.
    :param curr_month_df: process measure data for the current month
    :return: the new current month dataframe
    """
    curr_month_df['Target Pct Routine Referrals Seen in 30d'] = 50.0
    curr_month_df['Target Pct Urgent Referrals Seen in 5d'] = 50.0
    return curr_month_df
# END add_targets


def _calculate_variance_categories(curr_month_df: DataFrame, categories: list[dict]) -> DataFrame:
    """
    Tags each clinic with performance and improvement categories based on near term,
    midterm, and long term variances against targets and against historical rates.
    :param curr_month_df: process measure data for the current month
    :param categories: list of categories and their included variance measures
    :return: the new current month dataframe
    """

    def calculate_score(x: float, score: int) -> int:
        if x >= 0.0:
            return score
        else:
            return 0

    for category in categories:
        near_vars = curr_month_df[category['near-term']].apply(calculate_score, args=(1,))
        mid_vars = curr_month_df[category['mid-term']].apply(calculate_score, args=(10,))
        long_vars = curr_month_df[category['long-term']].apply(calculate_score, args=(100,))
        scores = near_vars + mid_vars + long_vars
        curr_month_df[category['category']] = scores.map(category['rubric'])

    return curr_month_df
# END calculate_variance_categories


def _calculate_process_time_measures() -> None:
    first_month = datetime.combine(_AS_OF_DATE.replace(day=1).date(), datetime.min.time()) + relativedelta(months=-12)

    for iter_month in range(12):
        curr_month = first_month + relativedelta(months=iter_month)
        print('Calculating clinic process measures for ' + curr_month.strftime('%Y-%m-%d'))

        # Calculate measure values for this month
        curr_month_clinic_df, curr_month_distributions_df = (
            _calculate_process_measures_for_month(r.referral_df, curr_month))
        curr_month_clinic_df = _add_targets(curr_month_clinic_df)
        curr_month_clinic_df = _calculate_dependent_variances(curr_month_clinic_df, _DEPENDENT_VARIANCES)
        curr_month_clinic_df = _calculate_variance_categories(curr_month_clinic_df, _VARIANCE_CATEGORIES)

        # Keep the 12 months of data resident in memory for requests from Bokeh
        clinic_measures[curr_month] = curr_month_clinic_df
        distribution_data[curr_month] = curr_month_distributions_df
# END _calculate_process_time_measures


# MAIN

print('Calculating clinic processing time measures...')

last_month = datetime.combine(_AS_OF_DATE.replace(day=1).date(), datetime.min.time()) + relativedelta(months=-1)
_calculate_process_time_measures()

print('Clinic processing time measures calculated')
