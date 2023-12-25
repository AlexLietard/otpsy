from os import chdir
chdir("../")

import config
import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from dash_bootstrap_templates import load_figure_template

load_figure_template('darkly')

def main(df, column_to_vis):
    a = {"border": "1px solid rgb(63,63,63)",
        "color": "#2186f4",
        "width": "1em",
        "height": "1em",
        "outline": "0",
        "padding": "0",
        "float": "left",
        "margin-right": "5px",
        'display': 'inline-flex'
        }
    app = dash.Dash(external_stylesheets=[
                    dbc.themes.DARKLY])  # set app layout
    df_vis = df.reset_index()
    list_of_method = ["IQR", "MAD", "SD", "rSD"]
    ls_method_with_html = []
    ls_distance = [2, 2.5, 3]
    ls_distance_with_html = []

    for method in list_of_method:
        ls_method_with_html.append({'label': html.Div(
            method, style={'font-size': 15, 
                           'padding-right': "0.5rem"}), 
                           'value': method})
    for num in ls_distance:
        ls_distance_with_html.append({'label': html.Div(
            str(num), style={'font-size': 15, 
                           'padding-right': "0.5rem"}), 
                           'value': num})

    fig = px.scatter(df,
                     x=df_vis.index,
                     y=column_to_vis[0])  # initialize app

    app.layout = html.Div(children=[
        html.H1('Outliers visualisation', style={
                'textAlign': 'center', "font-weight": "bold"}),
        html.Br(),
        # In this line, insert 3 columns
        dbc.Row(
            [dbc.Col(
                html.Div(
                    dcc.Dropdown(
                        options=[{'label': i, 'value': i}
                                 for i in column_to_vis],
                        value=str(column_to_vis[0]),
                        id='column',
                        style={"width": "50%", "offset": 1, },
                        clearable=False)
                )
            ),
                dbc.Col(html.Div(children=[
                    dcc.Checklist(options=ls_method_with_html,
                                  id="method",
                                  inputStyle=a)]),
                                  ),
                dbc.Col(html.Div(children=[
                    dcc.Checklist(options=ls_distance_with_html,
                                  value = [2],
                                  id="distance",
                                  style = a
                                  )]))]
        ),
        dcc.Graph(id='scatter', figure=fig)
    ])
    # callbacks
    # https://dash.plotly.com/duplicate-callback-outputs

    @app.callback(
        Output(component_id='scatter', component_property='figure'),
        Input(component_id='column', component_property='value'),
        Input(component_id='method', component_property='value'),
        Input(component_id='distance', component_property='value')
    )
    def update_graph(y, method, distance):
        triggered_id = dash.ctx.triggered_id

        # Debug
        print("Y", y)
        print("Method :", method)
        print("Distance : ", distance)

        fig = px.scatter(df, x=df.index, y=y)
        
        if triggered_id == 'method' or triggered_id == "distance":
            fig = update_threshold(df, fig, method, y, distance)

        return fig

    app.run_server(debug=True)

def update_threshold(df, fig, pre_method, y, distance):
    layout = {"showlegend":True}
    layout['shapes'] = []
    len_df = len(df.index)
    for met in pre_method:
        method = met.lower()
        func = config.DICT_FUNCTION[method]
        # give a default value when it is not input
        if distance == None:
            distance = [2]
        for dis in distance:
            if method == "mad":
                low_threshold, high_threshold = func(
                    df, [y], dis)
            else:
                low_threshold, high_threshold = func(
                    df, [y], dis)
            low_line = create_line_plotly(low_threshold, len_df, method)
            layout['shapes'].append(low_line)
            high_line = create_line_plotly(high_threshold, len_df, method)
            layout['shapes'].append(high_line)

    fig.update_layout(layout)

    return fig


def create_line_plotly(threshold, len_df, method):
    line={
        'type': 'line',
           'x0': 0,
           'y0': threshold,
           'x1': len_df,
           'y1': threshold,
           'line': {'color': f'{config.HEXA_FOR_PLOTLY[method]}','width': 4},
        }
    return line


