import pandas as pd
import app
from flask import request
from werkzeug.utils import secure_filename

def xer_to_dataframe(files):

    for file in files:
        filename = secure_filename(file.filename)
        dff = load_data(file)
        tablelist = dff['table'].unique()
        tables = pd.DataFrame(tablelist)
        tables.columns = ['tables']
        grouped = dff.groupby(dff.table)
        df_list = {}

        for x in tablelist:
            df = clean(grouped, x)
            app.my_dataframes[x] = df

def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file, sep='\t', names=range(100), encoding='unicode_escape', dtype=str)
    df.loc[df[0] == '%T', 'table'] = df[1]
    df['table'].fillna(method='ffill', inplace=True)
    data = df.loc[df[0].isin(['%R', '%F'])]
    return data

def clean(grouped, table):
    DF = grouped.get_group(table)
    DF.dropna(axis=1, how='all', inplace=True)
    new_header = DF.iloc[0]  # grab the first row for the header
    DF = DF[1:]  # take the data less the header row
    DF.columns = new_header  # set the header row as the df header
    del DF['%F']
    return DF

