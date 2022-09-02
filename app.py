# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, callback, ctx
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import Datareader as dr

data = dr.Datareader()
data.read_fc('KRX')
default_graph = px.line(data.default_graph, x='Date', y="Close")

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

app.layout = html.Div(children=[

    html.H1(children='STOCK ANALYSIS',
            style={'textAlign': 'center', 'color': '#7FDBFF'}),

    html.Div(html.H3(children='''SHOW STOCK ANALYSIS GRAPH'''
                     ,style={'margin':'10px','margin-left':'10%','color':'white'})),

    html.Div([dcc.Input(id="stock_name", type="text", placeholder="input stock name"
                       ,style={'width': '80%'}), html.Button(id='submit',n_clicks=0,value='SEARCH',style={'width':'50px','height':'20px'})]
             ,style={'textAlign':'center'}
             ),
    html.Div([dcc.RadioItems([
        {
            "label": 'ONLY STOCK',
            "value": "stock",
        },
        {
            "label": 'MOVING AVG',
            "value": "m_avg",
        },
        {
            "label": 'MUTY STOCK GRAGP',
            "value": "multi",
        }
    ],value="stock",id='radio', inline=True
     ,style={'margin':'10px','margin-left':'10%','width':'40%','color': 'white', 'font-size': 10,}
    )]
    ),
    html.Div(dcc.Graph( id='example-graph')),
    html.Div()
],style={'background-color':'black'})

@app.callback(
    Output(component_id='example-graph',component_property='figure'),
    Input(component_id='submit',component_property='n_clicks'),
    State(component_id="stock_name",component_property='value'),
    Input(component_id='radio',component_property='value')
              )
def switch(n_click , name, value):
    trigger_id = ctx.triggered_id
    if trigger_id == 'submit':
        return search_stock(n_click,name)
    elif trigger_id == 'radio':
        return change_mode(value)
    else:
        return default_graph
def search_stock(n_click ,name):
    if(n_click==0):
        return default_graph
    return px.line(data.get_graph_data('KRF',name), x='Date', y="Close",color='name')

def change_mode(value):
    if value == 'stock':
        data.off_multi_state()
        return px.line(data.current_graph_data, x='Date', y="Close",color='name')
    elif value == 'm_avg':
        data.off_multi_state()
        if data.current_show_stock_list is None:
            return px.line(data.current_graph_data, x='Date', y="Close",color='name')
        else:
            return px.line(data.get_graph_mavg_data('KRF',data.current_show_stock_list[-1],5,20,60), x='Date', y="Close",color='name')
    else:
        data.on_multi_state()
        return px.line(data.current_graph_data, x='Date', y="Close",color='name')


if __name__ == '__main__':
    app.run_server(debug=True)






