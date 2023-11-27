"""
DSMs.py
Module that sources and provides data for individual direct secure messages.  This module automatically
loads top level variables with this data when imported.
https://907sjl.github.io/

Top-Level Variables:
    dsm_df - The DSM master DataFrame

Functions:
    load_dsm_data - Loads direct secure message data from the source
    create_master_data_frame - Calculates facts and adds convenience columns for downstream filtering
"""

import pandas as pd
from pandas import DataFrame

from datetime import datetime 

# Effective as-of date for data
_AS_OF_DATE = datetime(2023, 3, 1)


def load_dsm_data() -> DataFrame:
    """Loads direct secure message data from the source and returns a DataFrame with a row for each message."""

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

    return pd.read_csv('DirectSecureMessages.csv', dtype=column_types, parse_dates=date_columns)
# END load_dsm_data


def create_master_data_frame():
    """
    Calculates simple facts for each message and adds columns to simplify downstream filtering.
    :return: A DataFrame with the message data that has one row per message
    """

    df = load_dsm_data()

    # Create time shifted date values to simplify transformations downstream
    df['Reporting Date 90 Day Lag'] = df['Message Date'] + pd.Timedelta(days=90)

    # Create convenience column to find unique patients who also have referrals
    # to the same clinic that a DSM was sent to
    idx = ~df['Referral ID'].isna()
    df.loc[idx, 'Referral Person ID'] = df.loc[idx, 'Person ID']

    # df.to_csv(r'C:\Users\SJL\PycharmProjects\referrals-bokeh\dsm_df.csv')
    return df
# End create_master_data_frame


# MAIN

print('Loading DSM data...')

# Initialize module with master dataframe of referral data 
dsm_df = create_master_data_frame()

print('DSM data loaded')
