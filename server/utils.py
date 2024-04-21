import plotly.graph_objects as go
from dash import dcc
import pandas as pd
from datetime import datetime


sectors_color_map = {
    "Finance": "#002C38",
    "Health": "#CC0130",
    "Transportation": "#79443b",
    "Energy": "#0094bd",
    "Telecommunications": "#89BD9E",
    "Defence industry": "#f4b942",
    "Critical Manufacturing": "#7272AB",
    "Digital Provider": "#CB904D",
    "Chemicals": "#F7F0F5",
    "Food": "#3E1929",
    "Research": "#847e89",
    "Space": "#F5E0B7",
    "Water": "#eb99ac",
    "Waste Water Management": "#779FA1"
}


initiator_types_color_map = {
    "State affiliated actor": "#6e977e",
    "Non-state-group": "#cc0130",
    "Not attributed": "#847e89",
    "Unknown": "#cecbd0",
    "Individual hacker(s)": "#e06783",
    "State": "#002C38",
}


incident_types_color_map = {
    "full_opacity": {
        "Data theft": "rgba(0,44,56,1)",
        "DDoS/Defacement": "rgba(204,1,48,1)",
        "Ransomware": "rgba(137,189,158,1)",
        "Wiper": "rgba(51,134,157,1)",
        "Hack and leak": "rgba(244,185,66,1)",
        "Other": "rgba(157,152,161,1)"
    },
    "low_opacity": {
        "Data theft": "rgba(0,44,56,0.4)",
        "DDoS/Defacement": "rgba(204,1,48,0.4)",
        "Ransomware": "rgba(137,189,158,0.4)",
        "Wiper": "rgba(51,134,157,0.4)",
        "Hack and leak": "rgba(244,185,66,0.4)",
        "Other": "rgba(157,152,161,0.4)"
    }
}


def generate_year_slider(id_name=None):
    year_slider = dcc.Slider(
        id=id_name,
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
    return year_slider


def filter_data(df, selected_country, selected_year=None, date_range=None):
    states_codes = {
        "Global (states)": None,
        "Asia (states)": "ASIA",
        "Central America (states)": "CENTAM",
        "Central Asia (states)": "CENTAS",
        "Collective Security Treaty Organization (states)": "CSTO",
        "EU (member states)": "EU",
        "Eastern Asia (states)": "EASIA",
        "Europe (states)": "EUROPE",
        "Gulf Countries (states)": "GULFC",
        "Mena Region (states)": "MENA",
        "Middle East (states)": "MEA",
        "NATO (member states)": "NATO",
        "North Africa (states)": "NAF",
        "Northeast Asia (states)": "NEA",
        "Oceania (states)": "OC",
        "Shanghai Cooperation Organisation (states)": "SCO",
        "South Asia (states)": "SASIA",
        "South China Sea (states)": "SCS",
        "Southeast Asia (states)": "SEA",
        "Sub-Saharan Africa (states)": "SSA",
        "Western Balkans (states)": "WBALKANS",
        "Africa (states)": "AFRICA",
    }

    if selected_country in states_codes.keys():
        selected_country = states_codes[selected_country]
        if selected_country and selected_country != "Global (states)":
            df = df[df["region_name"] == selected_country]
        else:
            df = df

    else:
        df = df[df["receiver_country"] == selected_country]

    if selected_year and selected_year != 2025:
        df["start_date"] = pd.to_datetime(df["start_date"])
        df = df[df["start_date"].dt.year == selected_year]

    if date_range:
        if date_range[0] == "2000-01-01" and date_range[1] == str(datetime.now().date()):
            df = df
        else:
            df["start_date"] = pd.to_datetime(df["start_date"])
            df = df[(df["start_date"] >= date_range[0]) & (df["start_date"] <= date_range[1])]

    return df


def empty_figure(height_value=400):
    fig = go.Figure()
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=height_value,
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        annotations=[
            go.layout.Annotation(
                x=2,
                y=2,
                text="<i>No incidents corresponding to your selection</i>",
                showarrow=False,
                font=dict(
                    family="Lato",
                    size=16,
                    color="black"
                )
            )
        ]
    )
    return fig


def graph_config(image_name):
    config = {
        "displayModeBar": True,
        "scrollZoom": False,
        "responsive": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["zoom2d", "pan2d", "select2d", "lasso2d",
                                   "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d",
                                   "hoverClosestCartesian", "hoverCompareCartesian", "zoom3d",
                                   "pan3d", "resetCameraDefault3d", "resetCameraLastSave3d",
                                   "hoverClosest3d", "orbitRotation", "tableRotation", "zoomInGeo",
                                   "zoomOutGeo", "resetGeo", "hoverClosestGeo", "sendDataToCloud",
                                   "hoverClosestGl2d", "hoverClosestPie", "toggleHover", "resetViews",
                                   "toggleSpikelines", "resetViewMapbox"],

        "toImageButtonOptions": {
            "format": 'png',  # one of png, svg, jpeg, webp
            "filename": image_name,
            "height": 600,
            "width": 800,
            "scale": 1
        }
    }
    return config
