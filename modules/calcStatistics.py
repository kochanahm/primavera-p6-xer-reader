import pandas as pd
import datetime
import config


# Filter original my_dataframes by selectd proj id and store it in my_filt_dataframes dict
def update_my_filt_dataframes(selected_project_id):
    for tblName, myDf in config.my_dataframes.items():
        if 'proj_id' in myDf.columns:
            df_new = myDf.loc[(myDf['proj_id'] == selected_project_id) | (myDf['proj_id'].isnull())]
            config.my_filt_dataframes[tblName] = df_new
        else:
            config.my_filt_dataframes[tblName] = myDf


# Find data date
def find_data_date():
    df_project = config.my_filt_dataframes['PROJECT']
    prj_data_date_str = df_project.iloc[0]['last_recalc_date']
    prj_data_date_obj = datetime.datetime.strptime(prj_data_date_str, '%Y-%m-%d %H:%M')
    prj_data_date = prj_data_date_obj.strftime('%d-%b-%Y')
    prj_data_date_hr = prj_data_date_obj.strftime('%H:%M')
    return prj_data_date, prj_data_date_hr


# Find project start date
def find_proj_start_date():
    df_task = config.my_filt_dataframes['TASK']
    df_task['act_start_date'] = pd.to_datetime(df_task['act_start_date'])
    df_micro1 = df_task.loc[(df_task['task_type'] == 'TT_Task') &
                            (df_task['act_start_date'].notnull()) &
                            ((df_task['status_code'] == 'TK_Complete') |
                             (df_task['status_code'] == 'TK_Active')), ['act_start_date']]
    prj_start_date_obj1 = df_micro1['act_start_date'].min()
    df_task['early_start_date'] = pd.to_datetime(df_task['early_start_date'])
    df_micro2 = df_task.loc[(df_task['task_type'] == 'TT_Task') &
                            (df_task['early_start_date'].notnull()) &
                            (df_task['status_code'] == 'TK_NotStart'), ['early_start_date']]
    prj_start_date_obj2 = df_micro2['early_start_date'].min()
    prj_start_date_obj = min([prj_start_date_obj1, prj_start_date_obj2])
    prj_start_date = prj_start_date_obj.strftime('%d-%b-%Y')
    prj_start_date_hr = prj_start_date_obj.strftime('%H:%M')
    return prj_start_date, prj_start_date_hr


# Find project end date
def find_proj_end_date():
    df_task = config.my_filt_dataframes['TASK']
    df_task['act_end_date'] = pd.to_datetime(df_task['act_end_date'])
    df_micro3 = df_task.loc[(df_task['task_type'] == 'TT_Task') &
                            (df_task['act_end_date'].notnull()) &
                            (df_task['status_code'] == 'TK_Complete'), ['act_end_date']]
    prj_end_date_obj1 = df_micro3['act_end_date'].max()
    df_task['early_end_date'] = pd.to_datetime(df_task['early_end_date'])
    df_micro4 = df_task.loc[(df_task['task_type'] == 'TT_Task') &
                            (df_task['early_end_date'].notnull()) &
                            ((df_task['status_code'] == 'TK_NotStart') |
                             (df_task['status_code'] == 'TK_Active')), ['early_end_date']]
    prj_end_date_obj2 = df_micro4['early_end_date'].max()
    prj_end_date_obj = max([prj_end_date_obj1, prj_end_date_obj2])
    prj_end_date = prj_end_date_obj.strftime('%d-%b-%Y')
    prj_end_date_hr = prj_end_date_obj.strftime('%H:%M')
    return prj_end_date, prj_end_date_hr


# Create Task Status Table
def create_task_status_table():
    df_task = config.my_filt_dataframes['TASK']
    cnt_completed_tasks = len(df_task.loc[(df_task['status_code'] == 'TK_Complete'), ['task_id']])
    cnt_inprogress_tasks = len(df_task.loc[(df_task['status_code'] == 'TK_Active'), ['task_id']])
    cnt_notstarted_tasks = len(df_task.loc[(df_task['status_code'] == 'TK_NotStart'), ['task_id']])
    dict_task_status = [{'Status': 'Completed', 'Count': cnt_completed_tasks},
                        {'Status': 'In Progress', 'Count': cnt_inprogress_tasks},
                        {'Status': 'Not Started', 'Count': cnt_notstarted_tasks}]
    return dict_task_status


# Create Task Type Table
def create_task_type_table():
    df_task = config.my_filt_dataframes['TASK']
    cnt_task_dependent = len(df_task.loc[(df_task['task_type'] == 'TT_Task'), ['task_type']])
    cnt_wbs_summary = len(df_task.loc[(df_task['task_type'] == 'TT_WBS'), ['task_type']])
    cnt_loe = len(df_task.loc[(df_task['task_type'] == 'TT_LOE'), ['task_type']])
    cnt_start_milestone = len(df_task.loc[(df_task['task_type'] == 'TT_Mile'), ['task_type']])
    cnt_finish_milestone = len(df_task.loc[(df_task['task_type'] == 'TT_FinMile'), ['task_type']])
    cnt_resource_dependent = len(df_task.loc[(df_task['task_type'] == 'TT_Rsrc'), ['task_type']])
    dict_task_types = [{'Type': 'Task Dependent', 'Count': cnt_task_dependent},
                       {'Type': 'Start Milestone', 'Count': cnt_start_milestone},
                       {'Type': 'Finish Milestone', 'Count': cnt_finish_milestone},
                       {'Type': 'WBS Summary', 'Count': cnt_wbs_summary},
                       {'Type': 'Level of Effort', 'Count': cnt_loe},
                       {'Type': 'Resource Dependent', 'Count': cnt_resource_dependent}]
    return dict_task_types


# Create Cost Table
def create_cost_table():
    df_taskrsrc = config.my_filt_dataframes['TASKRSRC']
    df_taskrsrc[['target_cost', 'act_reg_cost', 'remain_cost']] = df_taskrsrc[
        ['target_cost', 'act_reg_cost', 'remain_cost']].apply(pd.to_numeric)
    sm_budg_cost = float(df_taskrsrc['target_cost'].sum())
    sm_act_cost = float(df_taskrsrc['act_reg_cost'].sum())
    sm_rem_cost = float(df_taskrsrc['remain_cost'].sum())
    sm_atc_cost = sm_act_cost + sm_rem_cost
    dict_sm_costs = [{'Title': 'Budgeted', 'Cost': sm_budg_cost},
                     {'Title': 'Actual', 'Cost': sm_act_cost},
                     {'Title': 'Remaining', 'Cost': sm_rem_cost},
                     {'Title': 'At Completion', 'Cost': sm_atc_cost}]
    return dict_sm_costs


# Create Labour Units Table
def create_labunits_table():
    df_task = config.my_filt_dataframes['TASK']
    df_task[['target_work_qty', 'act_work_qty', 'remain_work_qty']] = df_task[
        ['target_work_qty', 'act_work_qty', 'remain_work_qty']].apply(pd.to_numeric)
    sm_budg_labour = float(df_task['target_work_qty'].sum())
    sm_act_labour = float(df_task['act_work_qty'].sum())
    sm_rem_labour = float(df_task['remain_work_qty'].sum())
    sm_atc_labour = sm_act_labour + sm_rem_labour
    dict_sm_labours = [{'Title': 'Budgeted', 'Labour_Units': sm_budg_labour},
                       {'Title': 'Actual', 'Labour_Units': sm_act_labour},
                       {'Title': 'Remaining', 'Labour_Units': sm_rem_labour},
                       {'Title': 'At Completion', 'Labour_Units': sm_atc_labour}]
    return dict_sm_labours


# Create Non-labour Units Table
def create_nonlabunits_table():
    df_task = config.my_filt_dataframes['TASK']
    df_task[['target_equip_qty', 'act_equip_qty', 'remain_equip_qty']] = df_task[
        ['target_equip_qty', 'act_equip_qty', 'remain_equip_qty']].apply(pd.to_numeric)
    sm_budg_nonlabour = float(df_task['target_equip_qty'].sum())
    sm_act_nonlabour = float(df_task['act_equip_qty'].sum())
    sm_rem_nonlabour = float(df_task['remain_equip_qty'].sum())
    sm_atc_nonlabour = sm_act_nonlabour + sm_rem_nonlabour
    dict_sm_nonlabours = [{'Title': 'Budgeted', 'Nonlabour_Units': sm_budg_nonlabour},
                          {'Title': 'Actual', 'Nonlabour_Units': sm_act_nonlabour},
                          {'Title': 'Remaining', 'Nonlabour_Units': sm_rem_nonlabour},
                          {'Title': 'At Completion', 'Nonlabour_Units': sm_atc_nonlabour}]
    return dict_sm_nonlabours


# Create Float Metrics Table and Float Distribution Chart
def create_float_table():
    # Join Calendar and Task tables to get daily hours and convert hours to days
    df_task = config.my_filt_dataframes['TASK']
    df_calendar = config.my_filt_dataframes['CALENDAR']
    cnt_no_float = len(df_task.loc[(df_task['total_float_hr_cnt'].isnull()), ['task_id']])
    df_caltask = pd.merge(left=df_task, right=df_calendar, left_on='clndr_id', right_on='clndr_id')
    df_caltask_2 = df_caltask.loc[df_caltask['total_float_hr_cnt'].notnull()]
    df_caltask_2[['total_float_hr_cnt', 'day_hr_cnt']] = df_caltask_2[['total_float_hr_cnt', 'day_hr_cnt']].apply(
        pd.to_numeric)
    # Calculate Table Data
    df_caltask_2['total_float_day_cnt'] = df_caltask_2['total_float_hr_cnt'].div(df_caltask_2['day_hr_cnt'], axis=0)
    cnt_negative_float = len(df_caltask_2.loc[(df_caltask_2['total_float_day_cnt'] < 0), ['task_id']])
    cnt_critical_float = len(df_caltask_2.loc[(df_caltask_2['total_float_day_cnt'] == 0), ['task_id']])
    cnt_0_44_float = len(df_caltask_2.loc[
                             (df_caltask_2['total_float_day_cnt'] > 0) & (df_caltask_2['total_float_day_cnt'] < 44), [
                                 'task_id']])
    cnt_greater44_float = len(df_caltask_2.loc[(df_caltask_2['total_float_day_cnt'] > 44), ['task_id']])
    dict_float_metrics = [{'Title': 'No Float (Completed Tasks)', 'Count': cnt_no_float},
                          {'Title': 'Negative Float', 'Count': cnt_negative_float},
                          {'Title': 'Zero Float', 'Count': cnt_critical_float},
                          {'Title': 'Float 0 to 44 Days', 'Count': cnt_0_44_float},
                          {'Title': 'Float > 44 Days', 'Count': cnt_greater44_float}]
    # Calculate Chart Data
    cnt_min_sml30 = len(df_caltask_2.loc[(df_caltask_2['total_float_day_cnt'] < (-30)), ['task_id']])
    cnt_min_20_30 = len(df_caltask_2.loc[(df_caltask_2['total_float_day_cnt'] < (-20)) &
                                         (df_caltask_2['total_float_day_cnt'] >= (-30)), ['task_id']])
    cnt_min_10_20 = len(df_caltask_2.loc[(df_caltask_2['total_float_day_cnt'] < (-10)) &
                                         (df_caltask_2['total_float_day_cnt'] >= (-20)), ['task_id']])
    cnt_min_5_10 = len(df_caltask_2.loc[(df_caltask_2['total_float_day_cnt'] < (-5)) &
                                         (df_caltask_2['total_float_day_cnt'] >= (-10)), ['task_id']])
    cnt_min_0_5 = len(df_caltask_2.loc[(df_caltask_2['total_float_day_cnt'] < 0) &
                                         (df_caltask_2['total_float_day_cnt'] >= (-5)), ['task_id']])
    cnt_pls_0_5 = len(df_caltask_2.loc[(df_caltask_2['total_float_day_cnt'] > 0) &
                                         (df_caltask_2['total_float_day_cnt'] <= 5), ['task_id']])
    cnt_pls_5_10 = len(df_caltask_2.loc[(df_caltask_2['total_float_day_cnt'] > 5) &
                                         (df_caltask_2['total_float_day_cnt'] <= 10), ['task_id']])
    cnt_pls_10_20 = len(df_caltask_2.loc[(df_caltask_2['total_float_day_cnt'] > 10) &
                                         (df_caltask_2['total_float_day_cnt'] <= 20), ['task_id']])
    cnt_pls_20_30 = len(df_caltask_2.loc[(df_caltask_2['total_float_day_cnt'] > 20) &
                                         (df_caltask_2['total_float_day_cnt'] <= 30), ['task_id']])
    cnt_pls_30_44 = len(df_caltask_2.loc[(df_caltask_2['total_float_day_cnt'] > 30) &
                                         (df_caltask_2['total_float_day_cnt'] <= 44), ['task_id']])
    cnt_pls_44_100 = len(df_caltask_2.loc[(df_caltask_2['total_float_day_cnt'] > 44) &
                                         (df_caltask_2['total_float_day_cnt'] <= 100), ['task_id']])
    cnt_pls_grt100 = len(df_caltask_2.loc[(df_caltask_2['total_float_day_cnt'] > 100), ['task_id']])
    dict_float_dist = [{'FloatRange': '< -30', 'Count': cnt_min_sml30},
                       {'FloatRange': '-21 to -30', 'Count': cnt_min_20_30},
                       {'FloatRange': '-11 to -20', 'Count': cnt_min_10_20},
                       {'FloatRange': '-6 to -10', 'Count': cnt_min_5_10},
                       {'FloatRange': '-1 to -5', 'Count': cnt_min_0_5},
                       {'FloatRange': '0', 'Count': cnt_critical_float},
                       {'FloatRange': '1 to 5', 'Count': cnt_pls_0_5},
                       {'FloatRange': '6 to 10', 'Count': cnt_pls_5_10},
                       {'FloatRange': '11 to 20', 'Count': cnt_pls_10_20},
                       {'FloatRange': '21 to 30', 'Count': cnt_pls_20_30},
                       {'FloatRange': '31 to 44', 'Count': cnt_pls_30_44},
                       {'FloatRange': '45 to 100', 'Count': cnt_pls_44_100},
                       {'FloatRange': '> 100', 'Count': cnt_pls_grt100}]

    return dict_float_metrics, dict_float_dist
