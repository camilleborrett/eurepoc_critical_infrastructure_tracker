from dash import html, dcc
import pickle


receiver_countries_dd_options = pickle.load(open("./data/receiver_countries_dd.pickle", "rb"))


intro_section = html.Div([
    html.Div([
        html.Div([
            html.H1("Critical Infrastructure Tracker", style={'textAlign': 'center'}),
            html.H3(
                "Monitoring cyberattacks against critical infrastructure",
                style={'textAlign': 'center', 'font-weight': '600', 'padding-top': '10px'}
            ),
            html.P(
                "Cyberattacks on critical infrastructure represent a significant threat to society and \
                national security, as they impact crucial/essential systems from power grids, transportation networks to hospitals \
                and banking services. As critical infrastructure sectors become increasingly digitialised \
                and interconnected, they also become increasingly vulnerable to malicous cyber activities.",
                style={'font-weight': '400', "text-align": "left", 'padding-top': '10px'},
                className="hidden-on-mobile"
            ),
            html.P([
                "The EuRepoC database currently contains ",
                html.B(id='total-incidents'),
                " worldwide from the year 2000 to today (with a more systematic data collection since 2023)."
            ]),
            html.P("Our data shows the 'visible tip of the iceberg' of cyberattacks, focusing only on publicly \
            disclosed attacks. While there are likely many more undisclosed/covert cyberattacks not covered by \
            this analysis, we believe that the disclosed attacks are the most significant in shaping cybersecurity \
            policies and public awareness. This tracker focuses on the most targeted critical infrastructure \
            sectors overtime, the type of attacks and techniques used by threat actors along with the main attributed \
            cyber threat actors behind these attacks. By default the page shows worldwide data however you can display \
            all graphs for your chosen country or region.",
                   style={'font-weight': '400', "text-align": "left"},
                   className="hidden-on-mobile"
                   ),
            html.P(
                "Select a target country/region and dive into the data:",
                style={"font-weight": "600", "text-align": "center", 'padding-top': '10px'}
            ),
            html.Div([
                dcc.Dropdown(
                    id='selected-country',
                    options=receiver_countries_dd_options,
                    value="Global (states)",
                    clearable=False
                ),
            ], style={'margin': 'auto', 'width': '50%'})
        ], className="overlay-text"),
    ], className="custom-margin"),
    html.Br(),
    html.Div([
        html.Img(src="./assets/arrows-down.gif", height="60px")
    ], style={"text-align": "center"}, className="hidden-on-mobile")
])
