from pandas import DataFrame

from datetime import datetime
from dateutil.relativedelta import relativedelta

import model.Referrals as referrals

print('Loading holds and pending data set...')

# Effective as-of date for data
AS_OF_DATE = datetime(2023, 3, 1)


# On-Hold Measures


def get_on_hold_data(referral_df: DataFrame) -> tuple[DataFrame, DataFrame]:
    # Returns the on hold referral data.  All data represents referrals sent at 
    # any time in the past and still in an on-hold status. 
    #   referral_df: The pandas dataframe with the master set of referral data 
    #   returns: 1) a dataframe on hold age distributions, 2) a dataframe of hold reason distributions

    # Create sliced views of data for the on hold or pending statuses
    on_hold_df = referral_df.loc[(referral_df['Referral Status'] == 'On Hold')].copy()

    # Categorize the days on hold
    referrals.calculate_age_category(on_hold_df, 'Age Category On Hold', 'Days On Hold')

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
# End get_on_hold_data


def get_counts_by_on_hold_reason(clinic: str) -> DataFrame:
    # Returns the on hold reason counts for a clinic.  All data represents referrals sent at 
    # any time in the past and still in an on-hold status. 
    #   report_clinic: The name of a clinic to return data for
    #   returns: A dataframe of hold reason distributions
    return on_hold_reasons_df.loc[(on_hold_reasons_df['Clinic'] == clinic)]
# End get_counts_by_on_hold_reason


def get_on_hold_reason_list(clinic: str) -> list[str]:
    # Returns the on hold reasons used by a clinic as a list.  All data represents referrals sent at 
    # any time in the past and still in an on-hold status. 
    #   report_clinic: The name of a clinic to return data for
    #   returns: A list of hold reasons
    return on_hold_reasons_df.loc[(on_hold_reasons_df['Clinic'] == clinic)]['Reason for Hold'].tolist()
# End get_on_hold_reason_list


def get_on_hold_age_by_category(clinic: str, category: str) -> int:
    # Returns the on hold age count for a clinic and category combination 
    #   report_clinic: The name of the clinic being measured
    #   category: The category value to measure

    df = on_hold_ages_df
    view = df.loc[(df['Clinic'] == clinic)
                  & (df['Age Category On Hold'] == category)]
    if len(view.index) == 0:
        return 0
    else:
        return view.at[min(view.index), 'Referrals Aged']
# END get_on_hold_age_by_category


# Pending Reschedule Measures


def get_pending_reschedule_data(referral_df: DataFrame) -> tuple[DataFrame, DataFrame]:
    # Returns the pending reschedule referral data.  All data represents referrals sent at 
    # any time in the past and still in a pending reschedule status. 
    #   referral_df: The pandas dataframe with the master set of referral data 
    #   returns: 1) a dataframe on pending reschedule age distributions, 2) a dataframe of sub-status distributions

    # Create sliced views of data for the on hold or pending statuses
    pending_df = referral_df.loc[(referral_df['Referral Status'] == 'Pending Reschedule')].copy()

    # Categorize the days pending
    referrals.calculate_age_category(pending_df, 'Age Category Pending Reschedule', 'Days Pending Reschedule')

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
# End get_pending_reschedule_data


def get_counts_by_pending_reschedule_sub_status(clinic: str) -> DataFrame:
    # Returns the pending reschedule sub-status counts for a clinic.  All data represents referrals sent at 
    # any time in the past and still in a pending reschedule status. 
    #   report_clinic: The name of a clinic to return data for
    #   returns: A dataframe of sub-status distributions
    return reschedule_status_df.loc[(reschedule_status_df['Clinic'] == clinic)]
# End get_counts_by_pending_reschedule_sub_status


def get_pending_reschedule_sub_status_list(clinic: str) -> list[str]:
    # Returns the pending reschedule sub-statuses used by a clinic as a list.  All data represents referrals sent at 
    # any time in the past and still in a pending reschedule status. 
    #   report_clinic: The name of a clinic to return data for
    #   returns: A list of hold reasons
    return reschedule_status_df.loc[(reschedule_status_df['Clinic'] == clinic)]['Referral Sub-Status'].tolist()
# End get_pending_reschedule_sub_status_list


def get_pending_reschedule_age_by_category(clinic: str, category: str) -> int:
    # Returns the pending reschedule age count for a clinic and category combination 
    #   report_clinic: The name of the clinic being measured
    #   category: The category value to measure

    df = reschedule_ages_df
    view = df.loc[(df['Clinic'] == clinic)
                  & (df['Age Category Pending Reschedule'] == category)]
    if len(view.index) == 0:
        return 0
    else:
        return view.at[min(view.index), 'Referrals Aged']
# END get_pending_reschedule_age_by_category


# Pending Acceptance Measures


def get_pending_acceptance_data(referral_df: DataFrame) -> tuple[DataFrame, DataFrame]:
    # Returns the pending acceptance referral data.  All data represents referrals sent at 
    # any time in the past and still in a pending acceptance status. 
    #   referral_df: The pandas dataframe with the master set of referral data 
    #   returns: 1) a dataframe on pending acceptance age distributions, 2) a dataframe of sub-status distributions

    # Create sliced views of data for the on hold or pending statuses
    pending_df = referral_df.loc[(referral_df['Referral Status'] == 'Pending Acceptance')].copy()

    # Categorize the days pending
    referrals.calculate_age_category(pending_df, 'Age Category Pending Acceptance', 'Days until Referral Accepted')

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
# End get_pending_acceptance_data


def get_counts_by_pending_acceptance_sub_status(clinic: str) -> DataFrame:
    # Returns the pending acceptance sub-status counts for a clinic.  All data represents referrals sent at 
    # any time in the past and still in a pending acceptance status. 
    #   report_clinic: The name of a clinic to return data for
    #   returns: A dataframe of sub-status distributions
    return acceptance_status_df.loc[(acceptance_status_df['Clinic'] == clinic)]
# End get_counts_by_pending_acceptance_sub_status


def get_pending_acceptance_sub_status_list(clinic: str) -> list[str]:
    # Returns the pending acceptance sub-statuses used by a clinic as a list.  All data represents referrals sent at 
    # any time in the past and still in a pending acceptance status. 
    #   report_clinic: The name of a clinic to return data for
    #   returns: A list of sub-statuses
    return acceptance_status_df.loc[(acceptance_status_df['Clinic'] == clinic)]['Referral Sub-Status'].tolist()
# End get_pending_acceptance_sub_status_list


def get_pending_acceptance_age_by_category(clinic: str, category: str) -> int:
    # Returns the pending acceptance age count for a clinic and category combination 
    #   report_clinic: The name of the clinic being measured
    #   category: The category value to measure

    df = acceptance_ages_df
    view = df.loc[(df['Clinic'] == clinic)
                  & (df['Age Category Pending Acceptance'] == category)]
    if len(view.index) == 0:
        return 0
    else:
        return view.at[min(view.index), 'Referrals Aged']
# END get_pending_acceptance_age_by_category


# Accepted Status Measures


def get_accepted_status_data(referral_df: DataFrame) -> tuple[DataFrame, DataFrame]:
    # Returns the accepted referral data.  All data represents referrals sent at 
    # any time in the past and still in accepted status. 
    #   referral_df: The pandas dataframe with the master set of referral data 
    #   returns: 1) a dataframe on pending acceptance age distributions, 2) a dataframe of sub-status distributions

    # Create sliced views of data for the on hold or pending statuses
    pending_df = referral_df.loc[(referral_df['Referral Status'] == 'Accepted')].copy()

    # Categorize the days in accepted status.  If the referral is still in accepted status then it hasn't
    # been moved on to another status.  Using the age until patient seen as referral age. 
    referrals.calculate_age_category(pending_df, 'Age Category to Seen', 'Days until Patient Seen or Check In')

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
# End get_accepted_status_data


def get_counts_by_accepted_referral_sub_status(clinic: str) -> DataFrame:
    # Returns the accepted sub-status counts for a clinic.  All data represents referrals sent at 
    # any time in the past and still in an accepted status. 
    #   report_clinic: The name of a clinic to return data for
    #   returns: A dataframe of sub-status distributions
    return accepted_status_df.loc[(accepted_status_df['Clinic'] == clinic)]
# End get_counts_by_accepted_referral_sub_status


def get_accepted_referral_sub_status_list(clinic: str) -> list[str]:
    # Returns the accepted sub-statuses used by a clinic as a list.  All data represents referrals sent at 
    # any time in the past and still in an accepted status. 
    #   report_clinic: The name of a clinic to return data for
    #   returns: A list of sub-statuses
    return accepted_status_df.loc[(accepted_status_df['Clinic'] == clinic)]['Referral Sub-Status'].tolist()
# End get_accepted_referral_sub_status_list


def get_accepted_referral_age_by_category(clinic: str, category: str) -> int:
    # Returns the accepted age count for a clinic and category combination 
    #   report_clinic: The name of the clinic being measured
    #   category: The category value to measure

    df = accepted_ages_df
    view = df.loc[(df['Clinic'] == clinic)
                  & (df['Age Category to Seen'] == category)]
    if len(view.index) == 0:
        return 0
    else:
        return view.at[min(view.index), 'Referrals Aged']
# END get_accepted_referral_age_by_category


# MAIN


last_month = datetime.combine(AS_OF_DATE.replace(day=1).date(), datetime.min.time()) + relativedelta(months=-1)

on_hold_ages_df, on_hold_reasons_df = get_on_hold_data(referrals.referral_df)
reschedule_ages_df, reschedule_status_df = get_pending_reschedule_data(referrals.referral_df)
acceptance_ages_df, acceptance_status_df = get_pending_acceptance_data(referrals.referral_df)
accepted_ages_df, accepted_status_df = get_accepted_status_data(referrals.referral_df)

print('Holds and pending loaded')
