import src.config
import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output


def main(df, column_to_vis):
    df_vis = df.reset_index()
    list_of_method = ["IQR", "MAD", "SD", "rSD"]
    ls_cleaned = []

    for method in list_of_method:
        ls_cleaned.append({'label': html.Div(
            method, style={'font-size': 15, 'padding-right': "0.5rem"}), 'value': method})

    fig = px.scatter(df,
                     x=df_vis.index,
                     y=column_to_vis[0])  # initialize app

    app = dash.Dash(__name__, external_stylesheets=[
                    dbc.themes.COSMO])  # set app layout

    app.layout = html.Div(children=[
        html.H1('Outliers visualisation', style={
                'textAlign': 'center', "font-weight": "bold"}),
        html.Br(),
        dbc.Row(
            [dbc.Col(
                html.Div(
                    dcc.Dropdown(
                        options=[{'label': i, 'value': i}
                                 for i in column_to_vis],
                        value=str(column_to_vis[0]),
                        id='dropdown',
                        style={"width": "50%", "offset": 1, },
                        clearable=False)
                )
            ),
                dbc.Col(html.Div(children=[
                    dcc.Checklist(options=ls_cleaned,
                                  id="checklist",
                                  labelStyle={'display': 'inline-flex'})]))]
        ),
        dcc.Graph(id='scatter', figure=fig)
    ])
    # callbacks
    # https://dash.plotly.com/duplicate-callback-outputs

    @app.callback(
        Output(component_id='scatter', component_property='figure'),
        Input(component_id='checklist', component_property='value'),
        Input(component_id='dropdown', component_property='value'),
    )
    def update_graph(y, method):
        triggered_id = dash.ctx.triggered_id
        fig = px.scatter(df, x=df.index, y=y)
        
        if triggered_id == 'dropdown':
            fig = update_threshold(df, fig, method, y)
        return fig


    app.run_server(debug=True)

def update_threshold(df, fig, pre_method, y):
    method = pre_method.lower()
    func = src.config.DICT_FUNCTION(method)
    l_value = [2, 2.5, 3]
    low_threshold = []
    high_threshold = []
    for distance in l_value:
        if method == "mad":
            low_threshold, high_threshold = func(
                df, [y], distance, b)
        else:
            low_threshold, high_threshold = func(
                df, [y], distance)
        



    return fig