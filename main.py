import dash
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
from layout.layout import serve_layout
from server.titles import update_titles
from server.overview_section import OverviewIntensity
from server.types_section import Types
from server.initiators_section import Initiators
from server.query_data import QueryData
import os


DATABASE_URL = os.environ.get('DATABASE_URL')

db_query = QueryData(DATABASE_URL)
df = db_query.query_database()
subtype_df = db_query.get_subtype_data()
subtype_df = subtype_df.drop_duplicates()
df = db_query.preclean_data(df)
df = db_query.clean_initiators(df)
nb_incidents = df["id"].nunique()
df = db_query.clean_initiator_names(df)
db_query.dispose()
df["alpha_2_code"] = df["alpha_2_code"].fillna("unknown")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = serve_layout()


@app.callback(
    Output("total-incidents", "children"),
    Input("selected-country", "value"),
)
def update_total_incidents(selected_country):
    return [f"{nb_incidents} cyberattacks against critical infrastructure"]


update_titles(app)
overview_section_callbacks = OverviewIntensity(
    app=app,
    df=df,
    subtype_df=subtype_df,
    aggregate_graph_id="overview-section-aggregate-graph",
    bar_index_store_id='overview-section-bar-index-store',
    evolution_graph_id="overview-section-evolution-graph",
    bar_label_store_id="overview-section-bar-label-store",
    sunburst_chart_id="overview-section-sunburst-chart",
    reset_button="overview-section-reset-graphs",
)
types_section_callbacks = Types(
    app=app,
    df=df,
    aggregate_graph_id="types-section-aggregate-graph",
    aggregate_graph_title_year_id="types-section-aggregate-title-year",
    aggregate_graph_subtitle_id="types-section-aggregate-subtitle",
    impact_graph_id="types-section-impact-graph",
    impact_graph_title_year_id="types-section-impact-title-year",
    impact_graph_subtitle_id="types-section-impact-subtitle",
    intelligence_impact_graph_id="types-section-intelligence-impact-graph",
    intelligence_impact_graph_subtitle_id="types-section-intell-subtitle",
    functional_impact_graph_id="types-section-functional-impact-graph",
    functional_impact_graph_subtitle_id="types-section-functional-subtitle",
    techniques_dropdown_sectors_id="types-section-techniques-sectors-dropdown",
    techniques_dropdown_types_id="types-section-techniques-types-dropdown",
    techniques_graph_id="types-section-techniques-bar-chart",
    year_slider_id="types-section-year-slider",
    reset_button="types-section-reset-graphs",
    last_selected_stack="types-section-last-selected"
)
initiators_callbacks = Initiators(
    app=app,
    df=df,
    aggregate_graph_id="initiators-section-aggregate-graph",
    aggregate_graph_title_id="initiators-section-aggregate-sector-year",
    total_cyberattacks_id="initiators-section-total-cyberattacks",
    year_slider_id="initiators-section-year-slider",
    table_id="initiators-section-table",
    table_title_id="initiators-section-table-title-sector-year",
    conflicts_main_graph_id="initiators-section-conflicts-main-graph",
    conflicts_sectors_graph_id="initiators-section-conflicts-sectors-graph",
    conflicts_initiators_graph_id="initiators-section-conflicts-initiators-graph",
    conflicts_store_id="initiators-section-conflicts-initiators-store",
    date_range_picker_id="initiators-section-date-range-picker",
    reset_button="initiators-section-reset-graphs"
)

server = app.server
app.title = "EuRepoC Critical Infrastructure Tracker"

if __name__ == '__main__':
    app.run_server(host="0.0.0.0")
