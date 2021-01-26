import config
from graphviz import Digraph
from _PathPrintClass import Graph


def generateGraphviz(selected_start_task_int, selected_end_task_int):
    result_list = create_unique_task_list()
    myfinalarray = result_list[0]
    myDict = result_list[1]

    mySwappedDict = {}

    mySwappedDict = dict([(value, key) for key, value in myDict.items()])
    # print (len(myDict))
    g = Graph(len(myfinalarray))
    for x in myfinalarray:
        a = (x[0])
        b = (x[1])
        g.addEdge(a, b)

    s = int(selected_start_task_int)
    d = int(selected_end_task_int)

    result = g.printAllPaths(s, d)
    for r in result:
        for p in range(len(r)):
            r[p] = mySwappedDict[r[p]]

    cnt_total_paths = len(result)

    gp = Digraph()

    unique_result = []

    for nn in result:
        for x in range(len(nn) - 1):
            # print(nn[x])
            # print(nn[x + 1])
            temp_val = nn[x] + "|" + nn[x + 1]
            if temp_val not in unique_result:
                unique_result.append(temp_val)
                gp.edge(nn[x], nn[x + 1])
            else:
                continue

    gp_final = gp.pipe(format='svg')
    return gp_final, cnt_total_paths


def create_unique_task_list():
    df_taskpred_org = config.my_dataframes['TASKPRED']
    df_taskpred = df_taskpred_org.filter(['pred_task_id', 'task_id'], axis=1)
    df_taskpred = df_taskpred.sort_values(by=['pred_task_id'])

    mycombinedarray = []
    dfsize = len(df_taskpred)
    for i in range(dfsize):
        x = df_taskpred.iloc[i, 0]
        y = df_taskpred.iloc[i, 1]
        mycombinedarray.append(df_taskpred.iloc[i, 0])
        mycombinedarray.append(df_taskpred.iloc[i, 1])
    myuniquearray = set(mycombinedarray)
    myuniquearray = sorted(myuniquearray)
    myDict = {}
    mySecDic = {'task_id': [], 'int_task': []}
    m = 1
    for h in myuniquearray:
        myDict[h] = m
        mySecDic['task_id'].append(h)
        mySecDic['int_task'].append(m)
        m += 1
    myfinalarray = []
    for i in range(dfsize):
        x = df_taskpred.iloc[i, 0]
        y = df_taskpred.iloc[i, 1]
        myfinalarray.append([myDict[x], myDict[y]])

    result_list = [myfinalarray, myDict, mySecDic]

    return result_list
