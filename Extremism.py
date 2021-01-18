# Data
import os
import pathlib # file paths
import pandas as pd
import numpy as np

# Plotting
import plotly.express as px

# Dash application (JupyterDash)
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Load and clean data
data_file = 'CapitolHillTracker11721.xlsx'
sheet_name='Capitol Hill'
local_filepath = pathlib.Path(__file__).parent.absolute()
data_filepath = os.path.join(local_filepath,data_file)
extremism_data = pd.read_excel(data_filepath, sheet_name = sheet_name)

# get data for age of arrest in bins
age_arrest_names = ['<20','20-29','30-39','40-49','50-59','60-69','70-79','80+']
age_arrest_bins = [0, 19, 29, 39, 49, 59, 69, 79, np.inf]

#Get numeric column without the string 'Unknowns' in order to use the cut function for binning
extremism_data['age'] = [None if x =='Unknown' else x for x in extremism_data['agearrest']]
extremism_data['AgeRange'] = pd.cut(extremism_data['age'],age_arrest_bins, labels=age_arrest_names)
# Add 'Unknown' category back into the AgeRange column
extremism_data['AgeRange'] = extremism_data['AgeRange'].cat.add_categories('Unknown')
extremism_data['AgeRange'] = extremism_data['AgeRange'].fillna('Unknown')


# CHOROPLETH MAP
## Choropleth Map Data
states = extremism_data['state'].value_counts().to_frame().reset_index()
states.columns = ['State','Count']

## Choropleth Map Figure
map_fig = px.choropleth(data_frame = states,
                        locations='State',
                        color='Count',
                        locationmode="USA-states",
                        scope="usa",
                        color_continuous_scale='Greys',
                       title="Number of Cases per State of Residence")


# barchart data
bar_data = extremism_data.groupby(['gender','AgeRange']).size().reset_index(name='Gender_count')
bar_data_filtered = bar_data[bar_data['Gender_count'] > 0]
bar_data_filtered = bar_data_filtered.sort_values(by='AgeRange', ascending=False).sort_values(by='gender', ascending=False)

# barchart figure
bar_fig = px.bar(bar_data_filtered,
            y='AgeRange',
            x="Gender_count",
            color='gender',
            barmode='stack',
            orientation='h',
            color_discrete_sequence=['Grey','LightGrey'],
            title="Age at time of arrest",
            labels={ # replaces default labels by column name
                "gender": "Gender", 'AgeRange':'','Gender_count':''
            },
            )


# Build App
app = dash.Dash(external_stylesheets=[dbc.themes.SUPERHERO])

CONTENT_STYLE = {
    "padding": "2rem 1rem",
    "font-family": '"Times New Roman", Times, serif'
}


overview_message = 'Number of federal cases: ' + str(len(extremism_data))
note_message = ''' Note: The data depicted were collected from federal cases only.
A collection of individuals charged in the District of Columbia is available on the Program on Extremism's website,
but data were not gathered from these cases due to inconsistencies in available documents and reporting.'
'''

title_block = html.Div([
        html.H2('THE CAPITOL HILL SIEGE'),
        html.H4(overview_message),
        html.Div(note_message)
])

GWU_block = html.Div([
        html.H3('Program on Extremism'),
        html.H6('THE GEORGE WASHINGTON UNIVERSITY',style={'text-decoration': 'underline overline solid gold'}),
        html.P('Updated: January 17, 2021')
        ])

choropleth_map = html.Div(dcc.Graph(id='map',figure=map_fig))

bar_chart = html.Div(dcc.Graph(id='bar',figure=bar_fig))

app.layout = html.Div([
    dbc.Row([
        dbc.Col(title_block, width=8),
        dbc.Col(GWU_block)
    ]),
    dbc.Row([
        dbc.Col(choropleth_map),
        dbc.Col(bar_chart)
    ])
], style=CONTENT_STYLE)

# Run app and display result inline in the notebook
if __name__ == '__main__':
    app.run_server(debug=True,port=8055)
