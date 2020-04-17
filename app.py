import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import plotly.express as px
import pandas as pd
from static_data import APP_DESCRIPTION, APP_TITLE, REQUEST_TYPES, REQUEST_SUBTYPES, \
                        volunteer_data, agent_info, select_volunteer_info, match_volunteer_info, df_to_table
## TO-DO
## fake location data
## update agent volunteer info



app    = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
server = app.server

# Fake Map Graph
mapbox_access_token = open("mapbox_token").read()
px.set_mapbox_access_token(mapbox_access_token)
df = volunteer_data
fig = px.scatter_mapbox(df, lat="centroid_lat", lon="centroid_lon", color="availability", size="availability",
                  color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=12)

# layout = dict(
#     autosize=True,
#     automargin=True,
#     margin=dict(l=30, r=30, b=20, t=40),
#     hovermode="closest",
#     plot_bgcolor="#F9F9F9",
#     paper_bgcolor="#F9F9F9",
#     legend=dict(font=dict(size=10), orientation="h"),
#     title="Satellite Overview",
#     mapbox=dict(
#         accesstoken=mapbox_access_token,
#         style="light",
#         center=dict(lon=-78.05, lat=42.54),
#         zoom=7,
#     ),
# )

# Environment Variables
request_types = [{'label': item[0], 'value': item[1]} for item in REQUEST_TYPES.items()]
request_subtypes = [{'label': subtype, 'value': subtype} for type in REQUEST_SUBTYPES.values() for subtype in type]
intro_text    = APP_DESCRIPTION
title_text    = APP_TITLE

# App Layout
app.layout = html.Div(
    [
        dcc.Store(id="volunteer_data"),
        html.Div(id="output-clientside"),
        # Header row
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src="./assets/sf-logo.png",
                            id="sf-logo",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    [dcc.Markdown(title_text)],
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    'State Farm helps life go right, even in a pandemic', 
                                    style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),                                
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        # Description textbox
        html.Div(
            [
                html.Div(
                    [
                        html.Details(
                            id="intro-text",
                            open=True,
                            children=[html.Summary(html.B("About This App")), dcc.Markdown(intro_text)],
                            )
                    ],
                    className="pretty_container twelve columns"
                )
            ],
            className="row flex-display"
        ),
        # Search bar
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            html.B("Select Your Need:  ")
                        ),
                        dcc.RadioItems(
                            id="request_type_selector",
                            options=[{"label": "All ", "value": "all"}] +
                                [{"label": key, "value": val} for (key, val) in REQUEST_TYPES.items()],
                            value="all",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),                
                        dcc.Dropdown(
                            id="request_types",
                            options=request_subtypes,
                            multi=True,
                            value=[subtype for type in REQUEST_SUBTYPES.values() for subtype in type],
                            className="dcc_control",
                        ),                        
                        html.P(
                            html.B("Enter You Address:  ")
                        ),
                        dcc.Input(
                            placeholder="Try '11 Wall Street, New York, NY'",
                            id="map-address-filter",
                            value="",
                            style={'width': "100%"}
                        )
                    ],
                    className="pretty_container twelve columns"
                )
            ],
            className="row flex-display",
        ),
        # Map
        html.Div(
            [
                html.Div(
                    [dcc.Graph(figure=fig, id="main_graph")],
                    className="pretty_container twelve columns",
                ),
            ],
            className="row flex-display",
        ),
        # Two side-by-side text boxes
        html.Div(
            [
                html.Div(        
                    [html.P([html.B('Local Agent Information')]),
                     dash_table.DataTable(
                                        id='agent_table',
                                        style_cell={'textAlign': 'center'},
                                        columns=[{"name": i, "id": i} for i in agent_info.columns],
                                        data=df_to_table(agent_info))
                    ],
                    className="pretty_container six columns",
                    ),
                html.Div(        
                    [html.P([html.B('Volunteer Information')]), 
                     html.P('Best Match Volunteer:'),
                     dash_table.DataTable(
                                        id='match_volunteer_table',
                                        style_cell={'textAlign': 'center'},                                        
                                        columns=[{"name": i, "id": i} for i in match_volunteer_info.columns],
                                        data=df_to_table(match_volunteer_info)),
                     html.P('Your Selected Volunteer:'),
                     dash_table.DataTable(
                                        id='select_volunteer_table',
                                        style_cell={'textAlign': 'center'},                                        
                                        columns=[{"name": i, "id": i} for i in select_volunteer_info.columns],
                                        data=df_to_table(select_volunteer_info))
                    
                    ],
                    className="pretty_container six columns",
                    ),
            ],
            className="row flex-display",
        ),

        
    ])


# Radio items - Select/filter tasks 
@app.callback(Output("request_types", "value"), [Input("request_type_selector", "value")])
def display_type(selector):
    if selector == "all":
        return [subtype for type in REQUEST_SUBTYPES.values() for subtype in type]
    
    elif selector in REQUEST_SUBTYPES.keys():
        return REQUEST_SUBTYPES[selector]
    
    return []

@app.callback(
        Output('select_volunteer_table', 'data'),
        [Input('main_graph', 'clickData')])
def select_volunteer(clickdata):
    if clickdata is None:
        data = pd.DataFrame({'Name': [''],
                            'Phone': [''],
                            'Availability': [['']],
                            'Going to Stores': [['']]
                           })

    else:
        idx = clickdata['points'][0]["pointIndex"]
        select_volunteer = volunteer_data.iloc[[idx], :]
        data = pd.DataFrame({'Name': ["No. {}".format(idx)],
                            'Phone': ['222-111-0000'],
                            'Availability': [['2020-04-31', '2020-05-32']],
                            'Going to Stores': [['Whole Foods', 'Aldi']]
                           })    
    
    return df_to_table(data)


if __name__ == '__main__':
    app.run_server(debug=True)

