import json
import pandas as pd
import datetime
from graphviz import Digraph
from _PathPrintClass import Graph
from flask import Flask, render_template, request, redirect, abort, flash, url_for, jsonify
from werkzeug.utils import secure_filename
import plotly
import plotly.graph_objects as go
import networkx as nx
import modules.loadXer
import modules.calcStatistics
import modules.calcDiagnostics
import modules.drawPlotly
import modules.drawGraphviz
import config

app = Flask(__name__, static_url_path="/static", static_folder="/static")

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/navpanel', methods=['POST', 'GET'])
def navpanel():
    # Get selected project id from project selection page
    selected_project_id = str(request.form.get('project_selector'))

    modules.calcStatistics.update_my_filt_dataframes(selected_project_id) # update dataframes based on selected project id

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
    dict_Task_Metrics = modules.calcDiagnostics.funcDiagnostics()[0]
    dict_Mil_Metrics = modules.calcDiagnostics.funcDiagnostics()[1]

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

@app.route('/network')
def network():
    bar = modules.drawPlotly.create_plot()
    return render_template('network.html', plot=bar)


@app.route('/nodeselection', methods=['POST', 'GET'])
def nodeselection():
    result_list = modules.drawGraphviz.create_unique_task_list()
    mySecDic= result_list[2]
    df = pd.DataFrame.from_dict(mySecDic)
    dict_task_list = df.to_dict(orient='records')
    return render_template('nodeselection.html', dict_task_list=dict_task_list)

@app.route('/graphviz', methods=['POST', 'GET'])
def graphviz():

    # Get selected task id  from node selection page
    selected_start_task_int = str(request.form.get('start_node'))
    selected_end_task_int = str(request.form.get('end_node'))

    gp_final = modules.drawGraphviz.generateGraphviz(selected_start_task_int, selected_end_task_int)[0]
    cnt_total_paths = modules.drawGraphviz.generateGraphviz(selected_start_task_int, selected_end_task_int)[1]
    return render_template('graphviz.html', gp_final=gp_final, cnt_total_paths=cnt_total_paths)

@app.route('/task-metrics')
def task_metrics():
    return render_template('task-metrics.html')

@app.route('/mil-metrics')
def mil_metrics():
    return render_template('mil-metrics.html')

if __name__ == '__main__':
    app.run(debug=True)
