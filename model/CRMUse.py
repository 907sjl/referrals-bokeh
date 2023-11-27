"""
CRMUse.py
Module that provides measure data for the relative use of the Clinic Referral Management system vs. the schedule
https://907sjl.github.io/

Top-Level Variables:
    overall_measures[month] - Calculated measurement data by month aggregated across all clinics
    clinic_measures[month] - Calculated measurement data by month by clinic
    distribution_data[month] - Calculated counts by category by month and clinic
    test_results[month] - Calculated test scores of CRM use by month and clinic
    last_month - The first day of the previous month at time 00:00:00

Functions:
    set_crm_usage_score_for_clinic - Calculates the point score for one of the CRM usage tests
    get_counts_by_not_accepted_referral_status - Returns referral status and counts for referrals not accepted,
                                                 canceled, nor rejected
    get_not_accepted_referral_status_list - Returns the list of unique statuses included in the counts by status
    get_clinic_count_measure - Returns the requested measure value as an integer data type
    get_crm_usage_test_results - Returns the CRM usage test results for a clinic as a DataFrame of milestones and scores
"""

from pandas import DataFrame

import pandas as pd
import numpy as np 

from datetime import datetime 
from dateutil.relativedelta import relativedelta

import model.source.Referrals as r


# Effective as-of date for data
_AS_OF_DATE = datetime(2023, 3, 1)

# Top-level variable pointers to CRM data
overall_measures = {}
clinic_measures = {}
distribution_data = {}
test_results = {}

# Config for a standardized test of CRM use vs. the schedule book
_CRM_USAGE_TESTS = {'Milestone': ['Accepted', 'Linked', 'Seen', 'Completed', 'Import'],
                    'Title': ['% of Referrals Accepted',
                              '% of Scheduled Referrals with Linked Appt',
                              '% of Seen Referrals Tagged as Seen',
                              '% of Seen Referrals that are Completed',
                              '% of DSM Referrals with CRM Referral'],
                    'Point Value': [10, 10, 10, 10, 5],
                    'Result': [0, 0, 0, 0, 0],
                    'Score': [0, 0, 0, 0, 0],
                    'merge_key': [0, 0, 0, 0, 0]}

# A template for test results for a clinic and a month
_tests_df = pd.DataFrame(_CRM_USAGE_TESTS, index=[0, 1, 2, 3, 4])


def _calculate_distributions_after_90_days(source_df: DataFrame, category_column: str) -> DataFrame:
    """
    Calculates distributions of referrals by age category bin.
    :param source_df: The DataFrame of referrals to count
    :param category_column: Name of the column in the DataFrame that contains the category to count by
    :return: A DataFrame of counts by clinic and category
    """

    # Create sums of referrals by clinic and category combinations
    distribution_df = source_df.groupby(['Clinic', category_column]) \
        .agg({'Referral Aged Yn': 'sum'}) \
        .rename(columns={'Referral Aged Yn': 'Referrals Aged'}) \
        .reset_index()
    
    return distribution_df
# END calculate_distributions_after_90_days


def set_crm_usage_score_for_clinic(report_month: datetime, clinic: str, milestone: str, result_ratio: float) -> None:
    """
    Calculates a point score for one of the tests of CRM use.
    :param report_month: The month to calculate the score for
    :param clinic: The clinic to calculate the score for
    :param milestone: The test to calculate the score for
    :param result_ratio: The percentage result for the test
    """

    df = test_results[report_month]
    vw = df.loc[((df['Milestone'] == milestone) & (df['Clinic'] == clinic))]
    index = min(vw.index) 
    value = vw.at[min(vw.index), 'Point Value'] 
    score = value * result_ratio
    df.at[index, 'Result'] = int((result_ratio * 100.0) + 0.5)
    df.at[index, 'Score'] = round(score, 2) 
# END set_crm_usage_score_for_clinic


def _calculate_crm_measures_for_month(referral_df: DataFrame,
                                      report_month: datetime) -> tuple[DataFrame, DataFrame, DataFrame]:
    """
    Calculates measures of CRM usage and test data for a given month.
    :param referral_df: The master DataFrame of referral source data
    :param report_month: The month to calculate measures for
    :return: A tuple with three DataFrames
        - A DataFrame of CRM usage measures
        - A DataFrame of referral distribution counts by age categories
        - A DataFrame with usage test templates that must be calculated using these measures
    """

    next_month = report_month + relativedelta(months=1)

    # Create sliced views of data for various lookback periods of time
    month_view_90d = referral_df.loc[(referral_df['Reporting Date 90 Day Lag'] >= report_month) 
                                     & (referral_df['Reporting Date 90 Day Lag'] < next_month)].copy()
    
    # Create master list of clinics used to merge data using left joins and add a placeholder clinic named *ALL* 
    crm_df = pd.DataFrame({'Clinic': np.sort(referral_df['Clinic'].unique())})
    crm_df = pd.concat([pd.DataFrame({'Clinic': '*ALL*'}, index=[0]), crm_df]).reset_index(drop=True)

    # Create a dataset with counts of referrals by status that are not accepted
    not_accepted_90d_df = month_view_90d.loc[(month_view_90d['Referral Accepted Yn'] == 0) 
                                             & (month_view_90d['Referral Aged Yn'] == 1)]
    after_90d_distribution_df = _calculate_distributions_after_90_days(not_accepted_90d_df, 'Referral Status')

    # Create a dataset with placeholder test results for CRM use in each clinic 
    crm_tests_90d_df = pd.merge(crm_df, _tests_df, how='cross')

    # MEASURE: Count of appointments linked in CRM after 90 days
    scheduled_by_90d_df = month_view_90d.loc[(month_view_90d['Appointment Linked Yn'] == 1)
                                             & (month_view_90d['Referral Aged Yn'] == 1)] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': 'Appointments Linked After 90d'})
    
    # Append to data set of referral performance measures by clinic
    crm_df = pd.merge(crm_df, scheduled_by_90d_df, how='left', on=['Clinic'])

    # MEASURE: Count of referrals seen in CRM after 90 days
    seen_by_90d_df = month_view_90d.loc[(month_view_90d['Referral Seen in CRM Yn'] == 1)
                                        & (month_view_90d['Referral Aged Yn'] == 1)] \
        .groupby('Clinic') \
        .agg({'Referral ID': 'count'}) \
        .rename(columns={'Referral ID': 'Referrals Seen in CRM After 90d'})
    
    # Append to data set of referral performance measures by clinic
    crm_df = pd.merge(crm_df, seen_by_90d_df, how='left', on=['Clinic'])

    # Clean up missing data from clinics by replacing with zero 
    crm_df = crm_df.fillna(0)
   
    return crm_df, after_90d_distribution_df, crm_tests_90d_df
# End calculate_crm_measures_for_month


def get_counts_by_not_accepted_referral_status(report_month: datetime, clinic: str) -> DataFrame:
    """
    Returns a DataFrame of referral status and counts for referrals not accepted, canceled,
    nor rejected.
    :param report_month: The month to return counts for
    :param clinic: The clinic to return counts for
    :return: A DataFrame of referral counts by status
    """
    df = distribution_data[report_month]
    return df.loc[(df['Clinic'] == clinic)]
# END get_counts_by_not_accepted_referral_status


def get_not_accepted_referral_status_list(report_month: datetime, clinic: str) -> list[str]:
    """Returns the list of unique statuses included in the counts by status."""
    df = distribution_data[report_month]
    return df.loc[(df['Clinic'] == clinic)]['Referral Status'].tolist()
# END get_not_accepted_referral_status_list


def get_clinic_count_measure(report_month: datetime, clinic: str, measure: str) -> int:
    """Returns a clinic measure value as an integer count or as zero if there is no value."""
    df = clinic_measures[report_month]
    if measure in df.select_dtypes(include=['int64', 'int32', 'float64']).columns:
        view = df.loc[(df['Clinic'] == clinic)]
        if view.empty:
            return 0
        else:
            return int(view.at[min(view.index), measure])
# END get_clinic_count_measure


def get_crm_usage_test_results(report_month: datetime, clinic: str) -> DataFrame:
    """Returns the CRM usage test results for a clinic as a DataFrame of milestones and scores."""
    df = test_results[report_month]
    return df.loc[(df['Clinic'] == clinic)]
# END get_crm_usage_test_results


# MAIN

print('Calculating CRM measures...')

last_month = datetime.combine(_AS_OF_DATE.replace(day=1).date(), datetime.min.time()) + relativedelta(months=-1)

# Create dictionary for months and wait time measures starting with last month
# Need to have 12 months readily available
for iter_month in range(12):
    curr_month = last_month + relativedelta(months=-1*iter_month)
    print('Calculating measures for ' + curr_month.strftime('%Y-%m-%d'))
    curr_month_crm_df, curr_month_distributions_df, curr_month_tests_df = (
        _calculate_crm_measures_for_month(r.referral_df, curr_month))
    overall_measures[curr_month] = curr_month_crm_df.loc[(curr_month_crm_df['Clinic'] == '*ALL*')]
    clinic_measures[curr_month] = curr_month_crm_df.loc[~(curr_month_crm_df['Clinic'] == '*ALL*')]
    distribution_data[curr_month] = (
        curr_month_distributions_df.loc)[~(curr_month_distributions_df['Clinic'] == '*ALL*')]
    test_results[curr_month] = curr_month_tests_df

print('CRM measures calculated')
