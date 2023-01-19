import itertools
import math
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
from decouple import config

from python_eodhistoricaldata.eod_historical_data import get_eod_data

API_KEY = config('API_KEY')
FIRST_DAY = '30/06/17'
TODAY = datetime.today().strftime('%Y/%m/%d')
BENCHMARKS = [('LU0323577840', 'EUFUND'), ('GDAXI', 'INDX'), ('STOXX50E', 'INDX'), ('TEPLX', 'US')]


def fetch_stock_data(first_day, today, api_key, benchmarks):
    """Requesting historical stock data from the EOD Historical Data API.

    These data is assembled in a dataframe and set as output.
    """
    df_temp = pd.DataFrame()
    for string_pair in benchmarks:
        df_bench = get_eod_data(string_pair[0], string_pair[1], first_day, today, api_key=api_key).reset_index()
        normalise_benchmark(100, df_bench['Adjusted_close'])

        df_temp['Date'] = df_bench['Date']
        df_temp['{}.{}'.format(string_pair[0], string_pair[1])] = df_bench['Adjusted_close']

    return df_temp


def normalise_benchmark(one_time_value, row):
    """Iteration through a dataframe row to normalise the values to a specific value.

    These values are shortened to two decimal places.
    """
    first_entry = row[0]

    for i, value in enumerate(row):
        row[i] = pd.to_numeric(math.ceil(value / (first_entry / one_time_value) * 100) / 100)


def dateparse(date_string):
    """Parsing a date string according to a specific format.
    """
    return datetime.strptime(date_string, '%d.%m.%y').date()


def get_csv_data(first_day, today):
    """Retrieve data representing the Minveo strategy from a local CSV file from a specific period of time.

    These data is formatted, assembled in a dataframe and set as output.
    """
    df_temp = pd.read_csv('Macromedia_example.csv', sep=';', parse_dates=['Date'], date_parser=dateparse)
    df_temp = df_temp.loc[(df_temp['Date'] >= first_day) & (df_temp['Date'] <= today)]
    df_csv_columns = ['Cash', 'Defensiv', 'Offensiv', 'Ausgewogen']

    for column in df_csv_columns:
        df_temp[column] = pd.to_numeric(df_temp[column].str.replace(',', '.').str.replace('€', ''))
    return df_temp


df_csv = get_csv_data(FIRST_DAY, TODAY)
df_stock = fetch_stock_data(FIRST_DAY, TODAY, API_KEY, BENCHMARKS)
df = pd.merge(df_csv, df_stock, on='Date')

df['Date'] = df['Date'].apply(lambda x: x.timestamp())

app = Dash(__name__)

app.layout = html.Div([
    html.H1('Historische Aktienkursanalyse und Vergleich mit Minveo Strategien', style={'textAlign': 'center'}),

    html.Div([
        html.Label('Einmalige Zahlung: '),
        dcc.Input(id='one_time', type='number', value=100, min=1),
    ]),
    html.Div(children=[
        html.Label('Inflation'),
        html.Br(),
        html.Button('Ein', id='infl_on', n_clicks=0),
        html.Button('Aus', id='infl_off', n_clicks=0),
    ]),

    html.Div([
        html.Label('Minveo Strategien: '),
        dcc.Dropdown(
            id='minveo_strategies',
            options=[
                {'label': 'Defensiv', 'value': 'Defensiv'},
                {'label': 'Ausgewogen', 'value': 'Ausgewogen'},
                {'label': 'Offensiv', 'value': 'Offensiv'}
            ],
            value=['Offensiv'],
            clearable=False,
            multi=True,
            style={
                'width': '55%'}
        ),

        html.Label('Benchmarks: '),
        dcc.Dropdown(
            id='benchmarks',
            options=[
                {'label': 'Cash', 'value': 'Cash'},
                {'label': 'LU0323577840.EUFUND', 'value': 'LU0323577840.EUFUND'},
                {'label': 'GDAXI.INDX', 'value': 'GDAXI.INDX'},
                {'label': 'STOXX50E.INDX', 'value': 'STOXX50E.INDX'},
                {'label': 'TEPLX.US', 'value': 'TEPLX.US'}
            ],
            value=['Cash'],
            clearable=False,
            multi=True,
            style={
                'width': '55%'}
        )
    ]),

    html.Div(children=[
        html.Button('Logarithmisch', id='lin/log', n_clicks=0),
    ]),

    dcc.Graph(id='my_fig', config={
        'displayModeBar': False}),

    html.Div(children=[
        dcc.RangeSlider(id='rangeslider',
                        min=min(df['Date']),
                        max=max(df['Date']),
                        value=[min(df['Date']), max(df['Date'])],
                        step=1,
                        marks={i: str(datetime.fromtimestamp(i)) for i in df['Date'][::30]},
                        # display the date in the marks
                        updatemode='drag')
    ]),

])


@app.callback(
    Output('lin/log', 'children'),
    Output('my_fig', 'figure'),
    Input('lin/log', 'n_clicks'),
    Input('one_time', 'value'),
    Input('infl_on', 'n_clicks'),
    Input('infl_off', 'n_clicks'),
    Input('minveo_strategies', 'value'),
    Input('benchmarks', 'value'),
    Input('rangeslider', 'value')
)
def update_output(n_clicks_log, one_time, n_clicks_on, n_clicks_off, minveo_value, benchmark_value, rangesl_value):
    start_timestamp = rangesl_value[0]
    end_timestamp = rangesl_value[1]

    df_filtered = df[(df['Date'] >= start_timestamp) & (df['Date'] <= end_timestamp)]

    df_filtered['Date'] = pd.to_datetime(df_filtered['Date'], unit='s')

    if one_time is None or one_time <= 0:
        one_time = 100

    for column in df_filtered.loc[:, df_filtered.columns != 'Date']:
        normalise_benchmark(one_time, df[column])

    traces = []
    for trace_name in itertools.chain(minveo_value, benchmark_value):
        traces.append(go.Scatter(
            x=df_filtered['Date'],
            y=df_filtered[trace_name],
            mode='lines',
            name=trace_name
        ))

    fig = go.Figure(data=traces)

    if n_clicks_log % 2 == 0:
        lin_log_text = 'Logarithmisch'
        fig.update_layout(yaxis_type='log')
    else:
        lin_log_text = 'Linear'
        fig.update_layout(yaxis_type='linear')

    fig.update_layout(showlegend=True,
                      legend=dict(groupclick="toggleitem", orientation="h"),
                      xaxis=dict(rangeslider=dict(visible=True)),
                      height=700)
    fig.update_xaxes(rangeslider_thickness=0.1)

    return lin_log_text, fig


if __name__ == '__main__':
    app.run_server(debug=True)
