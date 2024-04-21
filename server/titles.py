from dash import Output, Input


def update_titles(app):
    @app.callback(
        [
            Output('overview-section-main-title', 'children'),
            Output('overview-section-aggregate-graph-title', 'children'),
            Output('types-section-main-title', 'children'),
            Output('types-section-aggregate-title', 'children'),
            Output('types-section-impact-title', 'children'),
            Output('types-section-techniques-bar-title', 'children'),
            Output("initiators-section-main-title", "children"),
            Output("initiators-section-aggregate-title", "children"),
            Output("initiators-section-table-title", "children"),
            Output("initiators-section-conflicts-main-title", "children"),
        ],
        [
            Input('selected-country', 'value'),
        ]
    )
    def update_titles(selected_country):
        if selected_country:
            if selected_country == "Global (states)":
                selected_country = "all countries"
            overview_section_main_title = f"Targeted critical infrastructure sectors in {selected_country}"
            overview_section_aggregate_title = f"Top targeted sectors in {selected_country}"
            types_section_main_title = f"Types of attacks and techniques targeting {selected_country}"
            types_section_aggregate_title = f"Top attack types by sector in {selected_country}"
            types_section_impact_title = f"Types of MITRE impact in {selected_country}"
            types_section_techniques_bar_title = f"MITRE Initial Access techniques used in attacks against {selected_country}"
            initiators_section_main_title = f"Top initiators of cyberattacks in {selected_country}"
            initiators_section_aggregate_title = f"Type of initiators by country of origin targeting {selected_country}"
            initiators_section_table_title = f"Top threat actors targeting {selected_country}"
            initiators_section_conflicts_main_title = f"Number of cyberattacks linked to offline conflicts in {selected_country}"
        else:
            overview_section_main_title = "Overview of cyber incidents"
            overview_section_aggregate_title = "Top targeted sectors"
            types_section_main_title = "Types of attacks by sector"
            types_section_aggregate_title = "Top attack types by sector"
            types_section_impact_title = "Type of MITRE impact"
            types_section_techniques_bar_title = "MITRE Initial Access techniques used"
            initiators_section_main_title = "Top initiators of cyberattacks"
            initiators_section_aggregate_title = "Type of initiators by country of origin"
            initiators_section_table_title = "Top threat actors"
            initiators_section_conflicts_main_title = "Number of cyberattacks linked to offline conflicts"

        return (
            overview_section_main_title,
            overview_section_aggregate_title,
            types_section_main_title,
            types_section_aggregate_title,
            types_section_impact_title,
            types_section_techniques_bar_title,
            initiators_section_main_title,
            initiators_section_aggregate_title,
            initiators_section_table_title,
            initiators_section_conflicts_main_title,
        )
