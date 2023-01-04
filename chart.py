import math
from datetime import datetime
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, ctx
from decouple import config

from python_eodhistoricaldata.eod_historical_data import get_eod_data

API_KEY = config('API_KEY')
dateparse = lambda x: datetime.strptime(x, '%d.%m.%y').date()
today = datetime.today().strftime('%Y/%m/%d')
first_day = "30/06/17"

df_lu = get_eod_data("LU0323577840", "EUFUND", first_day, today, api_key=API_KEY).reset_index()
df_dax = get_eod_data("GDAXI", "INDX", first_day, today, api_key=API_KEY).reset_index()
df_stox = get_eod_data("STOXX50E", "INDX", first_day, today, api_key=API_KEY).reset_index()
df_teplx = get_eod_data("TEPLX", "US", first_day, today, api_key=API_KEY).reset_index()


def standardise_benchmark(row):
    first_entry = row[0]

    for i, value in enumerate(row):
        row[i] = pd.to_numeric(math.ceil(value / (first_entry / 100) * 100) / 100)


standardise_benchmark(df_lu['Adjusted_close'])
standardise_benchmark(df_dax['Adjusted_close'])
standardise_benchmark(df_stox['Adjusted_close'])
standardise_benchmark(df_teplx['Adjusted_close'])


def convert(df_input, columns):

    for column in columns:
        df_input[column] = pd.to_numeric(df[column].str.replace(',', '.').str.replace('€', ''))


def get_csv_data():
    df_csv = pd.read_csv("Macromedia_example.csv", sep=';', parse_dates=['Date'], date_parser=dateparse)
    df_csv = df_csv.loc[(df_csv["Date"] >= first_day) & (df_csv["Date"] <= today)]
    return df_csv


df = get_csv_data()
df_columns = ['Cash', 'Defensiv', 'Offensiv', 'Ausgewogen']
convert(df, df_columns)

df['LU0323577840.EUFUND'] = df_lu['Adjusted_close']
df['GDAXI.INDX'] = df_dax['Adjusted_close']
df['STOXX50E.INDX'] = df_stox['Adjusted_close']
df['TEPLX.US'] = df_teplx['Adjusted_close']



app = Dash(__name__)
app.layout = html.Div([
    html.H1('Stock price analysis', style={'textAlign': 'center'}),

    html.Button('Logarithmisch', id='log', n_clicks=0),
    html.Button('Linear', id='lin', n_clicks=0),

    html.Button('Offensiv', id='off_btn', n_clicks=0),
    html.Button('Ausgewogen', id='asgw_btn', n_clicks=0),
    html.Button('Defensiv', id='def_btn', n_clicks=0),

    dcc.Graph(id='mygraph')
])


@app.callback(
    Output('mygraph', 'figure'),
    Input('log', 'n_clicks'),
    Input('lin', 'n_clicks'),
    Input('off_btn', 'n_clicks'),
    Input('asgw_btn', 'n_clicks'),
    Input('def_btn', 'n_clicks'),

)
def update_graph(btn_log, btn_lin, off_btn, asgw_btn, def_btn):
    exclude_columns = []

    # if 'off_btn' == ctx.triggered_id:
    #     if off_btn % 2 != 0:
    #         exclude_columns.append('Ausgewogen')
    #         exclude_columns.append('Defensiv')
    #
    # elif 'asgw_btn' == ctx.triggered_id:
    #     if asgw_btn % 2 != 0:
    #         exclude_columns.append('Offensiv')
    #         exclude_columns.append('Defensiv')
    #
    # elif 'def_btn' == ctx.triggered_id:
    #     if def_btn % 2 != 0:
    #         exclude_columns.append('Offensiv')
    #         exclude_columns.append('Ausgewogen')

    fig = px.line(df, x='Date',
                  y=df.columns
                  , hover_data={'Date': '|%d/%m/%y'})

    fig.update_xaxes(ticks="outside", rangeslider_visible=True, )
    fig.update_layout(showlegend=True, )

    if 'log' == ctx.triggered_id:
        fig.update_yaxes(type="log")

    elif 'lin' == ctx.triggered_id:
        fig.update_yaxes(type="linear")

    return fig


if __name__ == '__main__':
    app.run(debug=True)
