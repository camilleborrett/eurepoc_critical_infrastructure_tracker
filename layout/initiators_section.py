import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from server.utils import graph_config, generate_year_slider
from datetime import datetime, date


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
    ], id="button-group", vertical=False
)


year_slider = generate_year_slider("initiators-section-year-slider")


initiators_section = dbc.Row([
    dbc.Row([
        dbc.Col([
            html.H2(
                id="initiators-section-main-title",
                style={"text-align": "center", "padding-top": "20px", "padding-bottom": "20px", "font-weight": "700"}),
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H3("What are the main threat actors targeting critical infrastructure?"),
            html.P([
                html.Span(),
                "Identifying the perpetrators of cyberattacks is a complex yet vital aspect of cybersecurity. \
                As part of our broader data collection ",
                html.A("methodology", href="https://eurepoc.eu/methodology/", target="_blank", style={"color": "black"}),
                html.Span(", we track attribution reports and update our data \
                as new information emerges. Although a large proportion of attacks remain unattributed, our data shows \
                the diverse array of threat actors that target critical infrastructure sectors, ranging from "),
                html.A("advanced persistent threats (APTs)", href="https://eurepoc.eu/advanced-persistent-threats-apts/", target="_blank", style={"color": "black"}),
                html.Span(", often state or state-sponsored groups, to independent \
                hacker groups and criminal networks. The threat landscape also differs from sector to sector \
                and overtime. The bar chart below displays the different types of initiators by country of origin \
                and a list of the most prolific threat actors. Use the buttons to compare sectors and/or years. \
                Please note again that a cyber operation can affect multiple target sectors."),
            ], style={"text-align": "left", "padding-top": "10px", "padding-bottom": "20px", "font-weight": "400"}
            )
        ], xl=10, md=12)
    ]),
    dbc.Row([
        dbc.Col([button_group]),
        dcc.Store(id="active-button-store", data="all-button"),
    ], style={"padding": "0px 40px 20px 40px", "text-align": "center"}),
    dbc.Row([
        dbc.Col([year_slider]),
    ], style={"padding": "10px 80px", "text-align": "center"}, className="hide-slider"),
    dbc.Row([
        dbc.Col([
            html.H5(id="initiators-section-aggregate-title", style={"text-align": "center"}),
            html.H6(id="initiators-section-aggregate-sector-year", style={"text-align": "center"}),
            dcc.Graph(
                id="initiators-section-aggregate-graph",
                config=graph_config("EuRepoC-Type-of-initiators-by-country-of-origin"),
                style={"height": "570px"}
            ),
            html.P([html.B("Total cyberattacks for selected year and sector: "), html.Span(id="initiators-section-total-cyberattacks")]),
        ], xl=7),
        dbc.Col([
            html.H5(id="initiators-section-table-title", style={"text-align": "center"}),
            html.H6(id="initiators-section-table-title-sector-year", style={"text-align": "center", "padding-bottom": "10px"}),
            dbc.ListGroup(id="initiators-section-table")
        ], xl=5),
    ], style={"padding-top": "20px"}),
    html.Div(html.Hr(style={"width": "50%"}), style={"text-align": "center", "padding": "20px"}),
    dbc.Row([
        dbc.Col([
            html.H3("How do cyberattacks against critical infrastructure fit into the broader geopolitical context?"),
            html.P([
                html.Span("In many cases, cyberattacks are not isolated incidents but linked to broader geopolitical \
                (offline) conflicts. Since January 2023, EuRepoC data tags cyberattacks linked to offline conflicts. \
                The conflict names are based on the "),
                html.A("Heidelberg Institute for International Conflict Research (HIIK)",
                       href="https://hiik.de/?lang=en", target="_blank", style={"color": "black"}),
                html.Span(" Conflict Barometer. The pie chart shows the number of incidents linked to different offline conflicts \
                for incidents added to the database "), html.Span(html.B("since January 2023")), html.Span(". The horizontal bar chart shows the proportion \
                of these incidents impacting each critical infrastructure sector, while the vertical bar chart shows \
                the types of inititiators attributed to these incidents. Click on a a section of the pie chart \
                to filter the data across the other charts for the chosen conflict. Similarly, by clicking on \
                a specific sector in the horizontal bar chart, you can view the attributed initiators specific \
                to that sector and selected conflict."),
            ], style={"text-align": "left", "padding-top": "10px", "font-weight": "400"}
            )
        ], xl=10, md=12),
    ]),
    dbc.Row([
        dbc.Col([
            html.Span(html.B("Select an incident start date range")),
            html.Br(),
            html.Small(html.I("Note that information on offline conflicts is recorded only for incidents added to the database since January 2023. However, these incidents may have a start date prior to 2023.")),
            dmc.DateRangePicker(
                id="initiators-section-date-range-picker",
                minDate=date(2000, 1, 1),
                value=[date(2000, 1, 1), datetime.now().date()],
                amountOfMonths=2,
                style={"width": 400},
            ),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.H5(id="initiators-section-conflicts-main-title", style={"text-align": "center"}),
            html.P([
                DashIconify(icon="mdi:cursor-default-click-outline", width=25, rotate=1),
                html.I(
                    " Click on a section of the pie chart to filter the data across the other charts for the chosen conflict.",
                    style={"font-size": "0.8rem"}
                ),
            ], style={"text-align": "center"}),
            dcc.Graph("initiators-section-conflicts-main-graph",
                      config=graph_config("EuRepoC-number-of-cyber-attacks-linked-to-offline-conflicts"),
                      style={"height": "600px"}),
        ], xl=6, style={"padding-top": "20px"}),
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.H5(id="initiators-section-conflicts-sectors-title", style={"text-align": "center"}),
                html.P([
                    DashIconify(icon="mdi:cursor-default-click-outline", width=25, rotate=1),
                    html.I(
                    " Click on a sector to display the attributed inititaors for the selected sector and conflict.",
                    style={"font-size": "0.8rem"}
                ),
                ], style={"text-align": "center"}),
                    dcc.Graph("initiators-section-conflicts-sectors-graph",
                              config=graph_config("EuRepoC-sectors-targeted-by-cyber-attacks-linked-to-offline-conflicts"),
                              style={"height": "200px"}
                    )
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                    html.H5(id="initiators-section-conflicts-initiators-title", style={"text-align": "center", "padding-top": "20px"}),
                    dcc.Graph("initiators-section-conflicts-initiators-graph",
                              config=graph_config("EuRepoC-type-of-initiators-of-cyber-attacks-linked-to-offline-conflicts"),
                              style={"height": "300px"}
                    ),
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
            ], style={"padding-top": "20px"})
        ], xl=6, style={"padding-top": "20px"})
    ], style={"padding-bottom": "20px"}),
], className="background-container background-container-initiators page-padding")
