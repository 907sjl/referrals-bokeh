"""
DSMs.py
Module that provides data from measures of direct secure message usage and conversions to referrals.
This module automatically loads top level variables with this data when imported.
https://907sjl.github.io/

Top-Level Variables:
    overall_measures[month] - Calculated measurement data by month aggregated across all clinics
    clinic_measures[month] - Calculated measurement data by month by clinic
    last_month - The first day of the previous month at time 00:00:00

Functions:
    get_clinic_count_measure - Returns the requested measure value as an integer data type
"""

import pandas as pd
from pandas import DataFrame
import numpy as np

from datetime import datetime 
from dateutil.relativedelta import relativedelta

import model.source.DSMs as d


# Effective as-of date for data
_AS_OF_DATE = datetime(2023, 3, 1)

# Top-level variable pointers to the DSM data
overall_measures = {}
clinic_measures = {}


def _calculate_dsm_measures_for_month(source_df: DataFrame, report_month: datetime) -> DataFrame:
    """
    Calculates DSM usage measures and measures of DSM conversions to referrals for a given month.
    :param source_df: The master DataFrame of DSM source data
    :param report_month: The first day of the month to return data for at time 00:00:00
    :return: Dataframe of DSM usage measures for the given month
    """

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


def get_clinic_count_measure(report_month: datetime, clinic: str, measure: str) -> int:
    """
    Returns the requested measure value as an integer data type.
    :param report_month: The month to return the measure for
    :param clinic: The clinic to return the measure for
    :param measure: The name of the measure to return
    :return: The integer measure value or zero if there is none
    """

    df = clinic_measures[report_month]
    if measure in df.select_dtypes(include=['int64', 'int32', 'float64']).columns:
        view = df.loc[(df['Clinic'] == clinic)]
        if view.empty:
            return 0
        else:
            return int(view.at[min(view.index), measure])
# END get_clinic_count_measure


def _calculate_dsm_measures() -> None:
    for iter_month in range(12):
        curr_month = last_month + relativedelta(months=-1 * iter_month)
        print('Calculating measures for ' + curr_month.strftime('%Y-%m-%d'))
        curr_month_dsm_df = _calculate_dsm_measures_for_month(d.dsm_df, curr_month)
        overall_measures[curr_month] = curr_month_dsm_df.loc[(curr_month_dsm_df['Clinic'] == '*ALL*')]
        clinic_measures[curr_month] = curr_month_dsm_df.loc[~(curr_month_dsm_df['Clinic'] == '*ALL*')]
# END calculate_dsm_measures


# MAIN - run on execution

print('Calculating DSM measures...')

last_month = datetime.combine(_AS_OF_DATE.replace(day=1).date(), datetime.min.time()) + relativedelta(months=-1)
_calculate_dsm_measures()

print('DSM measures calculated')
