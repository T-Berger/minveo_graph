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

df = pd.read_csv("Macromedia_example.csv", sep=';', parse_dates=['Date'], date_parser=dateparse)
df = df.loc[(df["Date"] >= "30/06/17") & (df["Date"] <= "30/09/22")]

df_columns = ['Cash', 'Defensiv', 'Offensiv', 'Ausgewogen']

def convert(df, columns):

    for column in columns:
        df[column] = df[column].str.replace(',','.')
        df[column] = df[column].str.replace('€','')
        df[column] = pd.to_numeric(df[column])
        #print(column)

convert(df, df_columns)

df['LU0323577840.EUFUND'] = df_lu['Adjusted_close']
df['GDAXI.INDX'] = df_dax['Adjusted_close']
df['STOXX50E.INDX'] = df_stox['Adjusted_close']
df['TEPLX.US'] = df_teplx['Adjusted_close']

# df.info()

app = Dash(__name__)
app.layout = html.Div([
    html.H1('Stock price analysis', style={'textAlign': 'center'}),

    html.Button('Logarithmisch', id='log', n_clicks=0),
    html.Button('Linear', id='lin', n_clicks=0),

    dcc.Graph(id='mygraph'),

    html.Label('Slider'),
    dcc.Slider(min=df['Date'].min().year,
               max=df['Date'].max().year,
               step=1,
               value=1350,
               tooltip={"placement": "bottom", "always_visible": True},
               updatemode='drag',
               persistence=True,
               persistence_type='session',
               id="my-slider"
               ),
],
    style={'margin': 30}
)


@app.callback(
    Output('mygraph', 'figure'),
    Input('my-slider', 'value'),
    Input('log', 'n_clicks'),
    Input('lin', 'n_clicks')
)
def update_graph(slider_value, btn_log, btn_lin):
    fig = px.line(df, x='Date', y=df.columns, hover_data={'Date': '|%d/%m/%y'})

    fig.update_layout(xaxis=dict(ticks="outside",
                    ticklabelmode="period",
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all")])),
                            rangeslider=dict(visible=True)))


    if 'log' == ctx.triggered_id:
        fig.update_yaxes(type="log")

    elif 'lin' == ctx.triggered_id:
        return fig

    return fig


if __name__ == '__main__':
    app.run(debug=True)
