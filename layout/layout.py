import dash_bootstrap_components as dbc
from layout.navbar import navbar
from layout.intro_section import intro_section
from layout.overview_section import overview_section
from layout.types_section import types_section
from layout.initiators_section import initiators_section
from layout.footer import footer
from dash import html
import dash_mantine_components as dmc
from dash_iconify import DashIconify


def serve_layout():
    full_layout = dbc.Container([
        html.Link(rel='icon', href='./assets/eurepoc-logo.png'),
        dbc.Row([
            navbar,
            intro_section
        ], class_name="transition-container transition-container-intro"),
        html.Div(id="overview-section"),
        overview_section,
        dbc.Row(className="transition-container transition-container-types"),
        html.Div(id="types-section"),
        types_section,
        dbc.Row(className="transition-container transition-container-initiators"),
        html.Div(id="initiators-section"),
        initiators_section,
        html.A(
            dmc.ActionIcon(
                DashIconify(icon="icon-park-outline:to-top", width=20),
                size="xl",
                variant="filled",
                id="action-icon",
                mb=10,
                style={"position": "fixed", "bottom": "20px", "right": "20px"}
            ),
            href="#intro-section"
        ),
        footer
    ], fluid=True)
    return full_layout
