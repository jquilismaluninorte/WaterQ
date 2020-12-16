import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_table as dt
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
import branca
import chardet
import folium
import geopandas
from scipy import stats
import os

content=html.Div(['Hello'],style={'width': '100%'})
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.config.suppress_callback_exceptions = True
app.layout=html.Div(content)


if __name__== '__main__':
    app.run_server(debug=True)
