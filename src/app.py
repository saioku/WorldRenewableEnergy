import dash
from dash import dcc, html
import pandas as pd
import plotly.graph_objs as go

# Load data from CSV
df = pd.read_csv('global-data-on-sustainable-energy.csv')

# Define app
app = dash.Dash(__name__)
server = app.server

top_5_total_energy_consumption = df.groupby('Entity')[['Electricity from fossil fuels (TWh)', 'Electricity from nuclear (TWh)', 'Electricity from renewables (TWh)']].sum().sum(axis=1).nlargest(5)

# Define figure 2: Energy distribution for top 5 countries
fig1 = go.Figure()

energy_columns = ['Electricity from fossil fuels (TWh)', 'Electricity from nuclear (TWh)', 'Electricity from renewables (TWh)']

top_5_countries = top_5_total_energy_consumption.index.tolist()
top_5_data = df[df['Entity'].isin(top_5_countries)].groupby('Entity')[energy_columns].sum()

for column in energy_columns:
    fig1.add_trace(go.Bar(
        x=top_5_countries,
        y=top_5_data[column],
        name=column
    ))

fig1.update_layout(barmode='stack', title='Energy distribution for top 5 countries', legend_title_text='Top & Bottom 5 Countries', legend=dict(traceorder='normal'))

#Defining figure 2
fig2 = go.Figure()

energy_columns = ['Electricity from fossil fuels (TWh)', 'Electricity from nuclear (TWh)', 'Electricity from renewables (TWh)']

bottom_5_total_energy_consumption = df.groupby('Entity')[['Electricity from fossil fuels (TWh)', 'Electricity from nuclear (TWh)', 'Electricity from renewables (TWh)']].sum().sum(axis=1).nsmallest(5)

bottom_5_countries = bottom_5_total_energy_consumption.index.tolist()
bottom_5_data = df[df['Entity'].isin(bottom_5_countries)].groupby('Entity')[energy_columns].sum()

for column in energy_columns:
    fig2.add_trace(go.Bar(
        x=bottom_5_countries,
        y=bottom_5_data[column],
        name=column
    ))

fig2.update_layout(barmode='stack', title='Energy distribution for bottom 5 countries', showlegend=False)

# Define figure 3: Renewable energy share of all countries
fig3 = go.Pie(
    labels=df['Entity'],
    values=df['Renewable energy share in the total final energy consumption (%)'],
    name='Renewable energy share',
    hoverinfo='label+percent',
    textinfo='none'
)

fig3_layout = {
    'title': 'Renewable Energy Share of All Countries',
    'margin': {'l': 250, 'r': 50, 't': 50, 'b': 50} 
}

# Define figure 4: Scatter plot with dropdown menu
fig4 = go.Figure()

# Define initial data
x_data = df['Electricity from fossil fuels (TWh)']
y_data = df['Value_co2_emissions_kt_by_country']

fig4.add_trace(go.Scatter(
    x=x_data,
    y=y_data,
    mode='markers',
    marker=dict(
        size=8,
        color='blue'
    ),
    name='Data'
))

fig4.update_layout(
    title='Electricity from fossil fuels vs Value_co2_emissions_kt_by_country',
    xaxis_title='Electricity from fossil fuels (TWh)',
    yaxis_title='Value_co2_emissions_kt_by_country'
)

# Define figure 5: Scatter plot with slider
fig5 = go.Figure()

# Initial data for the first year
initial_year = df['Year'].min()
initial_data = df[df['Year'] == initial_year]

fig5.add_trace(go.Scatter(
    x=initial_data['Renewables (% equivalent primary energy)'],
    y=initial_data['gdp_per_capita'],
    mode='markers',
    marker=dict(
        size=8,
        color='green'
    ),
    name=str(initial_year)
))

fig5.update_layout(
    title='Renewables vs GDP',
    xaxis_title='Renewables (% equivalent primary energy)',
    yaxis_title='GDP per capita',
    sliders=[{
        'currentvalue': {'prefix': 'Year: '},
        'steps': [{'label': str(year), 'method': 'update', 'args': [{'x': [df[df['Year'] == year]['Renewables (% equivalent primary energy)']], 'y': [df[df['Year'] == year]['gdp_per_capita']]}]} for year in df['Year'].unique()]
    }]
)

# Define layout
app.layout = html.Div(children=[
    html.H1(children='Energy Visualization Dashboard', style={'textAlign': 'center'}),

    html.Div(children=[
        html.Div(children='''
        ''', style={'width': '50%', 'display': 'inline-block'}),
        html.Div(children='''
        ''', style={'width': '50%', 'display': 'inline-block'}),
    ]),

    html.Div(children=[
        dcc.Graph(
            id='figure-1',
            figure=fig1,
            style={'width': '50%', 'display': 'inline-block'}
        ),
        dcc.Graph(
            id='figure-2',
            figure=fig2,
            style={'width': '50%', 'display': 'inline-block'}
        ),
    ]),

    html.Div(children=''),
    dcc.Graph(
        id='figure-3',
        figure={
            'data': [fig3],
            'layout': fig3_layout
        }
    ),

    html.Div(children=[
        html.Div([
            dcc.Dropdown(
                id='dropdown-parameters',
                options=[
                    {'label': 'Value of CO2 emissions vs GDP', 'value': 'co2_vs_gdp'},
                    {'label': 'Renewable energy share in total vs GDP', 'value': 'renewable_share_vs_gdp'},
                    {'label': 'Electricity from fossil fuels vs GDP', 'value': 'fossil_fuel_vs_gdp'}
                ],
                value='co2_vs_gdp'
            )
        ],
        style={'width': '50%', 'display': 'inline-block'}),
    ]),

    dcc.Graph(
        id='figure-4'
    ),

    dcc.Graph(
        id='figure-5',
        figure=fig5
    )
], style={'textAlign': 'center'})


# Define callback function to update scatter plot based on dropdown selection
@app.callback(
    dash.dependencies.Output('figure-4', 'figure'),
    [dash.dependencies.Input('dropdown-parameters', 'value')]
)
def update_figure(selected_parameter):
    fig4 = go.Figure()

    if selected_parameter == 'co2_vs_gdp':
        x_data = df['gdp_per_capita']
        y_data = df['Value_co2_emissions_kt_by_country']
        x_label = 'GDP per capita'
        y_label = 'Value of CO2 emissions (kt)'
    elif selected_parameter == 'renewable_share_vs_gdp':
        x_data = df['gdp_per_capita']
        y_data = df['Renewable energy share in the total final energy consumption (%)']
        x_label = 'GDP per capita'
        y_label = 'Renewable energy share (%)'
    elif selected_parameter == 'fossil_fuel_vs_gdp':
        x_data = df['gdp_per_capita']
        y_data = df['Electricity from fossil fuels (TWh)']
        x_label = 'GDP per capita'
        y_label = 'Electricity from fossil fuels (TWh)'

    fig4.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode='markers',
        marker=dict(
            size=8,
            color='blue'
        ),
        name='Data'
    ))

    fig4.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label
    )

    return fig4


if __name__ == '__main__':
    app.run_server(debug=True)
