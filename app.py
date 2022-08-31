# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

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
df = pd.DataFrame(data={'DATE':[1,2,3,4,5,6],'p':[1,2,3,4,5,6],'ORIGN':[6,5,4,3,2,1],'ORIGN':[3,3,3,3,3,3]})
print(df)
fig = px.line(df, x="DATE", y=['SHORT','ORIGN','LONG'])

app.layout = html.Div(children=[

    html.H1(children='STOCK ANALYSIS',
            style={'textAlign': 'center', 'color': '#7FDBFF'}),

    html.Div(html.H3(children='''SHOW STOCK ANALYSIS GRAPH'''
                     ,style={'margin':'10px','margin-left':'10%','color':'white'})),

    html.Div(dcc.Input(id="stock_name", type="text", placeholder="input stock name"
                       ,style={'width': '80%'})
             ,style={'width': '100%','text-align': 'center'}),

    html.Div(dcc.Graph( id='example-graph', figure=fig)),
    html.Div()
],style={'background-color':'black'})

if __name__ == '__main__':
    app.run_server(debug=True)






