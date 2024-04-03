from dash import html
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc


footer = dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.A(html.Img(src="./assets/EuRepoC_white_logo.svg", height="70px"),
                               href="https://eurepoc.eu/", target="_blank"),
                    ], md=12),
                    dbc.Col([
                        html.A("eurepoc.eu", href="https://eurepoc.eu/",
                               style={"padding-top": "10px", "color": "white", "font-size": "small"}),
                    ], md=12),
                ]),
            ], md=3, style={"text-align": "center", 'display': 'flex', 'align-items': 'center',
                            'justify-content': 'center'}
            ),
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.P([html.B("About us")]),
                        html.P([
                            html.A("Contact us", href="https://eurepoc.eu/feedback/",
                                   target="_blank", style={"color": "white"}),
                            html.Br(),
                            html.A("Consortium", href="https://eurepoc.eu/about-us/#consortium",
                                   target="_blank", style={"color": "white"}),
                            html.Br(),
                            html.A("Researchers", href="https://eurepoc.eu/about-us/#researchers",
                                   target="_blank", style={"color": "white"})
                        ]),
                    ], md=6),
                    dbc.Col([
                        html.P([html.B("Legal")]),
                        html.P([
                            html.A("Legal Notice", href="https://eurepoc.eu/legal-notice/",
                                   target="_blank", style={"color": "white"}),
                            html.Br(),
                            html.A("Privacy Policy", href="https://eurepoc.eu/privacy-policy/",
                                   target="_blank", style={"color": "white"}),
                        ]),
                    ], md=6),
                ]),
            ], md=3, style={
                "text-align": "left",
                'display': 'flex',
                'align-items': 'center',
                'justify-content': 'center',
            }),
            dbc.Col([
                html.Img(src="./assets/logo_grid.svg", height="150px")
            ], md=3, style={
                "text-align": "left",
                'display': 'flex',
                'align-items': 'center',
                'justify-content': 'left',
            }),
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        html.A(
                            dmc.Button(
                        "Subscribe to our newsletter",
                            color="white",
                            size="sm",
                            ),
                            href="https://eurepoc.eu/cyber-trackers/",
                            target="_blank",
                            style={"color": "white"}
                            )
                    ], md=12),
                    dbc.Col([
                        dmc.Group(
                            [
                                html.P([html.B("Follow us")], style={"margin-top": "15px", "padding-left": "10px"}),
                                html.A(
                                    DashIconify(icon="ri:twitter-x-fill", width=30, color="white"),
                                    href="https://twitter.com/EuRepoC",
                                    target="_blank",
                                ),
                                html.A(
                                    DashIconify(icon="ri:linkedin-box-fill", width=30, color="white"),
                                    href="https://www.linkedin.com/company/eurepoc/",
                                    target="_blank",
                                ),
                                html.A(
                                    DashIconify(icon="ri:bluesky-fill", width=30, color="white"),
                                    href="https://bsky.app/profile/eurepoc.bsky.social",
                                    target="_blank",
                                ),
                            ],
                        ),
                    ], md=12),
                ]),
            ], md=3, style={
                "text-align": "left",
                'display': 'flex',
                'align-items': 'center',
                'justify-content': 'center',
            })
    ], style={"padding": "20px 80px", "backgroundColor": "#002C38", "color": "white"})
