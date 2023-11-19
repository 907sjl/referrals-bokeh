"""
DSMs.py
Class that represents the data model and measures for direct secure message usage.
https://907sjl.github.io/
"""

from pandas import DataFrame

import pandas as pd
import numpy as np 

from datetime import datetime 
from dateutil.relativedelta import relativedelta

print('Loading DSM data...')

# Effective as-of date for data
AS_OF_DATE = datetime(2023, 3, 1)


# Initializations - run on execution


overall_measures = {}
dsm_views = {}


# Support functions for transforming data


def create_master_data_frame():
    # Future possibility of filtering to a recent period of time but for 
    # now this loads quick enough 

    date_columns = ['Message Date',
                    'Date Referral Sent']

    column_types = {
        'Message ID': 'string',
        'Message Date': 'object',
        'Clinic': 'string',
        'Sender Category': 'string',
        'Sent From': 'string',
        'Referral ID': 'string',
        'Date Referral Sent': 'object',
        'Person ID': 'string'}

    df = pd.read_csv('DirectSecureMessages.csv', dtype=column_types, parse_dates=date_columns)

    # Create time shifted date values to simplify transformations downstream
    df['Reporting Date 90 Day Lag'] = df['Message Date'] + pd.Timedelta(days=90)

    # Create convenience column to aggregate unique patients with referrals to the
    # same clinic that a DSM was sent to
    idx = ~df['Referral ID'].isna()
    df.loc[idx, 'Referral Person ID'] = df.loc[idx, 'Person ID']

    # df.to_csv(r'C:\Users\SJL\PycharmProjects\referrals-bokeh\dsm_df.csv')
    return df
# End create_master_data_frame


# Functions to calculate DSM usage measures


def get_dsm_data_for_month(source_df: DataFrame, report_month: datetime) -> DataFrame:
    # Returns the DSM usage data for one reporting month.  A reporting month includes 
    # measure data that looks back the appropriate amount of time for each measure. 
    #   source_df: The pandas dataframe with the master set of dsm data 
    #   report_month: The datetime value of the first day of the month to return data for at time 00:00:00 
    #   returns: Dataframe of DSM usage measures

    next_month = report_month + relativedelta(months=1)

    # Create sliced views of data for various lookback periods of time
    month_view_90d = source_df.loc[(source_df['Reporting Date 90 Day Lag'] >= report_month) 
                                   & (source_df['Reporting Date 90 Day Lag'] < next_month)].copy()
    
    # Create master list of clinics used to merge data using left joins and add a placeholder clinic named *ALL* 
    dsm_data_df = pd.DataFrame({'Clinic': np.sort(source_df['Clinic'].unique())})
    dsm_data_df = pd.concat([pd.DataFrame({'Clinic': '*ALL*'}, index=[0]), dsm_data_df]).reset_index(drop=True)

    # MEASURE: Count of patients with DSM referrals after 90 days
    patients_df = month_view_90d \
        .groupby('Clinic') \
        .agg({'Person ID': 'nunique'}) \
        .rename(columns={'Person ID': 'Patients with DSMs After 90d'})
    
    # Append to data set of referral performance measures by clinic
    dsm_data_df = pd.merge(dsm_data_df, patients_df, how='left', on=['Clinic'])

    # MEASURE: Count of patients with DSM referrals and CRM referrals within 30 days of each other after 90 days
    crm_patients_df = month_view_90d.loc[(~month_view_90d['Referral Person ID'].isna())] \
        .groupby('Clinic') \
        .agg({'Referral Person ID': 'nunique'}) \
        .rename(columns={'Referral Person ID': 'Patients with DSM and CRM Referrals After 90d'})
    
    # Append to data set of referral performance measures by clinic
    dsm_data_df = pd.merge(dsm_data_df, crm_patients_df, how='left', on=['Clinic'])

    # Clean up missing data from clinics by replacing with zero 
    dsm_data_df = dsm_data_df.fillna(0)
   
    return dsm_data_df
# End get_dsm_data_for_month


# Functions for data access


def get_clinic_count_measure(report_month: datetime, clinic: str, measure: str):
    df = dsm_views[report_month]
    if measure in df.select_dtypes(include=['int64', 'int32', 'float64']).columns:
        view = df.loc[(df['Clinic'] == clinic)]
        if view.empty:
            return 0
        else:
            return int(view.at[min(view.index), measure])
# END get_clinic_count_measure


# MAIN - run on execution


last_month = datetime.combine(AS_OF_DATE.replace(day=1).date(), datetime.min.time()) + relativedelta(months=-1)

# Initialize module with master dataframe of referral data 
dsm_df = create_master_data_frame()

# Create dictionary for months and wait time measures starting with last month
# Need to have 12 months readily available
for iter_month in range(12):
    curr_month = last_month + relativedelta(months=-1*iter_month)
    print('Calculating measures for ' + curr_month.strftime('%Y-%m-%d'))
    curr_month_dsm_df = get_dsm_data_for_month(dsm_df, curr_month)
    overall_measures[curr_month] = curr_month_dsm_df.loc[(curr_month_dsm_df['Clinic'] == '*ALL*')]
    dsm_views[curr_month] = curr_month_dsm_df.loc[~(curr_month_dsm_df['Clinic'] == '*ALL*')]

print('DSM data loaded')
