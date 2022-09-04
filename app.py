# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, callback, ctx
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import Datareader as dr
from datetime import datetime

app = Dash(__name__)
data = dr.Datareader()
default_graph = px.line(data.default_graph, x='Date', y="Close",color='name')
state = None


app.layout = html.Div(children=[

    html.H1(children='STOCK ANALYSIS',
            style={'textAlign': 'center', 'color': '#7FDBFF'}),

    html.Div(html.H3(children='''SHOW STOCK ANALYSIS GRAPH'''
                     ,style={'margin':'10px','margin-left':'10%','color':'white'})),

    html.Div([dcc.Input(id="stock_name", type="text", placeholder="input stock name"
                       ,style={'width': '80%'}),
              html.Button(id='submit',n_clicks=0,value='SEARCH',style={'width':'50px','height':'20px'})]
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
    ),
        dcc.DatePickerRange(
            id='period',
            start_date_placeholder_text="Start Period",
            end_date_placeholder_text="End Period",
            calendar_orientation='vertical',
            start_date=datetime(datetime.now().year - 1, datetime.now().month, datetime.now().day),
            end_date=datetime(datetime.now().year, datetime.now().month, datetime.now().day),
            display_format="YYYY-MM-DD"
        )
    ]
    ),
    html.Div(dcc.Graph( id='example-graph')),
    html.Div()
],style={'background-color':'black'})

@app.callback(
    Output(component_id='example-graph',component_property='figure'),
    Input(component_id='submit',component_property='n_clicks'),
    State(component_id="stock_name",component_property='value'),
    Input(component_id='radio',component_property='value'),
    State(component_id='period',component_property="start_date"),
    State(component_id='period',component_property='end_date')
              )
def switch(n_click , name, value,start,end):
    trigger_id = ctx.triggered_id
    global state
    state = value
    if trigger_id == 'submit':
        search_stock(n_click,name)
        return change_mode(state,start,end)
    elif trigger_id == 'radio':
        return change_mode(value,start,end)
    else:
        return default_graph
def search_stock(n_click ,name):
    if(n_click!=0):
        data.get_graph_data('KRF', name)

def change_mode(value,start,end):
    if value == 'stock':
        data.off_multi_state()
        period_data = data.get_graph_period_data(data.current_graph_data,start,end)
        return px.line(period_data, x='Date', y="Close",color='name')
    elif value == 'm_avg':
        data.off_multi_state()
        if data.current_show_stock_list is None:
            period_data = data.get_graph_period_data(data.current_graph_data,start,end)
            return px.line(period_data, x='Date', y="Close",color='name')
        else:
            period_data = data.get_graph_period_data(data.get_graph_mavg_data('KRF',data.current_show_stock_list[-1],5,20,60),start,end)
            return px.line(period_data, x='Date', y="Close",color='name')
    elif value == 'multi':
        data.on_multi_state()
        period_data = data.get_graph_period_data(data.current_graph_data,start,end)
        return px.line(period_data, x='Date', y="Close",color='name')
    else:
        return default_graph


if __name__ == '__main__':
    data.read_fc('KRX')
    data.sync_db()
    app.run_server(debug=True)
    data.manager.save_dr(data)






