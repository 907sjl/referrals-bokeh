"""
PendingTime.py
Module that provides data for pending referral wait times.  This data is not aggregated by month.  All referrals
in a pending status are included.
https://907sjl.github.io/

Top-Level Variables:
    last_month - The first day of the previous month at time 00:00:00

Functions:
    get_counts_by_category - Returns the counts of referrals by category in a given pending status
    get_count_by_age_category - Returns count of referrals in an age bin for referrals in the given pending status
    get_counts_by_on_hold_reason - Returns a DataFrame of current referral counts by hold reason for the given clinic
    get_on_hold_age_by_category - Returns count of on-hold referrals currently in an age category for the given clinic
    get_counts_by_pending_reschedule_sub_status - Returns pending reschedule referral counts by queue sub-status
    get_pending_reschedule_age_by_category - Returns count of pending reschedule referrals in an age category
    get_counts_by_pending_acceptance_sub_status - Returns pending acceptance referral counts by queue sub-status
    get_pending_acceptance_age_by_category - Returns count of pending acceptance referrals in an age category
    get_counts_by_accepted_referral_sub_status - Returns accepted stats referral counts by queue sub-status
    get_accepted_referral_age_by_category - Returns count of accepted referrals in an age category
"""

from pandas import DataFrame

from datetime import datetime
from dateutil.relativedelta import relativedelta

import model.source.Referrals as r

# Effective as-of date for data
_AS_OF_DATE = datetime(2023, 3, 1)


def _calculate_on_hold_measures(referral_df: DataFrame) -> tuple[DataFrame, DataFrame]:
    """
    Calculates measures of referral time on hold for referrals currently on hold.
    :param referral_df: The master DataFrame of referral source data
    :return: Returns a tuple of two DataFrames
        - A DataFrame of referral counts by age category on hold
        - A DataFrame of referral counts by hold reason
    """

    # Create sliced views of data for the on hold or pending statuses
    on_hold_df = referral_df.loc[(referral_df['Referral Status'] == 'On Hold')].copy()

    # Categorize the days on hold
    r.calculate_age_category(on_hold_df, 'Age Category On Hold', 'Days On Hold')

    # Create sums of referrals by clinic and age category combinations
    age_distribution_df = on_hold_df.groupby(['Clinic', 'Age Category On Hold']) \
        .agg({'Referral Aged Yn': 'sum'}) \
        .rename(columns={'Referral Aged Yn': 'Referrals Aged'}) \
        .reset_index()

    # Create sums of referrals by clinic and hold reason combinations
    reason_distribution_df = on_hold_df.groupby(['Clinic', 'Reason for Hold']) \
        .agg({'Referral Aged Yn': 'sum'}) \
        .rename(columns={'Referral Aged Yn': 'Referrals Aged'}) \
        .reset_index()
    
    return age_distribution_df, reason_distribution_df  
# END calculate_on_hold_measures


def get_counts_by_category(clinic: str, count_function: str, category_column: str, values_column: str) -> DataFrame:
    """
    Returns the counts of referrals by category in a given pending status.
    :param clinic: The name of the clinic to return data for
    :param count_function: The name of a function in this module that returns the category count
    :param category_column: The name of the category column to return in a default
    :param values_column: The name of the values columns to return in a default
    :return: A DataFrame with the referral counts by category
    """
    func = globals()[count_function]
    if func is None:
        return DataFrame.from_dict({category_column: [], values_column: []})
    else:
        return func(clinic).copy()
# END get_counts_by_category


def get_count_by_age_category(clinic: str, count_function: str, category: str) -> int:
    """
    Returns a single count of referrals in an age bin category for referrals currently in the given pending status.
    :param clinic: The name of the clinic to return data for
    :param count_function: The name of a function in this module that returns the category count
    :param category: The name of the age bin category to return a count for
    :return: An integer count of referrals in that age category, or zero if there are none
    """
    func = globals()[count_function]
    if func is None:
        return 0
    else:
        return func(clinic, category)
# END get_count_by_age_category


def get_counts_by_on_hold_reason(clinic: str) -> DataFrame:
    """Returns a DataFrame of current referral counts by hold reason for the given clinic."""
    df = _on_hold_reasons_df.loc[(_on_hold_reasons_df['Clinic'] == clinic)].copy()
    df['Reason for Hold'] = df['Reason for Hold'].str.replace('Coordinating', 'Coord.')
    return df
# END get_counts_by_on_hold_reason


def get_on_hold_age_by_category(clinic: str, category: str) -> int:
    """Returns the count of on-hold referrals currently in an age category for the given clinic."""

    df = _on_hold_ages_df
    view = df.loc[(df['Clinic'] == clinic)
                  & (df['Age Category On Hold'] == category)]
    if len(view.index) == 0:
        return 0
    else:
        return view.at[min(view.index), 'Referrals Aged']
# END get_on_hold_age_by_category


def _calculate_pending_reschedule_measures(referral_df: DataFrame) -> tuple[DataFrame, DataFrame]:
    """
    Calculates measures of referral time waiting for referrals currently pending reschedule.
    :param referral_df: The master DataFrame of referral source data
    :return: Returns a tuple of two DataFrames
        - A DataFrame of referral counts by age category on hold
        - A DataFrame of referral counts by hold reason
    """

    # Create sliced views of data for the on hold or pending statuses
    pending_df = referral_df.loc[(referral_df['Referral Status'] == 'Pending Reschedule')].copy()

    # Categorize the days pending
    r.calculate_age_category(pending_df, 'Age Category Pending Reschedule', 'Days Pending Reschedule')

    # Create sums of referrals by clinic and age category combinations
    age_distribution_df = pending_df.groupby(['Clinic', 'Age Category Pending Reschedule']) \
        .agg({'Referral Aged Yn': 'sum'}) \
        .rename(columns={'Referral Aged Yn': 'Referrals Aged'}) \
        .reset_index()
    
    # Create sums of referrals by clinic and sub-status combinations
    reason_distribution_df = pending_df.groupby(['Clinic', 'Referral Sub-Status']) \
        .agg({'Referral Aged Yn': 'sum'}) \
        .rename(columns={'Referral Aged Yn': 'Referrals Aged'}) \
        .reset_index()
    
    return age_distribution_df, reason_distribution_df  
# End calculate_pending_reschedule_measures


def get_counts_by_pending_reschedule_sub_status(clinic: str) -> DataFrame:
    """Returns a DataFrame of current pending reschedule referral counts by queue sub-status for the given clinic."""
    df = _reschedule_status_df.loc[(_reschedule_status_df['Clinic'] == clinic)].copy()
    df['Referral Sub-Status'] = (
        df['Referral Sub-Status'].str.replace('Call Patient to Schedule Appointment',
                                              'Call Patient to Schedule'))
    return df
# End get_counts_by_pending_reschedule_sub_status


def get_pending_reschedule_age_by_category(clinic: str, category: str) -> int:
    """Returns the count of pending reschedule referrals currently in an age category for the given clinic."""

    df = _reschedule_ages_df
    view = df.loc[(df['Clinic'] == clinic)
                  & (df['Age Category Pending Reschedule'] == category)]
    if len(view.index) == 0:
        return 0
    else:
        return view.at[min(view.index), 'Referrals Aged']
# END get_pending_reschedule_age_by_category


def _calculate_pending_acceptance_measures(referral_df: DataFrame) -> tuple[DataFrame, DataFrame]:
    """
    Calculates measures of referral time waiting for referrals currently pending acceptance.
    :param referral_df: The master DataFrame of referral source data
    :return: Returns a tuple of two DataFrames
        - A DataFrame of referral counts by age category on hold
        - A DataFrame of referral counts by hold reason
    """

    # Create sliced views of data for the on hold or pending statuses
    pending_df = referral_df.loc[(referral_df['Referral Status'] == 'Pending Acceptance')].copy()

    # Categorize the days pending
    r.calculate_age_category(pending_df, 'Age Category Pending Acceptance', 'Days until Referral Accepted')

    # Create sums of referrals by clinic and age category combinations
    age_distribution_df = pending_df.groupby(['Clinic', 'Age Category Pending Acceptance']) \
        .agg({'Referral Aged Yn': 'sum'}) \
        .rename(columns={'Referral Aged Yn': 'Referrals Aged'}) \
        .reset_index()
    
    # Create sums of referrals by clinic and sub-status combinations
    reason_distribution_df = pending_df.groupby(['Clinic', 'Referral Sub-Status']) \
        .agg({'Referral Aged Yn': 'sum'}) \
        .rename(columns={'Referral Aged Yn': 'Referrals Aged'}) \
        .reset_index()
    
    return age_distribution_df, reason_distribution_df  
# END calculate_pending_acceptance_measures


def get_counts_by_pending_acceptance_sub_status(clinic: str) -> DataFrame:
    """Returns a DataFrame of current pending acceptance referral counts by queue sub-status for the given clinic."""
    df = _acceptance_status_df.loc[(_acceptance_status_df['Clinic'] == clinic)].copy()
    df['Referral Sub-Status'] = (
        df['Referral Sub-Status'].str.replace('Call Patient to Schedule Appointment',
                                              'Call Patient to Schedule'))
    return df
# END get_counts_by_pending_acceptance_sub_status


def get_pending_acceptance_age_by_category(clinic: str, category: str) -> int:
    """Returns the count of pending acceptance referrals currently in an age category for the given clinic."""

    df = _acceptance_ages_df
    view = df.loc[(df['Clinic'] == clinic)
                  & (df['Age Category Pending Acceptance'] == category)]
    if len(view.index) == 0:
        return 0
    else:
        return view.at[min(view.index), 'Referrals Aged']
# END get_pending_acceptance_age_by_category


def _calculate_accepted_status_measures(referral_df: DataFrame) -> tuple[DataFrame, DataFrame]:
    """
    Calculates measures of referral time waiting for referrals currently accepted.
    :param referral_df: The master DataFrame of referral source data
    :return: Returns a tuple of two DataFrames
        - A DataFrame of referral counts by age category on hold
        - A DataFrame of referral counts by hold reason
    """

    # Create sliced views of data for the on hold or pending statuses
    pending_df = referral_df.loc[(referral_df['Referral Status'] == 'Accepted')].copy()

    # Categorize the days in accepted status.  If the referral is still in accepted status then it hasn't
    # been moved on to another status.  Using the age until patient seen as referral age. 
    r.calculate_age_category(pending_df, 'Age Category to Seen', 'Days until Patient Seen or Check In')

    # Create sums of referrals by clinic and age category combinations
    age_distribution_df = pending_df.groupby(['Clinic', 'Age Category to Seen']) \
        .agg({'Referral Aged Yn': 'sum'}) \
        .rename(columns={'Referral Aged Yn': 'Referrals Aged'}) \
        .reset_index()
    
    # Create sums of referrals by clinic and sub-status combinations
    reason_distribution_df = pending_df.groupby(['Clinic', 'Referral Sub-Status']) \
        .agg({'Referral Aged Yn': 'sum'}) \
        .rename(columns={'Referral Aged Yn': 'Referrals Aged'}) \
        .reset_index()
    
    return age_distribution_df, reason_distribution_df  
# END calculate_accepted_status_measures


def get_counts_by_accepted_referral_sub_status(clinic: str) -> DataFrame:
    """Returns a DataFrame of current accepted stats referral counts by queue sub-status for the given clinic."""
    df = _accepted_status_df.loc[(_accepted_status_df['Clinic'] == clinic)].copy()
    df['Referral Sub-Status'] = (
        df['Referral Sub-Status'].str.replace('Call Patient to Schedule Appointment',
                                              'Call Patient to Schedule'))
    return df
# End get_counts_by_accepted_referral_sub_status


def get_accepted_referral_age_by_category(clinic: str, category: str) -> int:
    """Returns the count of accepted referrals currently in an age category for the given clinic."""

    df = _accepted_ages_df
    view = df.loc[(df['Clinic'] == clinic)
                  & (df['Age Category to Seen'] == category)]
    if len(view.index) == 0:
        return 0
    else:
        return view.at[min(view.index), 'Referrals Aged']
# END get_accepted_referral_age_by_category


# MAIN

print('Calculating pending time measures...')

last_month = datetime.combine(_AS_OF_DATE.replace(day=1).date(), datetime.min.time()) + relativedelta(months=-1)

_on_hold_ages_df, _on_hold_reasons_df = _calculate_on_hold_measures(r.referral_df)
_reschedule_ages_df, _reschedule_status_df = _calculate_pending_reschedule_measures(r.referral_df)
_acceptance_ages_df, _acceptance_status_df = _calculate_pending_acceptance_measures(r.referral_df)
_accepted_ages_df, _accepted_status_df = _calculate_accepted_status_measures(r.referral_df)

print('Pending time measures calculated')
