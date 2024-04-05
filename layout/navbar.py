import dash_bootstrap_components as dbc
from dash import html


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(html.A(
            "Overview",
            href="#overview-section",
            style={"color": "black", "font-weight": "650", "text-decoration": "none", "font-size": "1.3em"}
        )),
        dbc.NavItem(html.A(
            "Type of incidents",
            href="#types-section",
            style={"color": "black", "font-weight": "650", "text-decoration": "none", "font-size": "1.3em"}
        )),
        dbc.NavItem(html.A(
            "Initiators",
            href="#initiators-section",
            style={"color": "black", "font-weight": "650", "text-decoration": "none", "font-size": "1.3em"}
        )),
    ],
    brand=html.Img(src="./assets/EuRepoC_logo.svg", height="60px"),
    brand_href="https://eurepoc.eu",
    color="rgba(0, 0, 0, 0);",
    links_left=True,
    expand="lg",
    style={"padding": "30px"},
    id="intro-section"
)
