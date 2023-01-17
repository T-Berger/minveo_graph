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
BENCHMARKS = [("LU0323577840", "EUFUND"), ("GDAXI", "INDX"), ("STOXX50E", "INDX"), ("TEPLX", "US")]


def fetch_stock_data(first_day, today, api_key, benchmark_string_pairs):
    df_temp = pd.DataFrame()
    for string_pair in benchmark_string_pairs:
        df_bench = get_eod_data(string_pair[0], string_pair[1], first_day, today, api_key=api_key).reset_index()
        standardise_benchmark(df_bench['Adjusted_close'])

        df_temp['Date'] = df_bench['Date']
        df_temp['{}.{}'.format(string_pair[0], string_pair[1])] = df_bench['Adjusted_close']

    return df_temp


def standardise_benchmark(row):
    first_entry = row[0]

    for i, value in enumerate(row):
        row[i] = pd.to_numeric(math.ceil(value / (first_entry / 100) * 100) / 100)


def dateparse(date_string):
    return datetime.strptime(date_string, '%d.%m.%y').date()


def get_csv_data(first_day, today):
    df_temp = pd.read_csv("Macromedia_example.csv", sep=';', parse_dates=['Date'], date_parser=dateparse)
    df_temp = df_temp.loc[(df_temp["Date"] >= first_day) & (df_temp["Date"] <= today)]
    df_csv_columns = ['Cash', 'Defensiv', 'Offensiv', 'Ausgewogen']

    for column in df_csv_columns:
        df_temp[column] = pd.to_numeric(df_temp[column].str.replace(',', '.').str.replace('€', ''))
    return df_temp


df_csv = get_csv_data(FIRST_DAY, TODAY)
df_stock = fetch_stock_data(FIRST_DAY, TODAY, API_KEY, BENCHMARKS)
df = pd.merge(df_csv, df_stock, on='Date')

app = Dash(__name__)

app.layout = html.Div([
    html.H1('Stock price analysis', style={'textAlign': 'center'}),
    html.Div(children=[
        html.Button('Logarithmisch', id='lin/log', n_clicks=0),
    ]),

    html.Div([
        html.Label('Einmalige Zahlung: '),
        dcc.Input(id='einmalig', type='number', value=100, min=1),
    ]),
    html.Div(children=[
        html.Label('Inflation'),
        html.Br(),
        html.Button('On', id='infl_on', n_clicks=0),
        html.Button('Off', id='infl_off', n_clicks=0),
    ]),

    html.Div([
        html.Label('Minveo Strategie: '),
        dcc.Checklist(
            id='minveo_strategies',
            options=[
                {'label': 'Defensiv', 'value': 'Defensiv'},
                {'label': 'Ausgewogen', 'value': 'Ausgewogen'},
                {'label': 'Offensiv', 'value': 'Offensiv'}
            ],
            value=['Offensiv']
        ),

        html.Label('Benchmarks: '),
        dcc.Checklist(
            id='benchmarks',
            options=[
                {'label': 'Cash', 'value': 'Cash'},
                {'label': 'LU0323577840.EUFUND', 'value': 'LU0323577840.EUFUND'},
                {'label': 'GDAXI.INDX', 'value': 'GDAXI.INDX'},
                {'label': 'STOXX50E.INDX', 'value': 'STOXX50E.INDX'},
                {'label': 'TEPLX.US', 'value': 'TEPLX.US'}
            ],
            value=['Cash']
        )
    ]),
    dcc.Graph(id='myfig', config={
        'displayModeBar': False}),

])

@app.callback(
    Output('lin/log', 'children'),
    Output('myfig', 'figure'),
    Input('lin/log', 'n_clicks'),
    Input('einmalig', 'value'),
    Input('infl_on', 'n_clicks'),
    Input('infl_off', 'n_clicks'),
    Input('minveo_strategies', 'value'),
    Input('benchmarks', 'value')
)
def update_output(n_clicks_log, einmalig, n_clicks_on, n_clicks_off, minveo_value, benchmark_value):
    
    if einmalig is None or einmalig <= 0:
        einmalig = 100

    for column in df.loc[:, df.columns != 'Date']:
        df[column] = df[column] * (einmalig / df.iloc[0][column])

    traces = []
    for trace_name in minveo_value:
        traces.append(go.Scatter(
            x=df['Date'],
            y=df[trace_name],
            mode='lines',
            name=trace_name
        ))
    for trace_name in benchmark_value:
        traces.append(go.Scatter(
            x=df['Date'],
            y=df[trace_name],
            mode='lines',
            name=trace_name
        ))

    if n_clicks_log % 2 == 0:
        lin_log_text = 'Logarithmisch'
    else:
        lin_log_text = 'Linear'

    fig = go.Figure(data=traces)

    '''for column in ['Defensiv', 'Ausgewogen']:
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df[column],
            legendgroup="strategie_group", legendgrouptitle_text="Minveo Strategie",
            name=column, mode="lines", visible='legendonly'
        ))

    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['Offensiv'],
        legendgroup="strategie_group", legendgrouptitle_text="Minveo Strategie",
        name='Offensiv', mode="lines",
    ))

    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['Cash'],
        legendgroup="benchmark_group", legendgrouptitle_text="Benchmark",
        name='Cash', mode="lines"
    ))

    for column in ['LU0323577840.EUFUND', 'GDAXI.INDX', 'STOXX50E.INDX', 'TEPLX.US']:
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df[column],
            legendgroup="benchmark_group", legendgrouptitle_text="Benchmark",
            name=column, mode="lines", visible='legendonly'
        ))'''

    fig.update_layout(yaxis_type='log' if n_clicks_log % 2 == 1 else 'linear', height=700)
    fig.update_layout(showlegend=False, legend=dict(
        groupclick="toggleitem", orientation="h", yanchor="top",
        y=-0.6,
        xanchor="left",
        x=0),
                      xaxis=dict(rangeslider=dict(visible=True)))
    fig.update_xaxes(rangeslider_thickness=0.1)

    return 'Linear' if n_clicks_log % 2 == 0 else 'Logarithmic', fig


if __name__ == '__main__':
    app.run_server(debug=True)