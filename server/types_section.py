from dash.dependencies import Input, Output, State
import dash
import plotly.graph_objects as go
import re
from server.utils import filter_data, empty_figure, incident_types_color_map, incident_types_symbol_map


chosen_types = ["Data theft", "DDoS/Defacement", "Ransomware", "Wiper", "Hack and leak", "Other"]


evolution_plot_layout = {
    "xaxis_title": "",
    "yaxis_title": '',
    "legend_title": "",
    "plot_bgcolor": 'rgba(0,0,0,0)',
    "paper_bgcolor": 'rgba(0,0,0,0)',
    "xaxis": {
        "showgrid": True,
        "showline": True,
        "showticklabels": True,
        "zeroline": False,
        "linecolor": 'rgba(225,225,225,0.4)',
        "gridcolor": 'rgba(225,225,225,0.4)',
        "rangeslider": {
            "bgcolor": 'rgba(225,225,225,0.4)',
            "bordercolor": 'rgba(225,225,225,0.5)',
        },
        "rangeselector": {
            "buttons": list([
                dict(count=1, label="Last 30 days", step="month", stepmode="backward"),
                dict(count=6, label="Last 6 months", step="month", stepmode="backward"),
                dict(count=1, label="Year to date", step="year", stepmode="todate"),
                dict(count=1, label="Last year", step="year", stepmode="backward"),
                dict(label="All time", step="all")
            ]),
        },
    },
    "yaxis": {
        "showgrid": True,
        "showline": True,
        "showticklabels": True,
        "zeroline": False,
        "linecolor": 'rgba(225,225,225,0.4)',
        "gridcolor": 'rgba(225,225,225,0.4)',
    },
    "margin": {'l': 10, 'r': 10, 't': 10, 'b': 10},
    "height": 430
}


class Types:
    def __init__(
            self,
            app=None,
            df=None,
            intensity=False,
            aggregate_graph_id=None,
            bar_index_store_id=None,
            evolution_graph_id=None,
            techniques_dropdown_sectors_id=None,
            techniques_dropdown_types_id=None,
            techniques_graph_id=None,
            reset_button=None
    ):
        self.app = app
        self.df = df
        self.intensity = intensity
        self.aggregate_graph_id = aggregate_graph_id
        self.bar_index_store_id = bar_index_store_id
        self.evolution_graph_id = evolution_graph_id
        self.techniques_graph_id = techniques_graph_id
        self.techniques_dropdown_sectors_id = techniques_dropdown_sectors_id
        self.techniques_dropdown_types_id = techniques_dropdown_types_id
        self.reset_button = reset_button

        self.initialize_callbacks()

    def initialize_callbacks(self):
        self.bar_selection()
        self.aggregate_graph()
        self.evolution_graph()
        self.techniques_graph()

    def bar_selection(self):
        @self.app.callback(
            [Output(self.bar_index_store_id, 'data')],
            [Input(self.aggregate_graph_id, 'clickData'),
             Input('selected-country', 'value'),
             Input(self.reset_button, 'n_clicks')],
            [State(self.bar_index_store_id, 'data')]
        )
        def update_selected_stacks(clickdata, selected_country, reset_button, selected_stacks_index):
            if selected_stacks_index is None:
                selected_stacks_index = []

            ctx = dash.callback_context

            input_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if input_id == 'selected-country':
                return [[]]

            elif input_id == self.reset_button:
                return [[]]

            elif clickdata:
                hover_info = clickdata['points'][0]['hovertext']
                type_match = re.search(r"Type: (.*?)<br>", hover_info)
                sector_match = re.search(r"Sector: (.*?)<br>", hover_info)
                clicked_identifier = f"{type_match.group(1)}; {sector_match.group(1)}"

                if clicked_identifier in selected_stacks_index:
                    selected_stacks_index.remove(clicked_identifier)
                else:
                    selected_stacks_index.append(clicked_identifier)

                return [selected_stacks_index]

            return [[]]

    def aggregate_graph(self):
        @self.app.callback(
            Output(self.aggregate_graph_id, "figure"),
            [Input("selected-country", "value"),
             Input(self.bar_index_store_id, 'data')]
        )
        def update_aggregate_graph(selected_country, selected_stacks):
            df_clean = self.df.copy(deep=True)
            df_clean = filter_data(df_clean, selected_country)
            if df_clean.empty:
                return empty_figure()
            else:
                df_clean = df_clean.groupby(["receiver_subcategory", "type_clean"]).agg(
                    {"id": "nunique", "weighted_intensity": "mean"}).reset_index()
                grouped_df = df_clean.groupby(['receiver_subcategory', 'type_clean']).sum().reset_index()
                total_count_per_sector = grouped_df.groupby('receiver_subcategory')['id'].sum()
                grouped_df = grouped_df.merge(total_count_per_sector, on='receiver_subcategory', suffixes=('', '_total'))
                grouped_df['percentage'] = grouped_df['id'] / grouped_df['id_total'] * 100
                grouped_df = grouped_df.sort_values(by='id_total', ascending=True)
                pivot_df = grouped_df.pivot(index='receiver_subcategory', columns='type_clean', values='percentage').fillna(0)
                pivot_df = pivot_df[[incident_type for incident_type in chosen_types if incident_type in pivot_df.columns]]
                pivot_df = pivot_df.reindex(total_count_per_sector.sort_values(ascending=True).index)
                counts_dict = {(row['receiver_subcategory'], row['type_clean']): row['id']
                               for _, row in grouped_df.iterrows()}

                bars = [
                    go.Bar(
                        name=incident_type,
                        x=pivot_df[incident_type],
                        y=pivot_df.index,
                        orientation='h',
                        hovertext=[
                            f"Type: {incident_type}<br>Sector: {sector}<br>{percentage:.2f}% ({counts_dict.get((sector, incident_type), 0)})"
                            for sector, percentage in zip(pivot_df.index, pivot_df[incident_type])
                        ],
                        hoverinfo='text',
                        marker=dict(color=incident_types_color_map[incident_type]),
                    ) for incident_type in pivot_df.columns
                ]

                fig = go.Figure(data=bars)

                fig.update_layout(
                    barmode='stack',
                    title='',
                    xaxis_title='Percentage',
                    xaxis_ticksuffix='%',
                    yaxis_title='',
                    legend_title='Type of attack',
                    legend=dict(traceorder='normal'),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin={'l': 10, 'r': 10, 't': 10, 'b': 10},
                    height=455
                )

                return fig

    def evolution_graph(self):
        @self.app.callback(
            Output(self.evolution_graph_id, 'figure'),
            Input('selected-country', 'value'),
            Input(self.bar_index_store_id, 'data'),
        )
        def generate_timeline(selected_country, selected_bars):
            callback_data = self.df.copy(deep=True)
            callback_data = filter_data(callback_data, selected_country)
            if callback_data.empty:
                return empty_figure()
            else:
                fig = go.Figure()
                if selected_bars and len(selected_bars) > 0:
                    for bar in selected_bars:
                        selected_type, selected_sector = [x.strip() for x in bar.split(";")]
                        sector_data = callback_data[callback_data["type_clean"] == selected_type]
                        sector_data = sector_data[sector_data["receiver_subcategory"] == selected_sector]
                        sector_data = sector_data.groupby(['added_to_db']).agg({"id": "nunique", "weighted_intensity": "mean"}).reset_index()
                        sector_data['value_moving_avg'] = sector_data['id'].rolling(window=30, min_periods=1).mean()
                        sector_data['intensity_moving_avg'] = sector_data['weighted_intensity'].rolling(window=30, min_periods=1).mean()
                        hovertemplate_count = 'Date: %{x}<br>Incident count: %{text}<br>Moving average over 30 days: %{y:.1f}<extra></extra>'
                        fig.add_trace(
                            go.Scatter(
                                x=sector_data['added_to_db'],
                                y=sector_data['value_moving_avg'],
                                mode='lines+markers',
                                name=f'{selected_sector} - {selected_type}',
                                text=sector_data['id'],
                                line=dict(color=incident_types_color_map[selected_type], width=1, dash='dash'),
                                marker=dict(color=incident_types_color_map[selected_type], symbol=incident_types_symbol_map[selected_sector], size=7),
                                hovertemplate=hovertemplate_count
                            )
                        )
                        fig.update_layout(showlegend=True)
                        fig.update_xaxes(rangeslider_visible=True)
                        fig.update_layout(**evolution_plot_layout)
                else:
                    fig = go.Figure()
                    callback_data = callback_data.groupby(['added_to_db', "type_clean"]).agg(
                        {"id": "nunique", "weighted_intensity": "mean"}).reset_index()
                    callback_data['value_moving_avg'] = callback_data['id'].rolling(window=30, min_periods=1).mean()
                    callback_data['intensity_moving_avg'] = callback_data['weighted_intensity'].rolling(window=30, min_periods=1).mean()
                    hovertemplate_count = 'Date: %{x}<br>Incident count: %{text}<br>Moving average over 30 days: %{y:.1f}<extra></extra>'
                    for incident_type in callback_data['type_clean'].unique():
                        fig.add_trace(
                            go.Scatter(
                                x=callback_data[callback_data['type_clean'] == incident_type]['added_to_db'],
                                y=callback_data[callback_data['type_clean'] == incident_type]['value_moving_avg'],
                                mode='lines',
                                text=callback_data[callback_data['type_clean'] == incident_type]['id'],
                                name=incident_type,
                                marker=dict(color=incident_types_color_map[incident_type]),
                                hovertemplate=hovertemplate_count
                            )
                        )
                    fig.update_layout(showlegend=True)
                    fig.update_xaxes(rangeslider_visible=True)
                    fig.update_layout(**evolution_plot_layout)

                return fig

    def techniques_graph(self):
        @self.app.callback(
            Output(self.techniques_graph_id, 'figure'),
            [Input('selected-country', 'value'),
             Input(self.techniques_dropdown_sectors_id, 'value'),
             Input(self.techniques_dropdown_types_id, 'value')]
        )
        def generate_techniques_graph(selected_country, selected_sector, selected_type):
            callback_data = self.df.copy(deep=True)
            callback_data = filter_data(callback_data, selected_country)
            if callback_data.empty:
                return empty_figure()
            else:
                if selected_sector != "all":
                    callback_data = callback_data[callback_data["receiver_subcategory"] == selected_sector]
                if selected_type != "all":
                    callback_data = callback_data[callback_data["type_clean"] == selected_type]

                callback_data = callback_data.groupby("initial_access").agg({"id": "nunique"}).reset_index()
                callback_data = callback_data.sort_values(by="id", ascending=False)
                callback_data = callback_data[callback_data["initial_access"] != "Not available"]

                fig = go.Figure(data=[go.Bar(x=callback_data["initial_access"], y=callback_data["id"])])
                fig.update_traces(marker_color='#668088', marker_line_color='#002C38',
                                  marker_line_width=1.5, opacity=1, hovertemplate='%{x}<br>%{y} incidents<extra></extra>')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    barcornerradius=8,
                    yaxis=dict(
                        title='Number of incidents',
                        showgrid=True,
                        showline=True,
                        showticklabels=True,
                        zeroline=False,
                        linecolor='rgba(225,225,225,0.9)',
                        gridcolor='rgba(225,225,225,0.9)',
                    ),
                    margin={'l': 10, 'r': 10, 't': 10, 'b': 10}
                )
                return fig
