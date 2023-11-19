"""
CRM.py
Class that represents the data model and measures for clinic referral management system usage.
https://907sjl.github.io/
"""

from pandas import DataFrame

import pandas as pd
import numpy as np 

from datetime import datetime 
from dateutil.relativedelta import relativedelta

import model.Referrals as referrals

print('Loading CRM usage test data set...')

# Effective as-of date for data
AS_OF_DATE = datetime(2023, 3, 1)


# Initializations - run on execution

overall_measures = {}
crm_views = {}
distribution_views = {}
test_results = {}

crm_usage_tests = {'Milestone': ['Accepted', 'Linked', 'Seen', 'Completed', 'Import'],
                   'Title': ['% of Referrals Accepted',
                             '% of Scheduled Referrals with Linked Appt',
                             '% of Seen Referrals Tagged as Seen',
                             '% of Seen Referrals that are Completed',
                             '% of DSM Referrals with CRM Referral'],
                   'Point Value': [10, 10, 10, 10, 5],
                   'Result': [0, 0, 0, 0, 0],
                   'Score': [0, 0, 0, 0, 0],
                   'merge_key': [0, 0, 0, 0, 0]}
tests_df = pd.DataFrame(crm_usage_tests, index=[0, 1, 2, 3, 4])


# Support functions for transforming data


def calculate_distributions_after_90_days(source, category_column):
    # Calculates distributions of referrals by age category
    #
    # source: the view of referrals to use from the master dataframe 
    # category_column: the name of the column that contains the category values 
    # returns: a dataframe of clinics and counts by category

    # Create sums of referrals by clinic and category combinations
    distribution_df = source.groupby(['Clinic', category_column]) \
        .agg({'Referral Aged Yn': 'sum'}) \
        .rename(columns={'Referral Aged Yn': 'Referrals Aged'}) \
        .reset_index()
    
    return distribution_df
# END calculate_distributions_after_90_days


def set_crm_usage_score_for_clinic(report_month: datetime, clinic: str, milestone: str, result_ratio: float) -> None:
    # Adds a point score to a test of CRM usage for a reporting month.  Tests will not 
    # have result data until this is called. But a placeholder for a month and test must 
    # be ready. 
    # report_month: The monthly report that should include the score
    # report_clinic: The clinic tested
    # milestone: The milestone tested 
    # result_ratio: The percentage result of the test 
    df = test_results[report_month]
    vw = df.loc[((df['Milestone'] == milestone) & (df['Clinic'] == clinic))]
    index = min(vw.index) 
    value = vw.at[min(vw.index), 'Point Value'] 
    score = value * result_ratio
    df.at[index, 'Result'] = int((result_ratio * 100.0) + 0.5)
    df.at[index, 'Score'] = round(score, 2) 
# END set_crm_usage_score_for_clinic


# Calculate CRM usage measures and distributions


def calculate_crm_measures_for_month(referral_df: DataFrame, report_month: datetime):
    # Returns the CRM usage test data for one reporting month.  A reporting month includes 
    # measure data that looks back the appropriate amount of time for each measure. 
    #   referral_df: The pandas dataframe with the master set of referral data 
    #   report_month: The datetime value of the first day of the month to return data for at time 00:00:00 
    #   returns: 1) a dataframe of CRM usage measures, 
    #            2) a dataframe of referral distribution counts, 
    #            3) a dataframe of placeholder crm usage test results for each clinic 

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
    after_90d_distribution_df = calculate_distributions_after_90_days(not_accepted_90d_df, 'Referral Status')

    # Create a dataset with placeholder test results for CRM use in each clinic 
    crm_tests_90d_df = pd.merge(crm_df, tests_df, how='cross') 

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


# Not Accepted Status Measures


def get_counts_by_not_accepted_referral_status(report_month: datetime, clinic: str) -> DataFrame:
    df = distribution_views[report_month]
    return df.loc[(df['Clinic'] == clinic)]
# END get_counts_by_not_accepted_referral_status


def get_not_accepted_referral_status_list(report_month: datetime, clinic: str) -> list[str]:
    df = distribution_views[report_month]
    return df.loc[(df['Clinic'] == clinic)]['Referral Status'].tolist()
# END get_not_accepted_referral_status_list


# Supporting functions for data access


def get_clinic_count_measure(report_month: datetime, clinic: str, measure: str):
    df = crm_views[report_month]
    if measure in df.select_dtypes(include=['int64', 'int32', 'float64']).columns:
        view = df.loc[(df['Clinic'] == clinic)]
        if view.empty:
            return 0
        else:
            return int(view.at[min(view.index), measure])
# END get_clinic_count_measure


def get_crm_usage_test_results(report_month: datetime, clinic: str) -> DataFrame:
    df = test_results[report_month]
    return df.loc[(df['Clinic'] == clinic)]
# END get_crm_usage_test_results


# MAIN


last_month = datetime.combine(AS_OF_DATE.replace(day=1).date(), datetime.min.time()) + relativedelta(months=-1)

# Create dictionary for months and wait time measures starting with last month
# Need to have 12 months readily available
for iter_month in range(12):
    curr_month = last_month + relativedelta(months=-1*iter_month)
    print('Calculating measures for ' + curr_month.strftime('%Y-%m-%d'))
    curr_month_crm_df, curr_month_distributions_df, curr_month_tests_df = (
        calculate_crm_measures_for_month(referrals.referral_df, curr_month))
    overall_measures[curr_month] = curr_month_crm_df.loc[(curr_month_crm_df['Clinic'] == '*ALL*')]
    crm_views[curr_month] = curr_month_crm_df.loc[~(curr_month_crm_df['Clinic'] == '*ALL*')]
    distribution_views[curr_month] = (
        curr_month_distributions_df.loc)[~(curr_month_distributions_df['Clinic'] == '*ALL*')]
    test_results[curr_month] = curr_month_tests_df

print('CRM usage test data loaded')
