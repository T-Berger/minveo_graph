import math
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from decouple import config
from python_eodhistoricaldata.eod_historical_data import get_eod_data
from dash import Dash, dcc, html, Input, Output, ctx

API_KEY = config('API_KEY')
FIRST_DAY = "30/06/17"
TODAY = datetime.today().strftime('%Y/%m/%d')

def fetch_stock_data():
    df_lu = get_eod_data("LU0323577840", "EUFUND", FIRST_DAY, TODAY, api_key=API_KEY).reset_index()
    df_dax = get_eod_data("GDAXI", "INDX", FIRST_DAY, TODAY, api_key=API_KEY).reset_index()
    df_stox = get_eod_data("STOXX50E", "INDX", FIRST_DAY, TODAY, api_key=API_KEY).reset_index()
    df_teplx = get_eod_data("TEPLX", "US", FIRST_DAY, TODAY, api_key=API_KEY).reset_index()

    return df_lu, df_dax, df_stox, df_teplx

def standardize_data(df_lu, df_dax, df_stox, df_teplx):
    def standardise_benchmark(row):
        first_entry = row[0]

        for i, value in enumerate(row):
            row[i] = pd.to_numeric(math.ceil(value / (first_entry / 100) * 100) / 100)

    standardise_benchmark(df_lu['Adjusted_close'])
    standardise_benchmark(df_dax['Adjusted_close'])
    standardise_benchmark(df_stox['Adjusted_close'])
    standardise_benchmark(df_teplx['Adjusted_close'])

def get_csv_data():
    def dateparse(date_string):
        return datetime.strptime(date_string, '%d.%m.%y').date()

    df_csv = pd.read_csv("Macromedia_example.csv", sep=';', parse_dates=['Date'], date_parser=dateparse)
    df_csv = df_csv.loc[(df_csv["Date"] >= FIRST_DAY) & (df_csv["Date"] <= TODAY)]
    df_csv_columns = ['Cash', 'Defensiv', 'Offensiv', 'Ausgewogen']

    for column in df_csv_columns:
        df_csv[column] = pd.to_numeric(df_csv[column].str.replace(',', '.').str.replace('€', ''))
    return df_csv

df_lu, df_dax, df_stox, df_teplx = fetch_stock_data()
standardize_data(df_lu, df_dax, df_stox, df_teplx)

df = get_csv_data()

df['LU0323577840.EUFUND'] = df_lu['Adjusted_close']
df['GDAXI.INDX'] = df_dax['Adjusted_close']
df['STOXX50E.INDX'] = df_stox['Adjusted_close']
df['TEPLX.US'] = df_teplx['Adjusted_close']

app = Dash(__name__)

app.layout = html.Div([
    html.H1('Stock price analysis', style={'textAlign': 'center'}),
    html.Div(children=[
        html.Button('Logarithmisch', id='lin/log', n_clicks=0),
    ]
    ),
    html.Div([
        html.Label('Einmalige Zahlung'),
        dcc.Input(id='einmalig', type='number', value=100, min=1),
    ]),
    html.Div(children=[
        html.Label('Inflation'),
        html.Br(),
        html.Button('On', id='infl_on', n_clicks=0),
        html.Button('Off', id='infl_off', n_clicks=0),
    ]),
    
    dcc.Graph(id='mygraph')
])

@app.callback(
    Output('lin/log', 'children'),
    Output('mygraph', 'figure'),
    Input('lin/log', 'n_clicks'),
    Input('einmalig', 'value'),
    Input('infl_on', 'n_clicks'),
    Input('infl_off', 'n_clicks')
)
def update_output(n_clicks_log, payment, n_clicks_on, n_clicks_off):

    df_lu, df_dax, df_stox, df_teplx = fetch_stock_data()
    standardize_data(df_lu, df_dax, df_stox, df_teplx)
    df = get_csv_data()
    df['LU0323577840.EUFUND'] = df_lu['Adjusted_close'] * (payment / df_lu.iloc[0]['Adjusted_close'])
    df['GDAXI.INDX'] = df_dax['Adjusted_close'] * (payment / df_dax.iloc[0]['Adjusted_close'])
    df['STOXX50E.INDX'] = df_stox['Adjusted_close'] * (payment / df_stox.iloc[0]['Adjusted_close'])
    df['TEPLX.US'] = df_teplx['Adjusted_close'] * (payment / df_teplx.iloc[0]['Adjusted_close'])

    traces = []
    for column in df.columns[1:]:
        traces.append(go.Scatter(x=df['Date'], y=df[column], name=column))

    if n_clicks_log % 2 == 0:
        lin_log_text = 'Logarithmisch'
    else:
        lin_log_text = 'Linear'

    fig = go.Figure()
    
    for column in ['Cash', 'Defensiv', 'Ausgewogen', 'Offensiv']:
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df[column],
            legendgroup="strategie_group", legendgrouptitle_text="Minveo Strategie",
            name=column, mode="lines",
        ))

    for column in ['LU0323577840.EUFUND', 'GDAXI.INDX', 'STOXX50E.INDX', 'TEPLX.US']:
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df[column],
            legendgroup="benchmark_group", legendgrouptitle_text="Benchmark",
            name=column,mode="lines",
        ))


    fig.update_layout(yaxis_type='log' if n_clicks_log % 2 == 1 else 'linear')
    fig.update_layout(showlegend=True, legend=dict(groupclick="toggleitem"))
    return lin_log_text, fig

if __name__ == '__main__':
    app.run_server(debug=True)