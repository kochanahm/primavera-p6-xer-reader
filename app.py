import os
import json
import pandas as pd
import datetime
from flask import Flask, render_template, request, redirect, abort, flash, url_for, jsonify,send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
import modules.loadXer
import modules.calcStatistics
import modules.calcDiagnostics
import config

app = Flask(__name__, static_url_path="/static", static_folder="/static")

list_Diagnostic_Results = []


@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico')

@app.route('/navpanel', methods=['POST', 'GET'])
def navpanel():

    # Get selected project id from project selection page
    selected_project_id = str(request.form.get('project_selector'))

    modules.calcStatistics.update_my_filt_dataframes(selected_project_id) # update dataframes based on selected project id
    modules.calcStatistics.checkTableExist() #check which tables exist in XER

    prj_data_date = modules.calcStatistics.find_data_date()[0]
    prj_data_date_hr = modules.calcStatistics.find_data_date()[1]
    prj_start_date = modules.calcStatistics.find_proj_start_date()[0]
    prj_start_date_hr = modules.calcStatistics.find_proj_start_date()[1]
    prj_end_date = modules.calcStatistics.find_proj_end_date()[0]
    prj_end_date_hr = modules.calcStatistics.find_proj_end_date()[1]
    dict_task_status = modules.calcStatistics.create_task_status_table()
    dict_task_types = modules.calcStatistics.create_task_type_table()
    dict_sm_costs = modules.calcStatistics.create_cost_table()
    dict_sm_labours = modules.calcStatistics.create_labunits_table()
    dict_sm_nonlabours = modules.calcStatistics.create_nonlabunits_table()
    dict_float_metrics = modules.calcStatistics.create_float_table()[0]
    dict_float_dist = modules.calcStatistics.create_float_table()[1]
    list_temp_diagnostics = modules.calcDiagnostics.funcDiagnostics()
    list_Diagnostic_Results.extend(list_temp_diagnostics)
    dict_Task_Metrics = list_temp_diagnostics[0]
    dict_Mil_Metrics = list_temp_diagnostics[1]

    if (dict_sm_costs[3]['Cost']) == 0:
        my_cost_progress = [0, 100]
    else:
        my_cost_progress = [(dict_sm_costs[1]['Cost'] / (dict_sm_costs[3]['Cost']))*100,
                            (dict_sm_costs[2]['Cost'] / (dict_sm_costs[3]['Cost']))*100]

    if (dict_sm_labours[3]['Labour_Units']) == 0:
        my_labour_progress = [0, 100]
    else:
        my_labour_progress = [(dict_sm_labours[1]['Labour_Units'] / (dict_sm_labours[3]['Labour_Units']))*100,
                              (dict_sm_labours[2]['Labour_Units'] / (dict_sm_labours[3]['Labour_Units']))*100]

    if (dict_sm_nonlabours[3]['Nonlabour_Units']) == 0:
        my_nonlabour_progress = [0, 100]
    else:
        my_nonlabour_progress = [(dict_sm_nonlabours[1]['Nonlabour_Units'] / (dict_sm_nonlabours[3]['Nonlabour_Units']))*100,
                                 (dict_sm_nonlabours[2]['Nonlabour_Units'] / (dict_sm_nonlabours[3]['Nonlabour_Units']))*100]

    return render_template('navpanel.html', 
    prj_data_date=prj_data_date,
    prj_start_date=prj_start_date,
    prj_end_date=prj_end_date,
    prj_data_date_hr=prj_data_date_hr,
    prj_start_date_hr=prj_start_date_hr,
    prj_end_date_hr=prj_end_date_hr,
    dict_task_status=dict_task_status,
    dict_task_types=dict_task_types,
    dict_sm_costs=dict_sm_costs,
    dict_sm_labours=dict_sm_labours,
    dict_sm_nonlabours=dict_sm_nonlabours,
    dict_float_metrics=dict_float_metrics,
    dict_float_dist=dict_float_dist,
    selected_project_id=selected_project_id,
    my_cost_progress=my_cost_progress,
    my_labour_progress=my_labour_progress,
    my_nonlabour_progress=my_nonlabour_progress,
    dict_Task_Metrics=dict_Task_Metrics,
    dict_Mil_Metrics=dict_Mil_Metrics)

@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/gonder', methods=['POST'])
def gonder():
    files = request.files.getlist('files[]')
    modules.loadXer.xer_to_dataframe(files)
    return ""

@app.route('/projectselection', methods=['POST'])
def projectselection():
    # df_project = config.my_dataframes['PROJECT']
    # df_project_filtered = df_project.filter(['proj_id', 'proj_short_name'], axis=1)
    df_project = config.my_dataframes['PROJWBS']
    df_project_filtered = df_project.loc[df_project['proj_node_flag'] == 'Y', ['proj_id', 'wbs_short_name', 'wbs_name']]
    dict_project_list = df_project_filtered.to_dict(orient='records')
    return render_template('projectselection.html', dict_project_list=dict_project_list)


@app.route('/task-metrics', methods=['POST', 'GET'])
def task_metrics():
    dict_Task_Metrics_Detail = list_Diagnostic_Results[2] 
    return render_template('task-metrics.html', dict_Task_Metrics_Detail = dict_Task_Metrics_Detail )

@app.route('/mil-metrics', methods=['POST', 'GET'])
def mil_metrics():
    dict_Mil_Metrics_Detail = list_Diagnostic_Results[3]
    return render_template('mil-metrics.html', dict_Mil_Metrics_Detail = dict_Mil_Metrics_Detail )

if __name__ == '__main__':
    app.run(debug=True)
