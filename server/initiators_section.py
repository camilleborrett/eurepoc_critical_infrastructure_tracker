import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash import callback_context, html
import dash_bootstrap_components as dbc
from server.utils import filter_data, empty_figure, sectors_color_map, initiator_types_color_map
from io import StringIO


button_to_sector = {
    "all-button": None,
    "health-button": "Health",
    "energy-button": "Energy",
    "finance-button": "Finance",
    "telecom-button": "Telecommunications",
    "transportation-button": "Transportation",
    "defence-industry-button": "Defence industry",
    "research-button": "Research",
    "critical-manufacturing-button": "Critical Manufacturing",
    "digital-provider-button": "Digital Provider",
    "food-button": "Food",
    "water-button": "Water",
    "chemicals-button": "Chemicals",
    "space-button": "Space",
    "waste-water-management-button": "Waste Water Management"
}


def filter_data_initiators(df, click_button, selected_year, initiator_name=None):
    if click_button and click_button != "all-button":
        sector = button_to_sector[click_button]
        df = df[df["receiver_subcategory"] == sector]

    df["start_date"] = pd.to_datetime(df["start_date"])

    if initiator_name:
        if selected_year < 2025:
            grouper = [
                pd.Grouper(key="start_date", freq="YE"),
                "initiator_name",
                "alpha_2_code",
                "initiator_category_most_common",
                "type_clean_most_common",
                "initial_access_most_common"
            ]
        else:
            grouper = [
                "initiator_name",
                "alpha_2_code",
                "initiator_category_most_common",
                "type_clean_most_common",
                "initial_access_most_common"
            ]

        df_aggregated = df.groupby(grouper).agg({"id": "nunique"}).reset_index()
        df_aggregated.rename(columns={"id": "total"}, inplace=True)

        if selected_year < 2025:
            df_aggregated["year"] = df_aggregated["start_date"].dt.year
            df_top = df_aggregated[df_aggregated["year"] == selected_year]
            df_top = df_top[~df_top['initiator_name'].isin(["Not attributed", "Unknown", "Not available"])]
            df_top = df_top.sort_values(by="total", ascending=False)
            df_top = df_top.drop(columns=["year", "start_date"]).head(5)

        else:
            df_top = df_aggregated[
                ~df_aggregated['initiator_name'].isin(["Not attributed", "Unknown", "Not available"])]
            df_top = df_top.sort_values(by="total", ascending=False).head(5)

    else:
        if selected_year < 2025:
            grouper = [pd.Grouper(key="start_date", freq="YE"), "initiator_country", "initiator_category"]
        else:
            grouper = ["initiator_country", "initiator_category"]

        df_aggregated = df.groupby(grouper).agg({"id": "nunique"}).reset_index()
        df_aggregated.rename(columns={"id": "total"}, inplace=True)

        if selected_year < 2025:
            df_aggregated["year"] = df_aggregated["start_date"].dt.year
            df_top = df_aggregated[df_aggregated["year"] == selected_year]
            overall_totals = df_top.groupby('initiator_country')['total'].sum()
            top_countries = overall_totals.nlargest(10).index
            df_top = df_top[df_top['initiator_country'].isin(top_countries)]
            df_top = df_top.merge(overall_totals.rename('total_overall'), on='initiator_country')
        else:
            overall_totals = df_aggregated.groupby('initiator_country')['total'].sum()
            top_countries = overall_totals.nlargest(10).index
            df_top = df_aggregated[df_aggregated['initiator_country'].isin(top_countries)]
            df_top = df_top.merge(overall_totals.rename('total_overall'), on='initiator_country')

        df_top = df_top.sort_values(by=["total_overall", "total"], ascending=[True, True])

    return df_top


def conflict_sectors_graph(df, click_data=None, conflict_name=None):
    callback_data = df[df["conflict_name"] != "Not available"]
    if click_data:
        callback_data = callback_data[callback_data["conflict_name"] == conflict_name]
        selected_conflict = conflict_name
    else:
        selected_conflict = "All conflicts"
    if callback_data.empty:
        return empty_figure(), callback_data
    else:
        callback_data = callback_data.groupby(["receiver_subcategory"]).agg(
            {"id": "nunique"}).reset_index()
        callback_data['percent'] = callback_data['id'] / callback_data['id'].sum() * 100
        callback_data = callback_data.sort_values(by='percent', ascending=False)
        callback_data["conflict_name"] = selected_conflict

        fig = go.Figure(data=[
            go.Bar(
                name=category,
                y=[""],
                x=[percentage],
                text=f"{value}",
                textposition='auto',
                orientation='h',
                marker=dict(color=sectors_color_map.get(category, '#000000')),
                hovertemplate=f"<b>{category}</b><br>Percentage: {percentage:.2f}%<br>Number of incidents: {value}<extra>{selected_conflict}</extra>",
            )
            for category, percentage, value in zip(callback_data['receiver_subcategory'],
                                                   callback_data['percent'],
                                                   callback_data['id'])
        ])
        fig.update_layout(
            barmode='stack',
            xaxis=dict(
                ticksuffix='%',
                linecolor='rgba(225,225,225,0.4)',
                gridcolor='rgba(225,225,225,0.4)',
            ),
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=200,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-1.5,
                xanchor="auto",
                x=0,
                traceorder="normal",
            ),
        )
        return fig, callback_data


class Initiators:
    def __init__(
            self,
            app,
            df,
            aggregate_graph_id,
            aggregate_graph_title_id,
            year_slider_id,
            table_id,
            table_title_id,
            conflicts_main_graph_id,
            conflicts_sectors_graph_id,
            conflicts_initiators_graph_id,
            conflicts_store_id,
            reset_button
    ):
        self.app = app
        self.df = df
        self.aggregate_graph_id = aggregate_graph_id
        self.aggregate_graph_title_id = aggregate_graph_title_id
        self.year_slider_id = year_slider_id
        self.button_group_dict = button_to_sector
        self.table_id = table_id
        self.table_title_id = table_title_id
        self.conflicts_main_graph_id = conflicts_main_graph_id
        self.conflicts_sectors_graph_id = conflicts_sectors_graph_id
        self.conflicts_initiators_graph_id = conflicts_initiators_graph_id
        self.conflicts_store_id = conflicts_store_id
        self.reset_button = reset_button

        self.initialize_callbacks()

    def initialize_callbacks(self):
        self.active_button()
        self.generate_aggregate_plot()
        self.generate_main_conflict_graph()
        self.generate_sectors_conflict_graph()
        self.generate_initiators_conflict_graph()

    def active_button(self):
        @self.app.callback(
            [Output(key, "active") for key in self.button_group_dict.keys()],
            [Input(key, "n_clicks") for key in self.button_group_dict.keys()],
            [Input("active-button-store", "data")]
        )
        def update_button_active_state(*args):
            ctx = callback_context
            if not ctx.triggered:
                return [True] + [False] * (len(self.button_group_dict) - 1)
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            return [button_id == key for key in self.button_group_dict.keys()]

    def generate_aggregate_plot(self):
        @self.app.callback(
            Output(self.aggregate_graph_id, "figure"),
            Output(self.table_id, "children"),
            Output(self.aggregate_graph_title_id, "children"),
            Output(self.table_title_id, "children"),
            [Input(self.year_slider_id, "value"), Input("selected-country", "value")]
            + [Input(button_id, "n_clicks") for button_id in self.button_group_dict.keys()]
        )
        def update_aggregate_plot(year, selected_country, *args):
            callback_data = self.df.copy(deep=True)
            callback_data = filter_data(callback_data, selected_country)
            ctx = callback_context
            button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
            if button_id in self.button_group_dict.keys():
                df_filtered = filter_data_initiators(callback_data, button_id, year)
                df_table = filter_data_initiators(callback_data, button_id, year, initiator_name=True)
                sector = self.button_group_dict[button_id]
                if sector is None:
                    sector = "All sectors"
            else:
                df_filtered = filter_data_initiators(callback_data, "all-button", year)
                df_table = filter_data_initiators(callback_data, "all-button", year, initiator_name=True)
                sector = "All sectors"

            if df_filtered.empty:
                return empty_figure(), [], [], []

            else:

                df_filtered = df_filtered.sort_values(by='total_overall', ascending=False)
                stack_order = [
                    "Non-state-group", "Individual hacker(s)", "State affiliated actor",
                    "State", "Not attributed", "Unknown"
                ]

                if year == 2025:
                    year = "All years"

                fig = px.bar(
                    df_filtered,
                    x='total',
                    y='initiator_country',
                    color='initiator_category',
                    orientation='h',
                    color_discrete_map=initiator_types_color_map,
                    category_orders={
                        "initiator_country": df_filtered['initiator_country'].unique(),
                        "initiator_category": stack_order
                    },
                    hover_data={'initiator_category': True}
                )

                fig.update_traces(hovertemplate="Country of origin: %{y}<br>Initiator type: %{customdata[0]}<br>Number of incidents %{x}<extra></extra>")

                fig.update_layout(
                    xaxis_title="",
                    yaxis_title="",
                    legend_title="",
                    plot_bgcolor="rgba(0,0,0,0)",
                    barmode='stack',
                    xaxis=dict(
                        showgrid=True,
                        showline=True,
                        showticklabels=True,
                        zeroline=True,
                        linecolor='rgba(225,225,225,0.4)',
                        gridcolor='rgba(225,225,225,0.4)',
                    ),
                    height=570,
                    margin=dict(l=10, r=10, t=30, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                )

                list_group_items = []
                for index, row in df_table.iterrows():
                    item = dbc.ListGroupItem([
                        html.Span(html.Img(src=f"/assets/flag/{row['alpha_2_code'].lower()}.svg", style={"width": "25px"})),
                        html.B(f"   {row['initiator_name']} - {row['initiator_category_most_common']}"),
                        html.Br(),
                        html.Small(f"Nb of operations: {row['total']}"),
                        html.Br(),
                        html.Small(f"Top attack type: {row['type_clean_most_common']}"),
                        html.Br(),
                        html.Small(f"Top MITRE initial access method: {row['initial_access_most_common']}"),
                    ], style={"background-color": "rgba(248,249,250,0.5)", "border-color": "rgba(248,249,250,0.7)", 'font-size': '0.8rem'})
                    list_group_items.append(item)

                return fig, list_group_items, f"{sector} - {year}", f"{sector} - {year}"

    def generate_main_conflict_graph(self):
        @self.app.callback(
            Output(self.conflicts_main_graph_id, "figure"),
            [Input("selected-country", "value"),
             Input(self.conflicts_main_graph_id, "clickData"),
             Input(self.reset_button, "n_clicks")]
        )
        def update_main_conflict_graph(selected_country, click_data, reset_button):
            callback_data = self.df.copy(deep=True)
            callback_data = filter_data(callback_data, selected_country)
            callback_data = callback_data[callback_data["conflict_name"] != "Not available"]
            ctx = callback_context
            triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

            if callback_data.empty:
                return empty_figure()

            selected_segment = None
            if click_data:
                selected_segment = click_data['points'][0]['pointNumber']

            if triggered_id == self.reset_button or triggered_id == "selected-country":
                selected_segment = None

            callback_data = callback_data.groupby(["conflict_name"]).agg({"id": "nunique"}).reset_index()

            colors = ["#d63459" if i == selected_segment else "#668088" for i in range(len(callback_data))]
            line_colors = ["#cc0130" if i == selected_segment else "#002C38" for i in range(len(callback_data))]
            pull_values = [0.1 if i == selected_segment else 0 for i in range(len(callback_data))]

            fig = px.pie(callback_data, values='id', names='conflict_name', title='')
            fig.update_traces(textposition='inside', textinfo='percent+label+value',
                              marker=dict(colors=colors, line=dict(color=line_colors, width=1.5)),
                              pull=pull_values, hovertemplate="%{label}<br>%{value} incidents<extra></extra>")
            fig.update_layout(
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=520
            )
            return fig

    def generate_sectors_conflict_graph(self):
        @self.app.callback(
            Output(self.conflicts_sectors_graph_id, "figure"),
            Output(self.conflicts_store_id, "data"),
            Output("initiators-section-conflicts-sectors-title", "children"),
            [Input("selected-country", "value"),
             Input(self.conflicts_main_graph_id, "clickData"),
             Input(self.reset_button, "n_clicks")]
        )
        def update_sectors_conflict_graph(selected_country, click_data, reset_button):
            callback_data = self.df.copy(deep=True)
            callback_data = filter_data(callback_data, selected_country)

            ctx = callback_context
            triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

            if selected_country == "Global (states)":
                selected_country = "all countries"

            if callback_data.empty:
                return empty_figure(), {}, ""

            else:

                if triggered_id == self.reset_button or triggered_id == "selected-country":
                    fig, filtered_data = conflict_sectors_graph(callback_data)
                    return (fig,
                            filtered_data.to_json(orient='records'),
                            f"Critical infrastructure sectors targeted by cyber attacks linked to offline conflicts in {selected_country}")

                if click_data:
                    conflict_name = click_data['points'][0]['label']
                    fig, filtered_data = conflict_sectors_graph(callback_data, click_data=True, conflict_name=conflict_name)
                    return fig, filtered_data.to_json(orient='records'), f"Sectors targeted by cyber attacks linked to the {conflict_name} offline conflict in {selected_country}"

                else:
                    fig, filtered_data = conflict_sectors_graph(callback_data)
                    return (fig,
                            filtered_data.to_json(orient='records'),
                            f"Sectors targeted by cyber attacks linked to offline conflicts in {selected_country}")

    def generate_initiators_conflict_graph(self):
        @self.app.callback(
            Output(self.conflicts_initiators_graph_id, "figure"),
            Output("initiators-section-conflicts-initiators-title", "children"),
            [Input("selected-country", "value"),
             Input(self.conflicts_sectors_graph_id, "clickData"),
             Input(self.conflicts_store_id, "data")]
        )
        def update_initiators_conflict_graph(selected_country, click_data, data):
            callback_data = self.df.copy(deep=True)
            callback_data = filter_data(callback_data, selected_country)
            callback_data = callback_data[callback_data["conflict_name"] != "Not available"]

            ctx = callback_context
            triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

            if selected_country == "Global (states)":
                selected_country = "all countries"

            if callback_data.empty:
                return empty_figure(), ""
            else:
                if click_data and triggered_id != self.conflicts_store_id:
                    selected_sector_index = click_data['points'][0]['curveNumber']
                    stored_data = pd.read_json(StringIO(data))
                    selected_sector = stored_data["receiver_subcategory"][selected_sector_index]
                    selected_conflict = stored_data["conflict_name"][0]
                    if selected_conflict == "All conflicts":
                        callback_data = callback_data[callback_data["receiver_subcategory"] == selected_sector]
                    else:
                        callback_data = callback_data[
                            (callback_data["receiver_subcategory"] == selected_sector) &
                            (callback_data["conflict_name"] == selected_conflict)
                        ]
                elif click_data and triggered_id == self.conflicts_store_id:
                    stored_data = pd.read_json(StringIO(data))
                    selected_conflict = stored_data["conflict_name"][0]
                    if selected_conflict != "All conflicts":
                        callback_data = callback_data[
                            callback_data["conflict_name"] == selected_conflict
                        ]
                    selected_sector = "All sectors"
                elif not click_data and triggered_id == self.conflicts_store_id:
                    stored_data = pd.read_json(StringIO(data))
                    selected_sector = "All sectors"
                    selected_conflict = stored_data["conflict_name"][0]
                    if selected_conflict != "All conflicts":
                        callback_data = callback_data[
                            callback_data["conflict_name"] == selected_conflict
                        ]
                else:
                    selected_sector = "All sectors"
                    selected_conflict = "All conflicts"

                callback_data = callback_data.groupby(["initiator_country", "initiator_category"]).agg({"id": "nunique"}).reset_index()
                callback_data.rename(columns={"id": "total"}, inplace=True)
                overall_totals = callback_data.groupby('initiator_country')['total'].sum()
                top_countries = overall_totals.nlargest(10).index
                df_top = callback_data[callback_data['initiator_country'].isin(top_countries)]
                df_top = df_top.merge(overall_totals.rename('total_overall'), on='initiator_country')
                df_top = df_top.sort_values(by=["total_overall", "total"], ascending=[True, True])

                df_top = df_top.sort_values(by='total_overall', ascending=False)
                stack_order = [
                    "Non-state-group", "Individual hacker(s)", "State affiliated actor",
                    "State", "Not attributed", "Unknown"
                ]

                fig = px.bar(
                    df_top,
                    y='total',
                    x='initiator_country',
                    color='initiator_category',
                    color_discrete_map=initiator_types_color_map,
                    category_orders={
                        "initiator_country": df_top['initiator_country'].unique(),
                        "initiator_category": stack_order
                    },
                    hover_data={'initiator_category': True}
                )

                fig.update_traces(hovertemplate="Country of origin: %{y}<br>Initiator type: %{customdata[0]}<br>Number of incidents %{x}<extra></extra>")

                fig.update_layout(
                    xaxis_title="",
                    yaxis_title="",
                    legend_title="",
                    plot_bgcolor="rgba(0,0,0,0)",
                    barmode='stack',
                    xaxis=dict(
                        showgrid=True,
                        showline=True,
                        showticklabels=True,
                        zeroline=True,
                        linecolor='rgba(225,225,225,0.5)',
                        gridcolor='rgba(225,225,225,0.5)',
                    ),
                    yaxis=dict(
                        linecolor='rgba(225,225,225,0.6)',
                        gridcolor='rgba(225,225,225,0.6)',
                    ),
                    height=300,
                    margin=dict(l=10, r=10, t=30, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                )

                if selected_conflict != "All conflicts":
                    selected_conflict_title = f"the {selected_conflict} offline conflict"
                else:
                    selected_conflict_title = "offline conflicts"

                return (fig,
                        f"Initiators of cyber attacks linked to {selected_conflict_title} against {selected_sector.lower()} in {selected_country}")