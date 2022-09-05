# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, callback, ctx
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import Datareader as dr
from datetime import datetime

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__,external_stylesheets=external_stylesheets)
data = dr.Datareader()
default_graph = px.line(data.default_graph, x='Date', y="Close",color='name')
state = None
colors = {'background': '#111111','text': '#7FDBFF'}
load = True


app.layout = html.Div(children=[

    html.H1(children='STOCK ANALYSIS',
            style={'textAlign': 'center', 'color': '#7FDBFF','border':'5px'}),

    html.Div(html.H5(children='''SHOW STOCK ANALYSIS GRAPH'''
                     ,style={'margin':'10px','margin-left':'10%','color':'#ffc500'})),
    html.Div(style={'height':'5px'}),
    html.Div(style={'background-color':'#C0C0C0','height':'5px','opacity':0.5}),
    html.Div(style={'height':'5px'}),

    html.Div([dcc.Input(id="stock_name", type="text", placeholder="input stock name"
                       ,style={'width': '80%'}),
              html.Button(children='SEARCH',id='submit',n_clicks=0
                          ,style={'width':'100px','height':'40px','margin-top':'5px','color':'white','textAlign': 'center'})]
              ,style={'textAlign':'center'}
             ),
    html.Div(style={'height':'5px'}),
    html.Div([
        dcc.RadioItems([
        {
            "label": 'ONLY STOCK',
            "value": "stock",
        },
        {
            "label": 'MOVING AVG',
            "value": "m_avg",
        },
        {
            "label": 'MUTY STOCK GRAPH',
            "value": "multi",
        }
    ],value="stock",id='radio', inline=True
     ,style={'margin':'10px','margin-left':'10%','width':'40%','color': 'white', 'font-size': 10,'display':'inline'}
    )
        ,

        dcc.DatePickerRange(
            id='period',
            start_date_placeholder_text="Start Period",
            end_date_placeholder_text="End Period",
            calendar_orientation='vertical',
            start_date=datetime(datetime.now().year - 1, datetime.now().month, datetime.now().day),
            end_date=datetime(datetime.now().year, datetime.now().month, datetime.now().day),
            display_format="YYYY-MM-DD",
            style={'margin-left':'38%','display':'inline'}
        )
    ]
        ,style={'textAlign':'horizontal'}
    ),
    html.Div(style={'height':'5px'}),
    html.Div(style={'background-color':'#C0C0C0','height':'5px','opacity':0.5}),
    html.Div(dcc.Graph( id='example-graph')),
    html.Div(style={'background-color':'#C0C0C0','height':'5px','opacity':0.5})
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
        result = change_mode(state,start,end).update_layout({'plot_bgcolor':colors['background'],'paper_bgcolor': colors['background']})
        result.update_layout(font_color = 'white')
        return result
    elif trigger_id == 'radio':
        result = change_mode(value,start,end).update_layout({'plot_bgcolor':colors['background'],'paper_bgcolor': colors['background']})
        result.update_layout(font_color = 'white')
        return result
    else:
        result = default_graph.update_layout({'plot_bgcolor':colors['background'],'paper_bgcolor': colors['background']})
        result.update_layout(font_color = 'white')
        return result
def search_stock(n_click ,name):
    if(name is None):
        return
    if(n_click!=0):
        data.get_graph_data('KRX', name)

def change_mode(value,start,end):
    if value == 'stock':
        data.off_multi_state()
        period_data = data.get_graph_period_data(data.current_graph_data,start,end)
        return px.line(period_data, x='Date', y="Close",color='name')
    elif value == 'm_avg':
        data.off_multi_state()
        if len(data.current_show_stock_list) == 0 :
            period_data = data.get_graph_period_data(data.current_graph_data,start,end)
            return px.line(period_data, x='Date', y="Close",color='name')
        else:
            print(data.current_show_stock_list[-1])
            period_data = data.get_graph_period_data(data.get_graph_mavg_data('KRX',data.current_show_stock_list[-1],5,20,60),start,end)
            return px.line(period_data, x='Date', y="Close",color='name')
    elif value == 'multi':
        data.on_multi_state()
        period_data = data.get_graph_period_data(data.current_graph_data,start,end)
        return px.line(period_data, x='Date', y="Close",color='name')
    else:
        return default_graph


if __name__ == '__main__':
    if load:
        load = False
        data.read_fc('KRX')
        data.sync_db()
    app.run_server(debug=True)
    data.manager.save_dr(data)






