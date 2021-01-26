import pandas as pd
import datetime
import config

# Create Links Table and Count Diagnostics
def count_link_types():
    # Join TASKPRED and TASK and CALENDAR tables
    df_task = config.my_filt_dataframes['TASK']
    df_taskpred = config.my_filt_dataframes['TASKPRED']
    df_calendar = config.my_filt_dataframes['CALENDAR']
    df_taskpred_task = pd.merge(left=df_taskpred, right=df_task, left_on='task_id', right_on='task_id')
    df_task_2 = df_task[['task_id', 'task_code', 'task_name', 'clndr_id']]
    df_task_2.rename({'task_code': 'pred_task_code', 'task_name': 'pred_task_name', 'clndr_id': 'pred_clndr_id'}, axis=1, inplace=True)
    df_taskpred_task_2 = pd.merge(left=df_taskpred_task, right=df_task_2, left_on='pred_task_id', right_on='task_id')

    def check_lag_calendar():
        if 'SCHEDOPTIONS' in config.my_filt_dataframes.keys():
            df_schedoptions = config.my_filt_dataframes['SCHEDOPTIONS']
            rcal_Used = df_schedoptions.iloc[0]['sched_calendar_on_relationship_lag'] # Find calendar for scheduling lags

            if rcal_Used == 'rcal_Successor':
                df_taskpred_task_2_cal = pd.merge(left=df_taskpred_task_2, right=df_calendar, left_on='clndr_id',
                                              right_on='clndr_id')
                df_taskpred_task_2_cal[['lag_hr_cnt', 'day_hr_cnt']] = df_taskpred_task_2_cal[
                    ['lag_hr_cnt', 'day_hr_cnt']].apply(pd.to_numeric)
                df_taskpred_task_2_cal['lag_day_cnt'] = df_taskpred_task_2_cal['lag_hr_cnt'].div(df_taskpred_task_2_cal['day_hr_cnt'],
                                                                                             axis=0)
                return df_taskpred_task_2_cal
            elif rcal_Used == 'rcal_Predecessor':
                df_taskpred_task_2_cal = pd.merge(left=df_taskpred_task_2, right=df_calendar, left_on='pred_clndr_id',
                                                  right_on='clndr_id')
                df_taskpred_task_2_cal[['lag_hr_cnt', 'day_hr_cnt']] = df_taskpred_task_2_cal[
                    ['lag_hr_cnt', 'day_hr_cnt']].apply(pd.to_numeric)
                df_taskpred_task_2_cal['lag_day_cnt'] = df_taskpred_task_2_cal['lag_hr_cnt'].div(df_taskpred_task_2_cal['day_hr_cnt'],
                                                                                             axis=0)
                return df_taskpred_task_2_cal
            elif rcal_Used == 'rcal_24Hour':
                df_taskpred_task_2[['lag_hr_cnt']] = df_taskpred_task_2[['lag_hr_cnt']].apply(pd.to_numeric)
                df_taskpred_task_2['lag_day_cnt'] = df_taskpred_task_2['lag_hr_cnt'] / 24
                return df_taskpred_task_2
            elif rcal_Used == 'rcal_ProjDefault':
                df_calendar_def = df_calendar.loc[(df_calendar['default_flag'] == 'Y'), ['day_hr_cnt']]
                if len(df_calendar_def) > 0:
                    def_day_hours_str = df_calendar_def.iloc[0]['day_hr_cnt']
                    def_day_hours = float(def_day_hours_str)
                    df_taskpred_task_2[['lag_hr_cnt']] = df_taskpred_task_2[['lag_hr_cnt']].apply(pd.to_numeric)
                    df_taskpred_task_2['lag_day_cnt'] = df_taskpred_task_2['lag_hr_cnt'] / def_day_hours
                    return df_taskpred_task_2
                else:
                    df_taskpred_task_2[['lag_hr_cnt']] = df_taskpred_task_2[['lag_hr_cnt']].apply(pd.to_numeric)
                    df_taskpred_task_2['lag_day_cnt'] = df_taskpred_task_2['lag_hr_cnt'] / 8
                    return df_taskpred_task_2
            else:
                df_taskpred_task_2['lag_day_cnt'] = df_taskpred_task_2['lag_hr_cnt'] / 8
                return df_taskpred_task_2

    # df_taskpred_task_3 = df_taskpred_task_2.loc[(df_taskpred_task_2['status_code'] != 'TK_Complete') &
    #                                          ((df_taskpred_task_2['task_type'] == 'TT_Task') |
    #                                          (df_taskpred_task_2['task_type'] == 'TT_Rsrc'))]

    df_taskpred_task_3 = check_lag_calendar()
    df_All_links = df_taskpred_task_3[['pred_task_code', 'pred_task_name', 'task_code', 'task_name', 'pred_type', 'lag_day_cnt']]

    # Count Missing Predecessors and create table
    df_task_taskpred_mp = pd.merge(left=df_task, right=df_taskpred, left_on='task_id', right_on='task_id', how='left')
    df_task_taskpred_mp_2 = df_task_taskpred_mp[df_task_taskpred_mp['pred_task_id'].isna()].drop('pred_task_id', axis=1)
    df_Missing_Pred = df_task_taskpred_mp_2[['task_id', 'task_code', 'task_name']]
    cnt_Missing_Pred = len(df_Missing_Pred)

    # Count Missing Successors and create table
    df_taskpred_temp = df_taskpred[['task_id', 'pred_task_id']]
    df_taskpred_temp.rename({'task_id': 'suc_task_id'},axis=1, inplace=True)
    df_task_taskpred_ms = pd.merge(left=df_task, right=df_taskpred_temp, left_on='task_id', right_on='pred_task_id', how='left')
    df_task_taskpred_ms_2 = df_task_taskpred_ms[df_task_taskpred_ms['suc_task_id'].isna()].drop('suc_task_id', axis=1)
    df_Missing_Suc = df_task_taskpred_ms_2[['task_id', 'task_code', 'task_name']]
    cnt_Missing_Suc = len(df_Missing_Suc)

    # Count Negative Lags and create table
    df_Negative_Lags = df_taskpred_task_3.loc[(df_taskpred_task_3['lag_day_cnt'] < 0), ['pred_task_code', 'pred_task_name', 'task_code', 'task_name', 'pred_type', 'lag_day_cnt']]
    cnt_Negative_Lags = len(df_Negative_Lags)

    # Count Positive Lags and create table
    df_Positive_Lags = df_taskpred_task_3.loc[(df_taskpred_task_3['lag_day_cnt'] > 0), ['pred_task_code', 'pred_task_name', 'task_code', 'task_name', 'pred_type', 'lag_day_cnt']]
    cnt_Positive_Lags = len(df_Positive_Lags)

    # Count FS Links and create table
    df_FS_links = df_taskpred_task_3.loc[(df_taskpred_task_3['pred_type'] == 'PR_FS'), ['pred_task_code', 'pred_task_name', 'task_code', 'task_name', 'pred_type', 'lag_day_cnt']]
    cnt_FS_links = len(df_FS_links)

    # Count SS-FF Links and create table
    df_SS_FF_links = df_taskpred_task_3.loc[(df_taskpred_task_3['pred_type'] == 'PR_SS') | (df_taskpred_task_3['pred_type'] == 'PR_FF'), ['pred_task_code', 'pred_task_name', 'task_code', 'task_name', 'pred_type', 'lag_day_cnt']]
    cnt_SS_FF_links = len(df_SS_FF_links)

    # Count SF Links and create table
    df_SF_links = df_taskpred_task_3.loc[(df_taskpred_task_3['pred_type'] == 'PR_SF'), ['pred_task_code', 'pred_task_name', 'task_code', 'task_name', 'pred_type', 'lag_day_cnt']]
    cnt_SF_links = len(df_SF_links)

    dict_FS_links = df_Missing_Suc.to_dict(orient='records')

    return dict_FS_links