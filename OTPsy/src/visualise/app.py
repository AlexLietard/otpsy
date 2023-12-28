""" Design of the visualisation of data 

"""

from otpsy.src import config

# Data visualisation
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from numpy import histogram, argmax, isnan

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
    'overflowY': 'auto'
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
    ls_graph = ["Scatter", "Histogram"]
    ls_graph_with_html = []

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
    for type in ls_graph:
        ls_graph_with_html.append({'label': html.Div(
            type, style={'font-size': 15, 
                         'padding-right': "0.5rem",
                         'color': "#FFFFFF"}), 
                         'value': type})

    fig = px.scatter({'data':[]})  # initialize app
    sidebar = html.Div(
                    [dbc.Col(
                        html.Div([
                            html.H4("Options"),
                            # in this column, there are 4 rows, starting with a line,
                            # followed by the name of the category and options
                            # Columns to show
                                dbc.Row(html.Div([
                                    html.Hr(),
                                    html.P(
                                        "Select columns"),
                                    dcc.Dropdown(
                                        options=[{'label': i, 'value': i}
                                                for i in column_to_vis],
                                        id='column',
                                        className = "drop",
                                        clearable=False, multi=True
                                )])),
                                # Method to use
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
                                # Distance to use
                                dbc.Row(
                                    html.Div([
                                        html.Hr(),
                                        html.P(
                                            "Select distance"
                                        ),
                                        dbc.Checklist(options=ls_distance_with_html,
                                            id="distance",
                                            style = CHECKLIST_DISTANCE
                                )])),
                                dbc.Row(
                                    html.Div([
                                        html.Hr(),
                                        html.P(
                                            "Select graph type"
                                        ),
                                        dcc.Dropdown(
                                            options=ls_graph_with_html,
                                            id="graph",
                                            value = "Scatter",
                                            className = "drop"
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
        Input(component_id='distance', component_property='value'),
        Input(component_id="graph", component_property='value')
    )
    def update_graph(y, method, distance, graph_type):
        # allow to know which subplot corresponds to the method
        ref = {}
        max_frequency = {}
        if y == None or len(y) == 0:
            fig = px.scatter({'data': []})
            # number_of_subplots = 1 because the value of number_of_subplots 
            # is used to increase the height_of_figure containing the subplot.
            # I increase the height_of_figure for each subplot added
            # with : height_of_figure = height_of_a_subplot * number_of_subplots. 
            # However, if there is no column (y == None), height_of_figure can't be 0.
            number_of_subplots = 1
        elif graph_type == "Scatter":
            title_of_subplots = [f"Scatter plot of {col}" for col in y]
            fig = make_subplots(rows=len(y), 
                                cols= 1, 
                                subplot_titles=title_of_subplots,
                                vertical_spacing=0.12)
            for i, column in enumerate(y):
                fig.add_trace(
                    go.Scatter(
                        x=df.reset_index().index, 
                        y=df[column],
                        hovertemplate= f'Index: %{{text}}<extra></extra><br>' \
                                    f'Row number: %{{x}}<br>{column}: %{{y}}<br>',
                        text=df.index,
                        mode="markers",
                        xaxis=f"x{i+1}",
                        yaxis=f"y{i+1}"),
                        row=i+1, col=1)
                fig.update_xaxes(title="Row Number")
                fig.update_yaxes(title=column)
                ref[column] = i + 1
            
            fig = update_threshold(df, fig, method, y, distance, ref, graph_type, "")
            number_of_subplots = i + 1
        
        elif graph_type == "Histogram":
            title_of_subplots = [f"Histogram plot of {col}" for col in y]
            fig = make_subplots(rows=len(y), 
                                cols= 1, 
                                subplot_titles=title_of_subplots,
                                vertical_spacing=0.12)
            for i, column in enumerate(y):
                max_frequency_for_a_column = create_hist_numpy(df, column)
                fig.add_trace(
                    go.Histogram(
                        x=df[column], 
                        xaxis=f"x{i+1}",
                        yaxis=f"y{i+1}"),
                        row=i+1, col=1,
                        )
                fig.update_xaxes(title=column)
                fig.update_yaxes(title="Count")
                ref[column] = i + 1
                max_frequency[column] = max_frequency_for_a_column
            
            fig = update_threshold(df, fig, method, y, distance, ref, graph_type, max_frequency)

            number_of_subplots = i + 1
        height_of_one_plot = 400
        
        fig.update_layout(
            height = height_of_one_plot*number_of_subplots,
            width = 900,
            margin=dict(l=30, r=30, t=30, b=20),
            showlegend = False
        )
        return fig

    app.run_server(debug=True)

def create_hist_numpy(df, column):
    col = df[column][~isnan(df[column])]
    hist, bin_edges = histogram(col, bins='auto')
    max_frequency=hist[argmax(hist)]
    return max_frequency


def update_threshold(df, fig, pre_method, y, distance, ref, graph_type, max_frequency):
    layout = {"showlegend":True}
    layout['shapes'] = []
    if pre_method == None or distance == None:
        return fig
    for column in y:
        for met in pre_method:
            method = met.lower()
            func = config.DICT_FUNCTION[method]
            # give a default value when it is not input
            if distance == None:
                distance = [2]
            for dis in distance:
                if method == "mad":
                    low_threshold, high_threshold = func(
                        df, [column], dis)
                else:
                    low_threshold, high_threshold = func(
                        df, [column], dis)
                low_line = create_line_plotly(low_threshold, df[column], method, ref[column], graph_type, max_frequency)
                layout['shapes'].append(low_line)
                high_line = create_line_plotly(high_threshold, df[column], method, ref[column], graph_type, max_frequency)
                layout['shapes'].append(high_line)

    fig.update_layout(layout)

    return fig


def create_line_plotly(threshold, column, method, reference, graph_type, max_frequency):
    """
    Create horizontal (or vertical) line on the scatter (histogram) 
    plot to represent the threshold corresponding to distance.
    """
    x0 = 0 if graph_type == "Scatter" else threshold
    y0 = threshold if graph_type == "Scatter" else 0
    x1 = len(column) if graph_type == "Scatter" else threshold
    y1 = threshold if graph_type == "Scatter" else max_frequency[column.name]
    line={
        'type': 'line',
        'xref': f'x{reference}',
        'yref': f'y{reference}',
        'x0': x0,
        'y0': y0,
        'x1': x1,
        'y1': y1,
        'line': {'color': f'{config.HEXA_FOR_PLOTLY[method]}','width': 4},
    }
    return line


