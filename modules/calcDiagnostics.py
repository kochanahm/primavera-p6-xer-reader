import pandas as pd
import datetime
import config
import modules.calcStatistics
from flask import url_for

# Create Links Table and Count Diagnostics
def funcDiagnostics():
    # Join TASKPRED and TASK and CALENDAR tables
    df_task = config.my_filt_dataframes['TASK']
    df_taskpred = config.my_filt_dataframes['TASKPRED']
    df_calendar = config.my_filt_dataframes['CALENDAR']
    df_taskrsrc = config.my_filt_dataframes['TASKRSRC']
    df_taskpred_task = pd.merge(left=df_taskpred, right=df_task, left_on='task_id', right_on='task_id')
    df_task_2 = df_task[['task_id', 'task_code', 'task_name', 'clndr_id','status_code','task_type']]
    df_task_2.rename({'task_code': 'pred_task_code', 'task_name': 'pred_task_name', 'clndr_id': 'pred_clndr_id','status_code': 'pred_status_code','task_type': 'pred_task_type'}, axis=1, inplace=True)
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

    def funcFilterIncompletedTasks(df):
        df_IT = df.loc[(df['status_code'] != 'TK_Complete') & ((df['task_type'] == 'TT_Task') | (df['task_type'] == 'TT_Rsrc')), ['task_id','task_code', 'task_name', 'status_code','task_type']]
        return df_IT

    def funcFilterIncompletedTasks(df):
        df_IM = df.loc[(df['status_code'] != 'TK_Complete') & ((df['task_type'] == 'TT_FinMile') | (df['task_type'] == 'TT_Mile')), ['task_id','task_code', 'task_name', 'status_code','task_type']]
        return df_IM


    #--- MISSING PREDECESSORS ---
    ## Merge TASK and TASKPRED
    df_task_taskpred_mp = pd.merge(left=df_task, right=df_taskpred, left_on='task_id', right_on='task_id', how='left')
    ## Check null values for predecessor and if not null remove those rows
    df_task_taskpred_mp_2 = df_task_taskpred_mp[df_task_taskpred_mp['pred_task_id'].isna()].drop('pred_task_id', axis=1)
    ## Only get required fields. This is the dataframe for Missing Predecessor for ALL activities
    df_Missing_Pred = df_task_taskpred_mp_2[['task_id', 'task_code', 'task_name','status_code','task_type']]
    ## Filter for only Incompleted Tasks. This is the dataframe for Incompleted Tasks
    df_Missing_Pred_IT = funcFilterIncompletedTasks(df_Missing_Pred)
    ## Filter for only Incompleted Milestones. This is the dataframe for Incompleted Milestones
    df_Missing_Pred_IM = funcFilterIncompletedTasks(df_Missing_Pred)
    ## Count of All activities that have missing preds
    cnt_Missing_Pred = len(df_Missing_Pred)
    ## Count of Incomplete Tasks that have missing preds
    cnt_Missing_Pred_IT = len(df_Missing_Pred_IT)
    ## Count of Incomplete Milestones that have missing preds
    cnt_Missing_Pred_IM = len(df_Missing_Pred_IM)

    #--- MISSING SUCCESSORS ---
    ## Create a temporary dataframe of TASKPRED with only required fields
    df_taskpred_temp = df_taskpred[['task_id', 'pred_task_id']]
    ## Since task_id is available in both tables, before merging rename it in temp dataframe
    df_taskpred_temp.rename({'task_id': 'suc_task_id'},axis=1, inplace=True)
    ## Merge TASK and TASKPRED
    df_task_taskpred_ms = pd.merge(left=df_task, right=df_taskpred_temp, left_on='task_id', right_on='pred_task_id', how='left')
    ## Check null values for successors and if not null remove those rows
    df_task_taskpred_ms_2 = df_task_taskpred_ms[df_task_taskpred_ms['suc_task_id'].isna()].drop('suc_task_id', axis=1)
    ## Only get required fields. This is the dataframe for Missing Successsors for ALL activities
    df_Missing_Suc = df_task_taskpred_ms_2[['task_id', 'task_code', 'task_name','status_code','task_type']]
    ## Filter for only Incompleted Tasks. This is the dataframe for Incompleted Tasks
    df_Missing_Suc_IT = funcFilterIncompletedTasks(df_Missing_Suc)
    ## Filter for only Incompleted Milestones. This is the dataframe for Incompleted Milestones
    df_Missing_Suc_IM = funcFilterIncompletedTasks(df_Missing_Suc)
    ## Count of All activities that have missing successors
    cnt_Missing_Suc = len(df_Missing_Suc)
    ## Count of Incomplete Tasks that have missing successors
    cnt_Missing_Suc_IT = len(df_Missing_Suc_IT)
    ## Count of Incomplete Milestones that have missing successors
    cnt_Missing_Suc_IM = len(df_Missing_Suc_IM)

    def funcFilterIncompletedTaskLinks(df):
        df_IT = df.loc[(df['status_code'] != 'TK_Complete') & ((df['task_type'] == 'TT_Task') | (df['task_type'] == 'TT_Rsrc')), ['pred_task_code', 'pred_task_name', 'task_code', 'task_name', 'pred_type', 'lag_day_cnt','pred_status_code','status_code','pred_task_type','task_type']]
        return df_IT

    def funcFilterIncompletedMilestoneLinks(df):
        df_IM = df.loc[(df['status_code'] != 'TK_Complete') & ((df['task_type'] == 'TT_FinMile') | (df['task_type'] == 'TT_Mile')), ['pred_task_code', 'pred_task_name', 'task_code', 'task_name', 'pred_type', 'lag_day_cnt','pred_status_code','status_code','pred_task_type','task_type']]
        return df_IM
    
    #--- NEGATIVE LAGS ---
    ## Fiter negative lags for ALL activities regardles of activity status.
    df_Negative_Lags = df_taskpred_task_3.loc[(df_taskpred_task_3['lag_day_cnt'] < 0), ['pred_task_code', 'pred_task_name', 'task_code', 'task_name', 'pred_type', 'lag_day_cnt','pred_status_code','status_code','pred_task_type','task_type']]
    ## Filter negative floats dataframe for Incompleted Tasks 
    df_Negative_Lags_IT = funcFilterIncompletedTaskLinks(df_Negative_Lags)
    ## Filter negative floats dataframe for Incompleted Milestones 
    df_Negative_Lags_IM = funcFilterIncompletedMilestoneLinks(df_Negative_Lags)
    ## Count of ALL activities that have negative float regardless of activity status
    cnt_Negative_Lags = len(df_Negative_Lags)
    ## Count of Incompleted Tasks that have negative float
    cnt_Negative_Lags_IT = len(df_Negative_Lags_IT)
    ## Count of Incompleted Milestones that have negative float
    cnt_Negative_Lags_IM = len(df_Negative_Lags_IM)

    #--- POSITIVE LAGS ---
    ## Fiter Positive lags for ALL activities regardles of activity status.
    df_Positive_Lags = df_taskpred_task_3.loc[(df_taskpred_task_3['lag_day_cnt'] > 0), ['pred_task_code', 'pred_task_name', 'task_code', 'task_name', 'pred_type', 'lag_day_cnt','pred_status_code','status_code','pred_task_type','task_type']]
    ## Filter Positive floats dataframe for Incompleted Tasks 
    df_Positive_Lags_IT = funcFilterIncompletedTaskLinks(df_Positive_Lags)
    ## Filter Positive floats dataframe for Incompleted Milestones 
    df_Positive_Lags_IM = funcFilterIncompletedMilestoneLinks(df_Positive_Lags)
    ## Count of ALL activities that have Positive float regardless of activity status
    cnt_Positive_Lags = len(df_Positive_Lags)
    ## Count of Incompleted Tasks that have Positive float
    cnt_Positive_Lags_IT = len(df_Positive_Lags_IT)
    ## Count of Incompleted Milestones that have Positive float
    cnt_Positive_Lags_IM = len(df_Positive_Lags_IM)

    #--- FS LINKS ---
    ## Fiter FS links for ALL activities regardles of activity status.
    df_FS_links = df_taskpred_task_3.loc[(df_taskpred_task_3['pred_type'] == 'PR_FS'), ['pred_task_code', 'pred_task_name', 'task_code', 'task_name', 'pred_type', 'lag_day_cnt','pred_status_code','status_code','pred_task_type','task_type']]
    ## Filter FS Links dataframe for Incompleted Tasks 
    df_FS_links_IT = funcFilterIncompletedTaskLinks(df_FS_links)
    ## Filter FS Links dataframe for Incompleted Milestones 
    df_FS_links_IM = funcFilterIncompletedMilestoneLinks(df_FS_links)
    ## Count of ALL activities that have FS Links regardless of activity status
    cnt_FS_links = len(df_FS_links)
    ## Count of Incompleted Tasks that have FS Links
    cnt_FS_links_IT = len(df_FS_links_IT)
    ## Count of Incompleted Milestones that have FS Links
    cnt_FS_links_IM = len(df_FS_links_IM)

    #--- SS & FF LINKS ---
    ## Fiter SS_FF links for ALL activities regardles of activity status.
    df_SS_FF_links = df_taskpred_task_3.loc[(df_taskpred_task_3['pred_type'] == 'PR_SS') | (df_taskpred_task_3['pred_type'] == 'PR_FF'), ['pred_task_code', 'pred_task_name', 'task_code', 'task_name', 'pred_type', 'lag_day_cnt','pred_status_code','status_code','pred_task_type','task_type']]
    ## Filter SS_FF Links dataframe for Incompleted Tasks 
    df_SS_FF_links_IT = funcFilterIncompletedTaskLinks(df_SS_FF_links)
    ## Filter SS_FF  Links dataframe for Incompleted Milestones 
    df_SS_FF_links_IM = funcFilterIncompletedMilestoneLinks(df_SS_FF_links)
    ## Count of ALL activities that have SS_FF Links regardless of activity status
    cnt_SS_FF_links = len(df_SS_FF_links)
    ## Count of Incompleted Tasks that have SS_FF Links
    cnt_SS_FF_links_IT = len(df_SS_FF_links_IT)
    ## Count of Incompleted Milestones that have SS_FF Links
    cnt_SS_FF_links_IM = len(df_SS_FF_links_IM)

    #--- SF LINKS ---
    ## Fiter SF links for ALL activities regardles of activity status.
    df_SF_links = df_taskpred_task_3.loc[(df_taskpred_task_3['pred_type'] == 'PR_SF'), ['pred_task_code', 'pred_task_name', 'task_code', 'task_name', 'pred_type', 'lag_day_cnt','pred_status_code','status_code','pred_task_type','task_type']]
    ## Filter SF Links dataframe for Incompleted Tasks 
    df_SF_links_IT = funcFilterIncompletedTaskLinks(df_SF_links)
    ## Filter SF Links dataframe for Incompleted Milestones 
    df_SF_links_IM = funcFilterIncompletedMilestoneLinks(df_SF_links)
    ## Count of ALL activities that have SF Links regardless of activity status
    cnt_SF_links = len(df_SF_links)
    ## Count of Incompleted Tasks that have SF Links
    cnt_SF_links_IT = len(df_SF_links_IT)
    ## Count of Incompleted Milestones that have SF Links
    cnt_SF_links_IM = len(df_SF_links_IM)

    #--- HARD CONSTRAINTS ---
    ## Fiter hard constraints for ALL activities regardles of activity status.
    df_hard_const = df_task.loc[(df_task['cstr_type'] == 'CS_MANDFIN') | (df_task['cstr_type'] == 'CS_MANDSTART') | (df_task['cstr_type2'] == 'CS_MANDFIN') | (df_task['cstr_type2'] == 'CS_MANDSTART'),['task_id', 'task_code', 'task_name','status_code','task_type','cstr_type','cstr_type2']]
    ## Filter hard constraints dataframe for Incompleted Tasks 
    df_hard_const_IT = df_hard_const.loc[(df_hard_const['status_code'] != 'TK_Complete') & ((df_hard_const['task_type'] == 'TT_Task') | (df_hard_const['task_type'] == 'TT_Rsrc')), ['task_id','task_code', 'task_name', 'status_code','task_type','cstr_type','cstr_type2']]
    ## Filter hard constraints dataframe for Incompleted Milestones 
    df_hard_const_IM = df_hard_const.loc[(df_hard_const['status_code'] != 'TK_Complete') & ((df_hard_const['task_type'] == 'TT_FinMile') | (df_hard_const['task_type'] == 'TT_Mile')), ['task_id','task_code', 'task_name', 'status_code','task_type','cstr_type','cstr_type2']]
    ## Count of ALL activities that have hard constraints regardless of activity status
    cnt_hard_const = len(df_hard_const)
    ## Count of Incompleted Tasks that have hard constraints
    cnt_hard_const_IT = len(df_hard_const_IT)
    ## Count of Incompleted Milestones that have hard constraints
    cnt_hard_const_IM = len(df_hard_const_IM)

    #--- HIGH DURATIONS ---
    ## Merge TASK and CALENDAR tables since we need daily hours to calculate durations as days
    df_caltask = pd.merge(left=df_task, right=df_calendar, left_on='clndr_id', right_on='clndr_id')
    ## In case of nulls in durations, remove those rows
    df_caltask_2 = df_caltask.loc[(df_caltask['target_drtn_hr_cnt'].notnull()) & (df_caltask['remain_drtn_hr_cnt'].notnull())]
    ## Since all fields are string type, we need to convert to numeric to make calculation
    df_caltask_2[['target_drtn_hr_cnt','remain_drtn_hr_cnt', 'day_hr_cnt']] = df_caltask_2[['target_drtn_hr_cnt','remain_drtn_hr_cnt', 'day_hr_cnt']].apply(pd.to_numeric)
    ## Add 2 more columns to the dataframe for those calculated day durations 
    df_caltask_2['target_drtn_day_cnt'] = df_caltask_2['target_drtn_hr_cnt'].div(df_caltask_2['day_hr_cnt'], axis=0)
    df_caltask_2['remain_drtn_day_cnt'] = df_caltask_2['remain_drtn_hr_cnt'].div(df_caltask_2['day_hr_cnt'], axis=0)
    ## Filter for high original days regardless of activity status
    df_high_org_drt = df_caltask_2.loc[(df_caltask_2['target_drtn_day_cnt'] > 44),['task_id', 'task_code', 'task_name','status_code','task_type','target_drtn_day_cnt','remain_drtn_day_cnt']]
    ## Filter for high original days for incompleted tasks
    df_high_org_drt_IT = df_high_org_drt.loc[(df_high_org_drt['status_code'] != 'TK_Complete') & ((df_high_org_drt['task_type'] == 'TT_Task') | (df_high_org_drt['task_type'] == 'TT_Rsrc')),['task_id', 'task_code', 'task_name','status_code','task_type','target_drtn_day_cnt','remain_drtn_day_cnt']]
    ## Filter for high remaining days regardless of activity status
    df_high_rem_drt = df_caltask_2.loc[(df_caltask_2['remain_drtn_day_cnt'] > 44),['task_id', 'task_code', 'task_name','status_code','task_type','target_drtn_day_cnt','remain_drtn_day_cnt']]
    ## Filter for high remaining days for incompleted tasks
    df_high_rem_drt_IT = df_high_rem_drt.loc[(df_high_rem_drt['status_code'] != 'TK_Complete') & ((df_high_rem_drt['task_type'] == 'TT_Task') | (df_high_rem_drt['task_type'] == 'TT_Rsrc')),['task_id', 'task_code', 'task_name','status_code','task_type','target_drtn_day_cnt','remain_drtn_day_cnt']]
    ## Count of ALL activities that have high orginal durations regardless of activity status
    cnt_high_org_drt = len(df_high_org_drt)
    ## Count of Incompleted tasks that have high orginal durations
    cnt_high_org_drt_IT = len(df_high_org_drt_IT)
    ## Count of ALL activities that have high remaining durations regardless of activity status
    cnt_high_rem_drt = len(df_high_rem_drt)
    ## Count of Incompleted tasks that have high remaining durations
    cnt_high_rem_drt_IT = len(df_high_rem_drt_IT)

    #--- HIGH FLOATS ---
    ## In case of nulls in floats, remove those rows
    df_caltask_3 = df_caltask.loc[df_caltask['total_float_hr_cnt'].notnull()]
    ## Since all fields are string type, we need to convert to numeric to make calculation
    df_caltask_3[['total_float_hr_cnt', 'day_hr_cnt']] = df_caltask_3[['total_float_hr_cnt', 'day_hr_cnt']].apply(pd.to_numeric)
    ## Add 1 more column to the dataframe for those calculated day floats
    df_caltask_3['total_float_day_cnt'] = df_caltask_3['total_float_hr_cnt'].div(df_caltask_3['day_hr_cnt'], axis=0)
    ## Filter for high floats regardless of activity status
    df_High_Floats = df_caltask_3.loc[(df_caltask_3['total_float_day_cnt'] > 44), ['task_id', 'task_code', 'task_name', 'clndr_id','status_code','task_type','total_float_day_cnt']]
    ## Filter for high floats for incompleted tasks
    df_High_Floats_IT = df_High_Floats.loc[(df_High_Floats['status_code'] != 'TK_Complete') & ((df_High_Floats['task_type'] == 'TT_Task') | (df_High_Floats['task_type'] == 'TT_Rsrc')), ['task_id', 'task_code', 'task_name', 'clndr_id','status_code','task_type','total_float_day_cnt']]
    ## Filter for high floats for incompleted milestones
    df_High_Floats_IM = df_High_Floats.loc[(df_High_Floats['status_code'] != 'TK_Complete') & ((df_High_Floats['task_type'] == 'TT_FinMile') | (df_High_Floats['task_type'] == 'TT_Mile')), ['task_id', 'task_code', 'task_name', 'clndr_id','status_code','task_type','total_float_day_cnt']]
    ## Count of ALL activities that have high floats regardless of activity status
    cnt_High_Floats = len(df_High_Floats)
    ## Count of Incompleted tasks that have high floats
    cnt_High_Floats_IT = len(df_High_Floats_IT)
    ## Count of Incompleted milestones that have high floats
    cnt_High_Floats_IM = len(df_High_Floats_IM)

    #--- NEGATIVE FLOATS ---
    ## Filter for negative floats regardless of activity status
    df_Negative_Floats = df_caltask_3.loc[(df_caltask_3['total_float_day_cnt'] < 0), ['task_id', 'task_code', 'task_name', 'clndr_id','status_code','task_type','total_float_day_cnt']]
    ## Filter for negative floats for incompleted tasks
    df_Negative_Floats_IT = df_Negative_Floats.loc[(df_Negative_Floats['status_code'] != 'TK_Complete') & ((df_Negative_Floats['task_type'] == 'TT_Task') | (df_Negative_Floats['task_type'] == 'TT_Rsrc')), ['task_id', 'task_code', 'task_name', 'clndr_id','status_code','task_type','total_float_day_cnt']]
    ## Filter for negative floats for incompleted milestones
    df_Negative_Floats_IM = df_Negative_Floats.loc[(df_Negative_Floats['status_code'] != 'TK_Complete') & ((df_Negative_Floats['task_type'] == 'TT_FinMile') | (df_Negative_Floats['task_type'] == 'TT_Mile')), ['task_id', 'task_code', 'task_name', 'clndr_id','status_code','task_type','total_float_day_cnt']]
    ## Count of ALL activities that have Negative floats regardless of activity status
    cnt_Negative_Floats = len(df_Negative_Floats)
    ## Count of Incompleted tasks that have Negative floats
    cnt_Negative_Floats_IT = len(df_Negative_Floats_IT)
    ## Count of Incompleted milestones that have Negative floats
    cnt_Negative_Floats_IM = len(df_Negative_Floats_IM)

    #--- INVALID DATES ---
    ## Get only required fileds from TASK
    df_task_invdt = df_task[['task_id', 'task_code', 'task_name','status_code','task_type','act_start_date','act_end_date','early_start_date','early_end_date']]
    ## Convert strings to datetime format in order to compare with data date
    df_task_invdt['act_start_date'] = pd.to_datetime(df_task_invdt['act_start_date'], format='%d-%b-%Y %H:%M')
    df_task_invdt['act_end_date'] = pd.to_datetime(df_task_invdt['act_end_date'], format='%d-%b-%Y %H:%M')
    df_task_invdt['early_start_date'] = pd.to_datetime(df_task_invdt['early_start_date'], format='%d-%b-%Y %H:%M')
    df_task_invdt['early_end_date'] = pd.to_datetime(df_task_invdt['early_end_date'], format='%d-%b-%Y %H:%M')
    ## Get data date from other module
    prj_data_date = modules.calcStatistics.find_data_date()[2]
    ## Filter for tasks that have Invalid Actual Start dates
    df_task_ias = df_task_invdt.loc[(df_task_invdt['status_code'] != 'TK_NotStart') & ((df_task_invdt['task_type'] == 'TT_Task') | (df_task_invdt['task_type'] == 'TT_Rsrc')) & (df_task_invdt['act_start_date'] > prj_data_date),['task_id', 'task_code', 'task_name','status_code','task_type','act_start_date','act_end_date','early_start_date','early_end_date']]
    ## Filter for tasks that have Invalid Actual Finish dates
    df_task_iaf = df_task_invdt.loc[(df_task_invdt['status_code'] == 'TK_Complete') & ((df_task_invdt['task_type'] == 'TT_Task') | (df_task_invdt['task_type'] == 'TT_Rsrc')) & (df_task_invdt['act_end_date'] > prj_data_date),['task_id', 'task_code', 'task_name','status_code','task_type','act_start_date','act_end_date','early_start_date','early_end_date']]
    ## Filter for milestones that have Invalid Actual Start dates
    df_mil_ias = df_task_invdt.loc[(df_task_invdt['status_code'] == 'TK_Complete') & (df_task_invdt['task_type'] == 'TT_Mile') & (df_task_invdt['act_start_date'] > prj_data_date),['task_id', 'task_code', 'task_name','status_code','task_type','act_start_date','act_end_date','early_start_date','early_end_date']]
    ## Filter for milestones that have Invalid Actual Finish dates
    df_mil_iaf = df_task_invdt.loc[(df_task_invdt['status_code'] == 'TK_Complete') & (df_task_invdt['task_type'] == 'TT_FinMile') & (df_task_invdt['act_end_date'] > prj_data_date),['task_id', 'task_code', 'task_name','status_code','task_type','act_start_date','act_end_date','early_start_date','early_end_date']]
    ## Filter for tasks that have Invalid Forecast Start dates
    df_task_ifs = df_task_invdt.loc[(df_task_invdt['status_code'] != 'TK_Complete') & ((df_task_invdt['task_type'] == 'TT_Task') | (df_task_invdt['task_type'] == 'TT_Rsrc')) & (df_task_invdt['early_start_date'].notnull()) & (df_task_invdt['early_start_date'] < prj_data_date) ,['task_id', 'task_code', 'task_name','status_code','task_type','act_start_date','act_end_date','early_start_date','early_end_date']]
    ## Filter for tasks that have Invalid Forecast Finish dates
    df_task_iff = df_task_invdt.loc[(df_task_invdt['status_code'] != 'TK_Complete') & ((df_task_invdt['task_type'] == 'TT_Task') | (df_task_invdt['task_type'] == 'TT_Rsrc')) & (df_task_invdt['early_end_date'].notnull()) & (df_task_invdt['early_end_date'] < prj_data_date) ,['task_id', 'task_code', 'task_name','status_code','task_type','act_start_date','act_end_date','early_start_date','early_end_date']]
    ## Filter for milestones that have Invalid Forecast Start dates
    df_mil_ifs = df_task_invdt.loc[(df_task_invdt['status_code'] != 'TK_Complete') & (df_task_invdt['task_type'] == 'TT_Mile') & (df_task_invdt['early_start_date'].notnull()) & (df_task_invdt['early_start_date'] < prj_data_date) ,['task_id', 'task_code', 'task_name','status_code','task_type','act_start_date','act_end_date','early_start_date','early_end_date']]
    ## Filter for milestones that have Invalid Forecast Finish dates
    df_mil_iff = df_task_invdt.loc[(df_task_invdt['status_code'] != 'TK_Complete') & (df_task_invdt['task_type'] == 'TT_FinMile') & (df_task_invdt['early_end_date'].notnull()) & (df_task_invdt['early_end_date'] < prj_data_date) ,['task_id', 'task_code', 'task_name','status_code','task_type','act_start_date','act_end_date','early_start_date','early_end_date']]
    ## Count of tasks that have Invalid Actual Start dates
    cnt_task_ias = len(df_task_ias)
    ## Count of tasks that have Invalid Actual Finish dates
    cnt_task_iaf = len(df_task_iaf)
    ## Count of milestones that have Invalid Actual Start dates
    cnt_mil_ias = len(df_mil_ias)
    ## Count of milestones that have Invalid Actual Finish dates
    cnt_mil_iaf = len(df_mil_iaf)
    ## Count of tasks that have Invalid Forecast Start dates
    cnt_task_ifs = len(df_task_ifs)
    ## Count of tasks that have Invalid Forecast Finish dates
    cnt_task_iff = len(df_task_iff)
    ## Count of milestones that have Invalid Forecast Start dates
    cnt_mil_ifs = len(df_mil_ifs)
    ## Count of milestones that have Invalid Forecast Finish dates
    cnt_mil_iff = len(df_mil_iff)

    #--- NO ASSIGNED RESOURCE ---
    ## Get only required fields from TASKRSC
    #df_task_3 = df_task[['task_id', 'task_code', 'task_name', 'clndr_id','status_code','task_type']]
    df_taskrsrc_2 = df_taskrsrc[['taskrsrc_id','task_id']]
    ## Since task id available in both tables. NOTE: This might not be required test it later
    df_taskrsrc_2.rename({'task_id': 'rsrc_task_id'}, axis=1, inplace=True)
    ## Merge TASK and TASKRSRC
    df_task_taskrsrc = pd.merge(left=df_task, right=df_taskrsrc_2, left_on='task_id', right_on='rsrc_task_id')
    ## Filter for Incompleted tasks that have no assigned resources
    df_task_no_rsrc = df_task_taskrsrc.loc[(df_task_taskrsrc['status_code'] != 'TK_Complete') & ((df_task_taskrsrc['task_type'] == 'TT_Task') | (df_task_taskrsrc['task_type'] == 'TT_Rsrc')) & (df_task_taskrsrc['taskrsrc_id'].isnull()),['task_id', 'task_code', 'task_name','status_code','task_type','act_start_date','act_end_date','early_start_date','early_end_date']]
    ## Count of Incompleted tasks that have no assigned resources
    cnt_task_no_rsrc = len(df_task_no_rsrc)

    dict_Task_Metrics = [{'Metric': 'Missing Predecessors', 'Count': cnt_Missing_Pred_IT},
                       {'Metric': 'Missing Successors', 'Count': cnt_Missing_Suc_IT},
                       {'Metric': 'Negative Lags', 'Count': cnt_Negative_Lags_IT},
                       {'Metric': 'Positive Lags', 'Count': cnt_Positive_Lags_IT},
                       {'Metric': 'FS Links', 'Count': cnt_FS_links_IT},
                       {'Metric': 'SS-FF Links', 'Count': cnt_SS_FF_links_IT},
                       {'Metric': 'SF Links', 'Count': cnt_SF_links_IT},
                       {'Metric': 'Hard Constraints', 'Count': cnt_hard_const_IT},
                       {'Metric': 'High Floats', 'Count': cnt_High_Floats_IT},
                       {'Metric': 'Negative Floats', 'Count': cnt_Negative_Floats_IT},
                       {'Metric': 'High Original Durations','Count': cnt_high_org_drt_IT},
                       {'Metric': 'High Remaining Durations', 'Count': cnt_high_rem_drt_IT},
                       {'Metric': 'Invalid Actual Start', 'Count': cnt_task_ias},
                       {'Metric': 'Invalid Actual Finish', 'Count': cnt_task_iaf},
                       {'Metric': 'Invalid Forecast Start', 'Count': cnt_task_ifs},
                       {'Metric': 'Invalid Forecast Finish', 'Count': cnt_task_iff},
                       {'Metric': 'No Assigned Resource','Count': cnt_task_no_rsrc}]

    dict_Mil_Metrics = [{'Metric': 'Missing Predecessors', 'Count': cnt_Missing_Pred_IM},
                       {'Metric': 'Missing Successors', 'Count': cnt_Missing_Suc_IM},
                       {'Metric': 'Negative Lags', 'Count': cnt_Negative_Lags_IM},
                       {'Metric': 'Positive Lags', 'Count': cnt_Positive_Lags_IM},
                       {'Metric': 'FS Links', 'Count': cnt_FS_links_IM},
                       {'Metric': 'SS-FF Links', 'Count': cnt_SS_FF_links_IM},
                       {'Metric': 'SF Links', 'Count': cnt_SF_links_IM},
                       {'Metric': 'Hard Constraints', 'Count': cnt_hard_const_IM},
                       {'Metric': 'High Floats', 'Count': cnt_High_Floats_IM},
                       {'Metric': 'Negative Floats', 'Count': cnt_Negative_Floats_IM},
                       {'Metric': 'Invalid Actual Start', 'Count': cnt_mil_ias},
                       {'Metric': 'Invalid Actual Finish', 'Count': cnt_mil_iaf},
                       {'Metric': 'Invalid Forecast Start', 'Count': cnt_mil_ifs},
                       {'Metric': 'Invalid Forecast Finish', 'Count': cnt_mil_iff}]

    return dict_Task_Metrics, dict_Mil_Metrics