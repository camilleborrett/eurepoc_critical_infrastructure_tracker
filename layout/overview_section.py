import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from server.utils import graph_config


overview_section = dbc.Row([
    dbc.Row([
        dbc.Col([
            html.H2(
                id="overview-section-main-title",
                style={"text-align": "center", "padding-top": "20px", "padding-bottom": "20px", "font-weight": "700"}
            ),
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H3("What are the most frequently targeted critical infrastructure sectors?"),
            html.P([
                "The bar chart displays the aggregate number of cyberattacks recorded by EuRepoC per sector \
                since January 2000. The accompanying timeline shows the average number of cyberattacks disclosed \
                each day, calculated over a rolling period of 30 days from a given point in time, along with the rolling ",
                html.A("average intensity",
                       href="https://eurepoc.eu/methodology/#intensity-indicator",
                       target="_blank",
                       style={"color": "black"}
                ),
                " of attacks. A straight line at any value, such as 1, indicates a constant average number of disclosed incidents \
                per day over time. Please note that the timeline only includes incidents publicly disclosed \
                since January 2023, due to a change in methodology. Click on the bars to display and compare \
                the timeline data for each sector. Click the toggle button under the timeline graph to display the \
                cumulative number of incidents disclosed since January 2023 as opposed to the rolling average."
            ], style={"text-align": "left", "padding-top": "10px", "padding-bottom": "20px", "font-weight": "400"}
            )
        ], xl=10, md=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.H5(id="overview-section-aggregate-graph-title", style={"text-align": "center"}),
            dcc.Store(id="overview-section-bar-index-store", data=[]),
            html.P([
                DashIconify(icon="mdi:cursor-default-click-outline", width=25, rotate=1),
                html.I(
                    " Click on sectors in the bar chart to display the timeline for the selected sector(s)",
                    style={"font-size": "0.8rem"}
                ),
            ], style={"text-align": "center"}),
            dcc.Graph(
                id="overview-section-aggregate-graph",
                config=graph_config("EuRepoC_top_targeted_critical_infrastructure_sectors"),
                style={"height": "480px"}
            ),
            html.P(html.I("Note that one incident may target multiple sectors."),
                   style={"text-align": "center", "font-size": "0.8rem"}),
        ], xl=6),
        dbc.Col([
            html.H5(id="overview-section-evolution-graph-title", style={"text-align": "center", 'margin-bottom': '2.8rem'}),
            dcc.Store(id="overview-section-bar-label-store", data=[]),
            dcc.Graph(
                id="overview-section-evolution-graph",
                config=graph_config("EuRepoC_targeted_critical_infrastructure_sectors_timeline"),
                style={"height": "480px"}
            ),
            html.Div([
                dmc.Switch(
                    id="toggle-switch",
                    onLabel="Cumulative count",
                    offLabel="Rolling average",
                    size="lg",
                    radius="sm",
                    color="grey"
                )
            ], style={"padding-top": "20px"}),
            html.Div([
                dmc.Button([
                    "Reset graphs",
                    ],
                    id="overview-section-reset-graphs",
                    variant="outline",
                    leftIcon=DashIconify(icon="fluent:arrow-reset-24-filled"),
                    color="grey",
                    size="sm",
                ),
            ], style={"text-align": "right"}),
        ], xl=6)
    ]),
    html.Div(html.Hr(style={"width": "50%", "weight": "500"}), style={"text-align": "center", "padding": "20px 10px"}),
    dbc.Row([
        dbc.Col([
            html.H3("What type of companies/organisations are most affected for each sector?"),
            html.P(
                "The pie chart shows the types of organisations within each critical infrastructure sector \
                most targeted by cyberattacks. As opposed to the bar chart above which shows the number of incidents \
                per sector, the pie shows the number of targeted organisations per sector, where a single incident may \
                affect multiple organisations within the same sector. Please note, however, that for some cyber \
                operations no specific targeted organisations could be identified on the basis of the publicly \
                disclosed information, but only the broader targeted sector. Such cases are counted as one \
                organisation in the chart below, often as 'Unknown'. Click on a section on a sector on the pie to expand the \
                graph for that sector.",
                style={"text-align": "left", "padding-top": "10px", "padding-bottom": "20px", "font-weight": "400"}
            )
        ], xl=10, lg=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id="overview-section-sunburst-chart",
                config=graph_config("EuRepoC_targeted_organisation_types_per_sector"),
            )
        ], style={"height": "510px"})
    ], style={"padding-bottom": "20px"}),
], className="background-container background-container-overview page-padding")
