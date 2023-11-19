"""
Referrals.py
Class that represents the source for referral data.
https://907sjl.github.io/
"""

import pandas as pd
from pandas import DataFrame

from datetime import datetime

print('Loading referral data...')

# Effective as-of date for data
AS_OF_DATE = datetime(2023, 3, 1)


def create_master_data_frame():
    # Future possibility of filtering to a recent period of time but for 
    # now this loads quick enough 

    date_columns = ['Date Referral Sent',
                    'Date Referral Seen',
                    'Date Patient Checked In',
                    'Date Held',
                    'Date Pending Reschedule',
                    'Date Last Referral Update',
                    'Date Similar Appt Scheduled',
                    'Date Accepted',
                    'Date Referral Written',
                    'Date Referral Completed',
                    'Date Referral Scheduled']

    column_types = {
        'Referral ID': 'string',
        'Source Location': 'string',
        'Provider Referred To': 'string',
        'Location Referred To': 'string',
        'Referral Priority': 'string',
        'Referral Status': 'string',
        'Patient ID': 'string',
        'Clinic': 'string',
        'Last Referral Update By': 'string',
        'Assigned Personnel': 'string',
        'Organization Referred To': 'string',
        'Reason for Hold': 'string',
        'Referral Sub-Status': 'string',
        'Date Referral Sent': 'object',
        'Date Referral Seen': 'object',
        'Date Patient Checked In': 'object',
        'Date Held': 'object',
        'Date Pending Reschedule': 'object',
        'Date Last Referral Update': 'object',
        'Date Similar Appt Scheduled': 'object',
        'Date Accepted': 'object',
        'Date Referral Written': 'object',
        'Date Referral Completed': 'object',
        'Date Referral Scheduled': 'object'}

    df = pd.read_csv('referrals.csv', dtype=column_types, parse_dates=date_columns)

    # Create time shifted date values to simplify transformations downstream
    df['Reporting Date 30 Day Lag'] = df['Date Referral Sent'] + pd.Timedelta(days=30)
    df['Reporting Date 90 Day Lag'] = df['Date Referral Sent'] + pd.Timedelta(days=90)
    df['Reporting Date 5 Day Lag'] = df['Date Referral Sent'] + pd.Timedelta(days=5)
    df['As Of Date'] = AS_OF_DATE

    # Calculate processing time deltas for use in measures
    # Days until the referral tagged as seen or patient checked into clinic appointment
    df['Date Patient Seen or Checked In'] = df['Date Referral Seen']
    idx = df['Date Patient Seen or Checked In'].isna()
    df.loc[idx, 'Date Patient Seen or Checked In'] = df.loc[idx, 'Date Patient Checked In']
    df['Days until Patient Seen or Check In'] = (
            (df['Date Patient Seen or Checked In'] - df['Date Referral Sent']) / pd.Timedelta(days=1))
    idx = df['Date Patient Seen or Checked In'].isna()
    df.loc[idx, 'Days until Patient Seen or Check In'] = (
            (df.loc[idx, 'As Of Date'] - df.loc[idx, 'Date Referral Sent']) / pd.Timedelta(days=1))

    # Days until the referral accepted
    df['Days until Referral Accepted'] = (
            (df['Date Accepted'] - df.loc[idx, 'Date Referral Sent']) / pd.Timedelta(days=1))
    idx = df['Date Accepted'].isna()
    df.loc[idx, 'Days until Referral Accepted'] = (
            (df.loc[idx, 'As Of Date'] - df.loc[idx, 'Date Referral Sent']) / pd.Timedelta(days=1))

    # Days until the referral completed
    df['Days until Referral Completed'] = (
            (df['Date Referral Completed'] - df['Date Referral Sent']) / pd.Timedelta(days=1))
    idx = df['Date Referral Completed'].isna()
    df.loc[idx, 'Days until Referral Completed'] = (
            (df.loc[idx, 'As Of Date'] - df.loc[idx, 'Date Referral Sent']) / pd.Timedelta(days=1))

    # Days until the referral linked to an appointment or patient scheduled for a clinic appointment
    df['Date Referral or Patient Scheduled'] = df['Date Referral Scheduled']
    idx = df['Date Referral or Patient Scheduled'].isna()
    df.loc[idx, 'Date Referral or Patient Scheduled'] = df.loc[idx, 'Date Similar Appt Scheduled']
    df['Days until Referral or Patient Scheduled'] = (
            (df['Date Referral or Patient Scheduled'] - df['Date Referral Sent']) / pd.Timedelta(days=1))
    idx = df['Date Referral or Patient Scheduled'].isna()
    df.loc[idx, 'Days until Referral or Patient Scheduled'] = (
            (df.loc[idx, 'As Of Date'] - df.loc[idx, 'Date Referral Sent']) / pd.Timedelta(days=1))

    # Days on hold
    df['Days On Hold'] = (AS_OF_DATE - df['Date Held']) / pd.Timedelta(days=1)

    # Days pending reschedule
    df['Days Pending Reschedule'] = (AS_OF_DATE - df['Date Pending Reschedule']) / pd.Timedelta(days=1)

    # Create a convenience column to aggregate referrals that are sent and not
    # rejected, canceled, or closed without being seen
    idx = ((~df['Date Referral Sent'].isna())
           & (~df['Referral Status'].isin(['Rejected', 'Cancelled']))
           & (~df['Referral Status'].isin(['Closed', 'Completed']) | (~df['Date Patient Seen or Checked In'].isna())))
    df['Referral Aged Yn'] = 0
    df.loc[idx, 'Referral Aged Yn'] = 1

    # Create a convenience column to aggregate referrals that sent
    idx = ~df['Date Referral Sent'].isna()
    df['Referral Sent Yn'] = 0
    df.loc[idx, 'Referral Sent Yn'] = 1

    # Create a convenience column to aggregate referrals that seen or checked in to an
    # appointment at the same clinic
    idx = ~df['Date Patient Seen or Checked In'].isna()
    df['Referral Seen or Checked In Yn'] = 0
    df.loc[idx, 'Referral Seen or Checked In Yn'] = 1

    # Create a convenience column to aggregate referrals with an appointment scheduled
    # at the same clinic
    idx = ~df['Date Similar Appt Scheduled'].isna()
    df['Patient Scheduled Yn'] = 0
    df.loc[idx, 'Patient Scheduled Yn'] = 1

    # Create a convenience column to aggregate referrals with an appointment linked to
    # the referral
    idx = ~df['Date Referral Scheduled'].isna()
    df['Appointment Linked Yn'] = 0
    df.loc[idx, 'Appointment Linked Yn'] = 1

    # Create a convenience column to aggregate referrals that have been accepted
    idx = ~df['Date Accepted'].isna()
    df['Referral Accepted Yn'] = 0
    df.loc[idx, 'Referral Accepted Yn'] = 1

    # Create a convenience column to aggregate referrals that have been completed
    idx = ~df['Date Referral Completed'].isna()
    df['Referral Completed Yn'] = 0
    df.loc[idx, 'Referral Completed Yn'] = 1

    # Create a convenience column to aggregate referrals that have been tagged
    # as seen in the clinic referral management system
    idx = ~df['Date Referral Seen'].isna()
    df['Referral Seen in CRM Yn'] = 0
    df.loc[idx, 'Referral Seen in CRM Yn'] = 1

    # df.to_csv(r'C:\Users\SJL\PycharmProjects\referrals-bokeh\referrals_df.csv')
    return df
# END create_master_data_frame


def calculate_age_category(source: DataFrame, category_column: str, age_column: str):
    """
    Add age category values to a column in a given dataframe using age values
    in a given column.
    :param source: a dataframe with age values
    :param category_column: name of the column to receive the category values
    :param age_column: name of the column with the age values
    :return: nothing
    """

    # Initialize the new category name column with either the first category or
    # the default for unknown
    source[category_column] = source[age_column].apply(lambda x: '7d' if x <= 7.0 else '(none)')

    # Override the default unknown category with the other categories that apply
    idx = ((source[age_column] > 7.0) & (source[age_column] <= 14.0))
    source.loc[idx, [category_column]] = '14d'

    idx = ((source[age_column] > 14.0) & (source[age_column] <= 30.0))
    source.loc[idx, [category_column]] = '30d'

    idx = ((source[age_column] > 30.0) & (source[age_column] <= 60.0))
    source.loc[idx, [category_column]] = '60d'

    idx = ((source[age_column] > 60.0) & (source[age_column] <= 90.0))
    source.loc[idx, [category_column]] = '90d'

    source.loc[(source[age_column] > 90.0), [category_column]] = '>90d'
# END calculate_age_category


# MAIN

# Initialize module with master dataframe of referral data 
referral_df = create_master_data_frame()

print('Referral data loaded')
