from otpsy.src import config

# Data visualisation
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Dashboard
import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash_bootstrap_templates import load_figure_template

load_figure_template('darkly')

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#222222",
}
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}
CHECKLIST_DISTANCE = {
    "color": "#FFFFFF",
    "width": "2em",
    "height": "1em",
    "outline": "0",
    "padding": "0",
    "float": "left",
    "margin-right": "5px",
    'display': 'inline-flex'
}

def main(df, column_to_vis):

    app = dash.Dash(__name__, external_stylesheets=[
                    dbc.themes.DARKLY])  # set app layout
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
                     x=df.reset_index().index,
                     y=column_to_vis[0],
                     hover_name=df.index)  # initialize app
    sidebar = html.Div(
                    [dbc.Col(
                        html.Div([
                            html.H4("Options"),
                                dbc.Row(html.Div([
                                    html.Hr(),
                                    html.P(
                                        "Select columns"),
                                    dcc.Dropdown(
                                        options=[{'label': i, 'value': i}
                                                for i in column_to_vis],
                                        value=str(column_to_vis[0]),
                                        id='column',
                                        className = "drop",
                                        clearable=False, multi=True
                                )])),
                                dbc.Row(
                                    html.Div([
                                        html.Hr(),
                                        html.P(
                                            "Select method"
                                        ),
                                        dbc.Checklist(options=ls_method_with_html,
                                            id="method",
                                            label_checked_style={"color": "#FFFFFF"},
                                            input_checked_style={
                                                "backgroundColor": "#324c71",
                                                "borderColor": "#324c71"}
                                )])),
                                dbc.Row(
                                    html.Div([
                                        html.Hr(),
                                        html.P(
                                            "Select distance"
                                        ),
                                        dbc.Checklist(options=ls_distance_with_html,
                                            value = [2],
                                            id="distance",
                                            style = CHECKLIST_DISTANCE
                                )]))
                        ]))], style=SIDEBAR_STYLE)
    
    content = html.Div([
        html.H1('Outliers visualisation', style={
                'textAlign': 'center', "font-weight": "bold "}),
        html.Br(),
        dcc.Graph(id='scatter', figure=fig)], style=CONTENT_STYLE)
    
    app.layout = html.Div(children=[sidebar, content]) 
    
    
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
        print(df[y[0]])
        fig = make_subplots(rows = len(y), cols= 1)
        for i in range(len(y)):
            fig.add_trace(
                go.Scatter(x = df.reset_index().index, 
                           y=df[y[i]],
                           hovertext=df.index, mode="markers",
                           xaxis=f"x{i+1}",
                           yaxis=f"y{i+1}"),
                           row=i+1, col=1)
        
        if triggered_id == 'method' or triggered_id == "distance":
            fig = update_threshold(df, fig, method, y, distance)
        
        fig.update_layout(
            margin=dict(l=30, r=30, t=30, b=20),
        )
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


