# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, callback
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import Datareader as dr

data = dr.Datareader()

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = data.get_graph_data('KRX','힘스','3S')
fig = px.line(df, x='Date', y="Close",color='name')

app.layout = html.Div(children=[

    html.H1(children='STOCK ANALYSIS',
            style={'textAlign': 'center', 'color': '#7FDBFF'}),

    html.Div(html.H3(children='''SHOW STOCK ANALYSIS GRAPH'''
                     ,style={'margin':'10px','margin-left':'10%','color':'white'})),

    html.Div([dcc.Input(id="stock_name", type="text", placeholder="input stock name"
                       ,style={'width': '80%'}), html.Button(id='submit',n_clicks=0,value='SEARCH',style={'width':'50px','height':'20px'})]
             ,style={'textAlign':'center'}
             ),

    html.Div(dcc.Graph( id='example-graph', figure=fig)),
    html.Div()
],style={'background-color':'black'})

@app.callback(
    Output(component_id='example-graph',component_property='figure'),
    Input(component_id='submit',component_property='n_clicks'),
    State(component_id="stock_name",component_property='value')
              )
def search_stock(n_click ,name):
    if(n_click==0):
        return fig
    return px.line(data.get_graph_data('KRX',name), x='Date', y="Close",color='name')

if __name__ == '__main__':
    app.run_server(debug=True)






