import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from server.utils import graph_config


button_group = dbc.ButtonGroup(
    [
        dbc.Button("All", id="all-button", color="primary"),
        dbc.Button("Health", id="health-button", color="primary"),
        dbc.Button("Finance", id="finance-button", color="primary"),
        dbc.Button("Telecom", id="telecom-button", color="primary"),
        dbc.Button("Transportation", id="transportation-button", color="primary"),
        dbc.Button("Energy", id="energy-button", color="primary"),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem("Defence industry", id="defence-industry-button"),
                dbc.DropdownMenuItem("Research", id="research-button"),
                dbc.DropdownMenuItem("Critical Manufacturing", id="critical-manufacturing-button"),
                dbc.DropdownMenuItem("Digital Provider", id="digital-provider-button"),
                dbc.DropdownMenuItem("Food", id="food-button"),
                dbc.DropdownMenuItem("Water", id="water-button"),
                dbc.DropdownMenuItem("Chemicals", id="chemicals-button"),
                dbc.DropdownMenuItem("Space", id="space-button"),
                dbc.DropdownMenuItem("Waste Water Management", id="waste-water-management-button"),
            ],
            label="More",
            group=True,
            color="primary",
            id="more-dropdown"
        ),
    ],
)


year_slider = dcc.Slider(
    id='year-slider',
    min=2010,
    max=2025,
    value=2025,
    marks={
        2010: {'label': '2010'},
        2011: {'label': ''},
        2012: {'label': '2012'},
        2013: {'label': ''},
        2014: {'label': '2014'},
        2015: {'label': ''},
        2016: {'label': '2016'},
        2017: {'label': ''},
        2018: {'label': '2018'},
        2019: {'label': ''},
        2020: {'label': '2020'},
        2021: {'label': ''},
        2022: {'label': '2022'},
        2023: {'label': ''},
        2024: {'label': '2024'},
        2025: {'label': 'All Years', 'style': {'transform': 'rotate(-45deg)', 'white-space': 'nowrap'}}
    },
    step=1
)


initiators_section = dbc.Row([
    dbc.Row([
        dbc.Col([
            html.H2(
                id="initiators-section-main-title",
                style={"text-align": "center", "padding-top": "20px", "padding-bottom": "20px", "font-weight": "700"}),
            html.H3("What are the main threat actors targeting critical infrastructure? "),
            html.P(
                "This section focused on the main targeted critical infrastructure sectors. The bar chart shows the aggregate number \
                of attacks recorded by EuRepoC per sector since 2000. The timeline shows the rolling average number of attacks \
                publicly disclosed over 30 days since January 2023, along with the rolling average intensity of these \
                attacks also over 30 days. Click on the bars to display and compare the timeline for each sector.",
                style={"text-align": "left", "padding": "10px 150px 10px 0px", "font-weight": "400"}
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([button_group]),
        dcc.Store(id="active-button-store", data="all-button"),
    ], style={"padding": "0px 40px 20px 40px", "text-align": "center"}),
    dbc.Row([
        dbc.Col([year_slider]),
    ], style={"padding": "10px 80px", "text-align": "center"}),
    dbc.Row([
        dbc.Col([
            html.H5(id="initiators-section-aggregate-title", style={"text-align": "center"}),
            html.H6(id="initiators-section-aggregate-sector-year", style={"text-align": "center"}),
            dcc.Graph(id="initiators-section-aggregate-graph",
                      config=graph_config("EuRepoC-Type-of-initiators-by-country-of-origin")),
        ], md=7),
        dbc.Col([
            html.H5(id="initiators-section-table-title", style={"text-align": "center"}),
            html.H6(id="initiators-section-table-title-sector-year", style={"text-align": "center", "padding-bottom": "10px"}),
            dbc.ListGroup(id="initiators-section-table")
        ], md=5),
    ], style={"padding-top": "20px"}),
    html.Div(html.Hr(style={"width": "50%"}), style={"text-align": "center", "padding": "20px"}),
    dbc.Row([
        dbc.Col([
            html.H3("How do cyber attacks against critical infrastructure fit into the broader geopolitical context?"),
            html.P(
                "This section focused on the main targeted critical infrastructure sectors. The bar chart shows the aggregate number \
                of attacks recorded by EuRepoC per sector since 2000. The timeline shows the rolling average number of attacks \
                publicly disclosed over 30 days since January 2023, along with the rolling average intensity of these \
                attacks also over 30 days. Click on the bars to display and compare the timeline for each sector.",
                style={"text-align": "left", "padding": "10px 150px 20px 0px", "font-weight": "400"}
            )
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.H5(id="initiators-section-conflicts-main-title", style={"text-align": "center"}),
            dcc.Graph("initiators-section-conflicts-main-graph",
                      config=graph_config("EuRepoC-number-of-cyber-attacks-linked-to-offline-conflicts"))
        ], md=6),
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.H5(id="initiators-section-conflicts-sectors-title", style={"text-align": "center"}),
                    dcc.Graph("initiators-section-conflicts-sectors-graph",
                              config=graph_config("EuRepoC-sectors-targeted-by-cyber-attacks-linked-to-offline-conflicts"))
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                    html.H5(id="initiators-section-conflicts-initiators-title", style={"text-align": "center", "padding-top": "20px"}),
                    dcc.Graph("initiators-section-conflicts-initiators-graph",
                              config=graph_config("EuRepoC-type-of-initiators-of-cyber-attacks-linked-to-offline-conflicts")),
                    dcc.Store("initiators-section-conflicts-initiators-store"),
                    html.Div([
                        dmc.Button([
                            "Reset graphs",
                            ],
                            id="initiators-section-reset-graphs",
                            variant="outline",
                            leftIcon=DashIconify(icon="fluent:arrow-reset-24-filled"),
                            color="grey",
                            size="sm",
                        ),
                    ], style={"text-align": "right"}),
                ]),
            ])
        ])
    ])
], style={"padding": "20px 80px"}, className="background-container background-container-initiators")
