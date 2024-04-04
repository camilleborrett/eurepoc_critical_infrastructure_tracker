from dash.dependencies import Input, Output, State
from dash import ctx
import plotly.graph_objects as go
import re
import json
from server.utils import filter_data, empty_figure, incident_types_color_map


chosen_types = ["Data theft", "DDoS/Defacement", "Ransomware", "Wiper", "Hack and leak", "Other"]


intell_category_array_list = [
    'No data breach/corruption/leak',
    'Minor data breach',
    'Moderate data breach',
    'Significant data breach',
    'Major data breach',
    'Unknown'
]


functional_category_array_list = [
    'No system interference/disruption',
    'Day (< 24h)',
    "Days (< 7 days)",
    'Weeks (< 4 weeks)',
    'Months',
    'Not available'
]


def generate_impact_graph(data=None, clicked_category=None, clicked_type=None, click_data=None):
    if click_data:
        data = data[
            (data["receiver_subcategory"] == clicked_category) &
            (data["type_clean"] == clicked_type)
            ]

    df_group = data.groupby("impact").agg({"id": "nunique"}).reset_index()
    df_group = df_group.sort_values(by="id", ascending=False)

    fig = go.Figure(data=[go.Bar(x=df_group["impact"], y=df_group["id"])])
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
        margin={'l': 10, 'r': 10, 't': 10, 'b': 10},
        height=300
    )

    return fig


def generate_impact_type_graph(data=None, impact_type=None, text_column=None, marker_color=None, marker_line_color=None, category_array_list=None):
    if text_column:
        agg_data = data.groupby([impact_type, text_column]).agg({"id": "nunique"}).reset_index()
        hover_texts = agg_data[text_column]
    else:
        agg_data = data.groupby(impact_type).agg({"id": "nunique"}).reset_index()
        hover_texts = agg_data['id']

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=agg_data[impact_type],
        y=agg_data['id'],
        hovertext=hover_texts,
        marker_color=marker_color,
        marker_line_color=marker_line_color,
        marker_line_width=1.5,
        hovertemplate='<b>%{x}</b><br>%{hovertext}<br>%{y} incidents<extra></extra>' if text_column else '<b>%{x}</b><br>%{y} incidents<extra></extra>',
        opacity=1
    ))

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            categoryorder='array',
            categoryarray=category_array_list
        ),
        yaxis=dict(
            showgrid=True,
            showline=True,
            showticklabels=True,
            zeroline=False,
            linecolor='rgba(225,225,225,0.9)',
            gridcolor='rgba(225,225,225,0.9)',
        ),
        margin={'l': 10, 'r': 10, 't': 10, 'b': 10},
        bargap=0.1,
        barcornerradius=8,
        height=300
    )

    return fig


def filter_data_click_data(data=None, category=None, type=None, last_selected=None, impact_click_data=None):
    if last_selected != "null" and impact_click_data:
        filtered_data = data[(data["receiver_subcategory"] == category) & (data["type_clean"] == type) & (data["impact"] == impact_click_data)]
    elif last_selected == "null" and impact_click_data:
        filtered_data = data[data["impact"] == impact_click_data]
    elif last_selected != "null" and not impact_click_data:
        filtered_data = data[(data["receiver_subcategory"] == category) & (data["type_clean"] == type)]
    else:
        filtered_data = data
    return filtered_data


class Types:
    def __init__(
            self,
            app=None,
            df=None,
            intensity=False,
            aggregate_graph_id=None,
            impact_graph_id=None,
            intelligence_impact_graph_id=None,
            functional_impact_graph_id=None,
            techniques_dropdown_sectors_id=None,
            techniques_dropdown_types_id=None,
            techniques_graph_id=None,
            reset_button=None,
            last_selected_stack=None
    ):
        self.app = app
        self.df = df
        self.intensity = intensity
        self.aggregate_graph_id = aggregate_graph_id
        self.impact_graph_id = impact_graph_id
        self.intelligence_impact_graph_id = intelligence_impact_graph_id
        self.functional_impact_graph_id = functional_impact_graph_id
        self.techniques_graph_id = techniques_graph_id
        self.techniques_dropdown_sectors_id = techniques_dropdown_sectors_id
        self.techniques_dropdown_types_id = techniques_dropdown_types_id
        self.reset_button = reset_button
        self.last_selected = None
        self.last_selected_stack = last_selected_stack

        self.initialize_callbacks()

    def initialize_callbacks(self):
        self.aggregate_graph()
        self.impact_types_graphs()
        self.techniques_graph()

    def aggregate_graph(self):
        @self.app.callback(
            Output(self.aggregate_graph_id, "figure"),
            Output(self.impact_graph_id, "figure"),
            Output(self.last_selected_stack, "data"),
            [Input("selected-country", "value"),
             Input(self.aggregate_graph_id, 'clickData'),
             Input(self.reset_button, 'n_clicks')],
            [State(self.aggregate_graph_id, 'figure')]
        )
        def update_aggregate_graph(selected_country, clickData, n_clicks, aggregate_fig):
            df_filtered = self.df.copy(deep=True)
            df_filtered = filter_data(df_filtered, selected_country)

            if ctx.triggered[0]['prop_id'] == self.reset_button:
                self.last_selected = None

            if df_filtered.empty:
                return empty_figure(), empty_figure(), []
            else:
                df_clean = df_filtered.groupby(["receiver_subcategory", "type_clean"]).agg(
                    {"id": "nunique", "weighted_intensity": "mean"}).reset_index()
                grouped_df = df_clean.groupby(['receiver_subcategory', 'type_clean']).sum().reset_index()
                total_count_per_sector = grouped_df.groupby('receiver_subcategory')['id'].sum()
                grouped_df = grouped_df.merge(total_count_per_sector, on='receiver_subcategory',
                                              suffixes=('', '_total'))
                grouped_df['percentage'] = grouped_df['id'] / grouped_df['id_total'] * 100
                grouped_df = grouped_df.sort_values(by='id_total', ascending=True)
                pivot_df = grouped_df.pivot(index='receiver_subcategory', columns='type_clean',
                                            values='percentage').fillna(0)
                pivot_df = pivot_df[
                    [incident_type for incident_type in chosen_types if incident_type in pivot_df.columns]]
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
                        marker=dict(color=incident_types_color_map["full_opacity"][incident_type]),
                    ) for incident_type in pivot_df.columns
                ]

                aggregate_fig = go.Figure(data=bars)

                aggregate_fig.update_layout(
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
                    height=600
                )

                impact_fig = generate_impact_graph(data=df_filtered)

                if clickData:
                    clicked_category = clickData['points'][0]['y']
                    hover_info = clickData['points'][0]['hovertext']
                    type_match = re.search(r"Type: (.*?)<br>", hover_info)
                    clicked_type = type_match.group(1) if type_match else None

                    if [clicked_type, clicked_category] == self.last_selected:
                        for i, trace in enumerate(aggregate_fig['data']):
                            trace['marker']['color'] = [incident_types_color_map["full_opacity"][trace['name']] for _ in
                                                        trace['y']]
                        self.last_selected = None
                        impact_fig = generate_impact_graph(
                            data=df_filtered
                        )
                    else:
                        highlight_color = incident_types_color_map["full_opacity"][clicked_type]
                        for i, trace in enumerate(aggregate_fig['data']):
                            if trace['name'] == clicked_type:
                                trace['marker']['color'] = [
                                    highlight_color if category == clicked_category else
                                    incident_types_color_map["low_opacity"][
                                        clicked_type]
                                    for category in trace['y']
                                ]
                            else:
                                trace['marker']['color'] = [
                                    incident_types_color_map["low_opacity"][trace['name']] for _ in trace['y']
                                ]
                        self.last_selected = [clicked_type, clicked_category]
                        impact_fig = generate_impact_graph(
                            data=df_filtered,
                            clicked_category=clicked_category,
                            clicked_type=clicked_type,
                            click_data=True
                        )

                return aggregate_fig, impact_fig, json.dumps(self.last_selected)

    def impact_types_graphs(self):
        @self.app.callback(
            Output(self.intelligence_impact_graph_id, 'figure'),
            Output(self.functional_impact_graph_id, 'figure'),
            [Input('selected-country', 'value'),
             Input(self.aggregate_graph_id, 'clickData'),
             Input(self.impact_graph_id, 'clickData'),
             Input(self.last_selected_stack, 'data'),
             Input(self.reset_button, 'n_clicks')],
        )
        def generate_impact_types_graph(selected_country, aggregate_graph_click_data, impact_graph_click_data, last_selected, n_clicks):
            df_clean = self.df.copy(deep=True)
            df_clean = filter_data(df_clean, selected_country)

            if self.reset_button == ctx.triggered_id:
                impact_graph_click_data = None
                aggregate_graph_click_data = None

            if self.aggregate_graph_id == ctx.triggered_id:
                impact_graph_click_data = None

            if aggregate_graph_click_data:
                clicked_category = aggregate_graph_click_data['points'][0]['y']
                hover_info = aggregate_graph_click_data['points'][0]['hovertext']
                type_match = re.search(r"Type: (.*?)<br>", hover_info)
                clicked_type = type_match.group(1) if type_match else None
            else:
                clicked_category = None
                clicked_type = None

            if impact_graph_click_data:
                selected_impact = impact_graph_click_data['points'][0]['x']
            else:
                selected_impact = None

            df_clean = filter_data_click_data(
                data=df_clean,
                category=clicked_category,
                type=clicked_type,
                last_selected=last_selected,
                impact_click_data=selected_impact
            )

            intell_fig = generate_impact_type_graph(
                data=df_clean,
                impact_type="intelligence_impact",
                text_column="intelligence_impact_text",
                marker_color='#e06783',
                marker_line_color='#cc0130',
                category_array_list=intell_category_array_list
            )

            functional_fig = generate_impact_type_graph(
                data=df_clean,
                impact_type="functional_impact",
                marker_color='#99c3ce',
                marker_line_color='#33869d',
                category_array_list=functional_category_array_list
            )

            return intell_fig, functional_fig

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
