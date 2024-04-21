from dash.dependencies import Input, Output, State
import dash
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from server.utils import filter_data, empty_figure, sectors_color_map


def aggregate_plot_layout(grid_title):
    return {
        'xaxis_title': "",
        'yaxis_title': f"{grid_title}",
        'legend_title': "",
        'barcornerradius': 6,
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'xaxis': {
            'showgrid': True,
            'showline': True,
            'showticklabels': True,
            'zeroline': False,
            'linecolor': 'rgba(225,225,225,0.4)',
            'gridcolor': 'rgba(225,225,225,0.4)'
        },
        'margin': {'l': 10, 'r': 10, 't': 10, 'b': 10},
        "height": 455,
    }


evolution_plot_layout = {
    "xaxis_title": "<i>date range slider - drag the handles to select a time period<br></i>",
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
        }
    },
    "yaxis": {
        "showgrid": True,
        "showline": True,
        "showticklabels": True,
        "zeroline": False,
        "linecolor": 'rgba(225,225,225,0.4)',
        "gridcolor": 'rgba(225,225,225,0.4)',
        "range": [0, None],
    },
    "yaxis2": {
        "title": "Intensity",
        "showgrid": False,
        "showline": True,
        "showticklabels": True,
        "zeroline": False,
        "linecolor": 'rgba(225,225,225,0.4)',
        "gridcolor": 'rgba(225,225,225,0.4)',
        "overlaying": "y",
        "side": "right",
        "range": [0, None],
    },
    "margin": {'l': 10, 'r': 0, 't': 10, 'b': 10},
    "height": 450,
    "font": {"color": 'black'},
}


def generate_plot_data(data, moving_average=False):
    data = data.copy()
    if moving_average:
        data = data[data["added_to_db"] >= "2023-01-01"]
        data = data.groupby(['added_to_db']).agg({"id": "nunique", "weighted_intensity": "mean"}).reset_index()
        data['value_moving_avg'] = data['id'].rolling(window=30, min_periods=1).mean()
        data['intensity_moving_avg'] = data['weighted_intensity'].rolling(window=30, min_periods=1).mean()
    else:
        data = data.groupby([pd.Grouper(key='added_to_db', freq='ME')]).agg(
            {"id": "nunique", "weighted_intensity": "mean"}).reset_index()
        data['cumulative_count'] = data['id'].cumsum()
    return data


def generate_plot(data, fig, moving_average=False, selected_sector=None, len_sector=None):
    if moving_average:
        col_name_count = "value_moving_avg"
        col_name_intensity = "intensity_moving_avg"
        hovertemplate_count = 'Date: %{x}<br>Rolling average over 30 days: %{y:.1f}<br>Incident count: %{text}<extra></extra>'
        hovertemplate_intensity = 'Date: %{x}<br>Rolling average intensity over 30 days: %{y:.1f}<br>Mean intensity: %{text:.1f}<extra></extra>'
        axis_title="Rolling average over 30 days"

    else:
        col_name_count = "cumulative_count"
        col_name_intensity = "weighted_intensity"
        hovertemplate_count = 'Date: %{x}<br>Cumulative count of incidents: %{y:.1f}<br>Incident count: %{text}<extra></extra>'
        hovertemplate_intensity = 'Date: %{x}<br>Mean intensity: %{text:.1f}<extra></extra>'
        axis_title="Cumulative count"

    if selected_sector:
        name = selected_sector
        color = sectors_color_map[selected_sector]
        if len_sector and len_sector == 1:
            visibility = True
        elif len_sector and len_sector > 1:
            visibility = 'legendonly'
        else:
            visibility = True
    else:
        name = "All sectors"
        color = "#002C38"
        visibility = True


    fig.add_trace(
        go.Scatter(
            x=data['added_to_db'],
            y=data[col_name_count],
            mode='lines',
            text=data['id'],
            name=f'{name}',
            line=dict(color=color),
            hovertemplate=hovertemplate_count
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data['added_to_db'],
            y=data[col_name_intensity],
            mode='lines',
            text=data['weighted_intensity'],
            name=f'Intensity',
            line=dict(color=color, dash='dot'),
            hovertemplate=hovertemplate_intensity,
            visible=visibility,
            yaxis="y2"
        )
    )

    fig.update_layout(showlegend=True)
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(**evolution_plot_layout)
    fig.update_layout(yaxis_title=axis_title)
    return fig


class OverviewIntensity:
    def __init__(
            self,
            app=None,
            df=None,
            subtype_df=None,
            aggregate_graph_id=None,
            bar_index_store_id=None,
            evolution_graph_id=None,
            bar_label_store_id=None,
            sunburst_chart_id=None,
            reset_button=None
    ):
        self.app = app
        self.df = df
        self.subtype_df = subtype_df
        self.aggregate_graph_id = aggregate_graph_id
        self.bar_index_store_id = bar_index_store_id
        self.bar_label_store_id = bar_label_store_id
        self.evolution_graph_id = evolution_graph_id
        self.sunburst_chart_id = sunburst_chart_id
        self.reset_button = reset_button

        self.initialize_callbacks()

    def initialize_callbacks(self):
        self.bar_selection()
        self.aggregate_graph()
        self.evolution_graph()
        self.sunburst_chart()

    def bar_selection(self):
        @self.app.callback(
            [Output(self.bar_index_store_id, 'data'),
             Output(self.bar_label_store_id, 'data')],
            [Input(self.aggregate_graph_id, 'clickData'),
             Input('selected-country', 'value'),
             Input(self.reset_button, 'n_clicks')],
            [State(self.bar_index_store_id, 'data'),
             State(self.bar_label_store_id, 'data')]
        )
        def update_selected_bars(clickdata, selected_country, reset_button, selected_bars_index, selected_bars):
            ctx = dash.callback_context

            if not ctx.triggered:
                return [], []

            input_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if input_id == 'selected-country':
                return [], []

            if input_id == self.reset_button:
                return [], []

            elif input_id == self.aggregate_graph_id and clickdata:
                clicked_bar_index = clickdata['points'][0]['pointIndex']
                clicked_bar_label = clickdata['points'][0]['y']
                if clicked_bar_index in selected_bars_index:
                    selected_bars_index.remove(clicked_bar_index)
                else:
                    selected_bars_index.append(clicked_bar_index)
                if clicked_bar_label in selected_bars:
                    selected_bars.remove(clicked_bar_label)
                else:
                    selected_bars.append(clicked_bar_label)

                return selected_bars_index, selected_bars

            return selected_bars_index, selected_bars

    def aggregate_graph(self):
        @self.app.callback(
            Output(self.aggregate_graph_id, 'figure'),
            Input('selected-country', 'value'),
            Input(self.bar_index_store_id, 'data')
        )
        def generate_graph(selected_country, selected_bars):
            callback_data = self.df.copy(deep=True)
            callback_data = callback_data[~callback_data["receiver_subcategory"].isin(["Not available", "Other"])]
            callback_data = filter_data(callback_data, selected_country)

            if callback_data.empty:
                return empty_figure()
            else:
                callback_data = callback_data.groupby("receiver_subcategory").agg(
                    {"id": "nunique", "weighted_intensity": "mean"}
                ).reset_index()
                callback_data = callback_data.sort_values(by="id", ascending=True)
                fig = px.bar(callback_data, y="receiver_subcategory", x="id", orientation='h')
                fig.update_traces(hovertemplate='Sector: %{y}<br>Number of incidents: %{x}<extra></extra>')
                grid_title = "Number of operations"

                fig_layout = aggregate_plot_layout(grid_title)
                fig.update_layout(**fig_layout)

                colors = ['#d63459' if i in selected_bars else '#668088' for i in
                          range(len(callback_data))]
                line_colors = ["#cc0130" if i in selected_bars else "#002C38" for i in
                               range(len(callback_data))]
                fig.update_traces(marker=dict(color=colors, line_color=line_colors, line_width=1.5))

                return fig

    def evolution_graph(self):
        @self.app.callback(
            Output(self.evolution_graph_id, 'figure'),
            Output('overview-section-evolution-graph-title', 'children'),
            Input('selected-country', 'value'),
            Input(self.bar_label_store_id, 'data'),
            Input("toggle-switch", "checked")
        )
        def generate_timeline(selected_country, selected_bars, toggle):
            callback_data = self.df.copy(deep=True)
            callback_data = callback_data[~callback_data["receiver_subcategory"].isin(["Not available", "Other"])]
            callback_data = filter_data(callback_data, selected_country)

            country = selected_country if selected_country != "Global (states)" else "all countries"

            if toggle:
                title = f"Cumulative number of attacks disclosed since Jan 2023 in {country}"
            else:
                title = f"Rolling average number of attacks disclosed since Jan 2023 in {country}"

            if callback_data.empty:
                return empty_figure(), title
            else:
                fig = go.Figure()
                if selected_bars and len(selected_bars) > 0 and not toggle:
                    for sector in selected_bars:
                        selected_sector = sector
                        sector_data = callback_data[callback_data["receiver_subcategory"] == selected_sector]
                        sector_data = generate_plot_data(sector_data, moving_average=True)
                        fig = generate_plot(
                            sector_data,
                            fig,
                            moving_average=True,
                            selected_sector=selected_sector,
                            len_sector=len(selected_bars)
                        )
                elif not selected_bars and len(selected_bars) == 0 and not toggle:
                    callback_data = generate_plot_data(callback_data, moving_average=True)
                    fig = generate_plot(callback_data, fig, moving_average=True)

                elif selected_bars and len(selected_bars) > 0 and toggle:
                    for sector in selected_bars:
                        selected_sector = sector
                        sector_data = callback_data[callback_data["receiver_subcategory"] == selected_sector]
                        sector_data = generate_plot_data(sector_data)
                        fig = generate_plot(
                            sector_data,
                            fig,
                            selected_sector=selected_sector,
                            len_sector=len(selected_bars)
                        )
                else:
                    callback_data = generate_plot_data(callback_data)
                    fig = generate_plot(callback_data, fig)


                return fig, title

    def sunburst_chart(self):
        @self.app.callback(
            Output(self.sunburst_chart_id, "figure"),
            Input('selected-country', 'value'),
        )
        def generate_sunburst(selected_country):
            callback_data = self.subtype_df.copy(deep=True)
            callback_data = callback_data[~callback_data["receiver_subcategory"].isin(["Not available", "Other"])]
            callback_data = filter_data(callback_data, selected_country)

            callback_data = callback_data.groupby(["receiver_subcategory", "ci_subtype"]).agg({"id": "nunique"}).reset_index()
            callback_data = callback_data.rename(columns={"id": "count"})

            fig = px.sunburst(
                callback_data,
                path=['receiver_subcategory', 'ci_subtype'],
                values='count',
                color='receiver_subcategory',
                color_discrete_map=sectors_color_map
            )
            fig.update_traces(
                hovertemplate='<b>%{label}</b><br>Number of targeted organisations: %{value}',
                marker=dict(line=dict(width=0.5, color='rgba(225,225,225,0.4)'))
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=0, b=0),
                font=dict(color='black'),
                height=500
            )
            return fig
