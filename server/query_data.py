import re
import pandas as pd
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, aliased
from datetime import datetime


iso_codes = pd.read_excel("./data/iso_codes.xlsx")


class QueryData:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        self.metadata = MetaData()
        self.metadata.reflect(self.engine)
        self.Base = automap_base(metadata=self.metadata)
        self.Base.prepare()
        self.Session = sessionmaker(bind=self.engine)

        self.Incidents = self.Base.classes.incidents_main_data
        self.CleanTypes = self.Base.classes.clean_types
        self.Receivers = self.Base.classes.receivers
        self.receivers_alias = aliased(self.Receivers)
        self.CyberIntensity = self.Base.classes.cyber_intensity
        self.Initiators = self.Base.classes.initiators
        self.MitreImpact = self.Base.classes.mitre_impact
        self.TechnicalCodings = self.Base.classes.technical_codings
        self.OfflineConflictIssues = self.Base.classes.offline_conflict_issues
        self.InitiatorsCategories = self.Base.classes.initiator_categories
        self.initiators_alias = aliased(self.Initiators)
        self.initiators_categories_alias = aliased(self.InitiatorsCategories)
        self.MitreInitialAccess = self.Base.classes.mitre_initial_access
        self.ImpactIndicator = self.Base.classes.impact_indicator
        self.Countries = self.Base.classes.countries
        self.Regions = self.Base.classes.regions
        self.Country_regions = self.metadata.tables['country_regions']
        self.CISubtypes = self.Base.classes.ci_subtypes

    def query_database(self):
        session = self.Session()

        # Build your query
        query = session.query(
            self.Incidents.id,
            self.Incidents.start_date,
            self.Incidents.added_to_db,
            self.CleanTypes.type_clean,
            self.receivers_alias.name.label('receiver_name'),
            self.receivers_alias.country.label('receiver_country'),
            self.Regions.region_name,
            self.receivers_alias.category.label('receiver_category'),
            self.receivers_alias.subcategory.label('receiver_subcategory'),
            self.initiators_alias.name.label('initiator_name'),
            self.initiators_alias.country.label('initiator_country'),
            self.initiators_categories_alias.category.label('initiator_category'),
            self.initiators_alias.settled.label('settled_initiator'),
            self.MitreInitialAccess.initial_access,
            self.CyberIntensity.weighted_intensity,
            self.TechnicalCodings.zero_days,
            self.MitreImpact.impact,
            self.OfflineConflictIssues.issue,
            self.OfflineConflictIssues.conflict_name,
            self.ImpactIndicator.functional_impact,
            self.ImpactIndicator.intelligence_impact,
            self.ImpactIndicator.economic_impact,
            self.ImpactIndicator.economic_impact_value,
            self.ImpactIndicator.economic_impact_currency,
        ).outerjoin(self.CleanTypes, self.Incidents.id == self.CleanTypes.incident_id). \
            outerjoin(self.receivers_alias, self.Incidents.id == self.receivers_alias.incident_id). \
            outerjoin(self.initiators_alias, self.Incidents.id == self.initiators_alias.incident_id). \
            outerjoin(self.initiators_categories_alias, self.initiators_alias.id == self.initiators_categories_alias.initiator_id). \
            outerjoin(self.MitreInitialAccess, self.Incidents.id == self.MitreInitialAccess.incident_id). \
            outerjoin(self.TechnicalCodings, self.Incidents.id == self.TechnicalCodings.incident_id). \
            outerjoin(self.MitreImpact, self.Incidents.id == self.MitreImpact.incident_id). \
            outerjoin(self.OfflineConflictIssues, self.Incidents.id == self.OfflineConflictIssues.incident_id). \
            outerjoin(self.CyberIntensity, self.Incidents.id == self.CyberIntensity.incident_id). \
            outerjoin(self.ImpactIndicator, self.Incidents.id == self.ImpactIndicator.incident_id). \
            outerjoin(self.Countries, self.Countries.country_name == self.receivers_alias.country). \
            outerjoin(self.Country_regions, self.Country_regions.c.country_id == self.Countries.country_id). \
            outerjoin(self.Regions, self.Regions.region_id == self.Country_regions.c.region_id). \
            filter(self.receivers_alias.category == "Critical infrastructure")

        df = pd.read_sql_query(query.statement, self.engine)
        session.close()
        return df

    def get_subtype_data(self):
        session = self.Session()

        query = session.query(
            self.Incidents.id,
            self.CISubtypes.receiver_subcategory,
            self.CISubtypes.ci_subtype,
            self.receivers_alias.country.label('receiver_country'),
            self.Regions.region_name,
        ).outerjoin(self.CISubtypes, self.Incidents.id == self.CISubtypes.incident_id). \
            outerjoin(self.receivers_alias, self.Incidents.id == self.receivers_alias.incident_id). \
            outerjoin(self.Countries, self.Countries.country_name == self.receivers_alias.country). \
            outerjoin(self.Country_regions, self.Country_regions.c.country_id == self.Countries.country_id). \
            outerjoin(self.Regions, self.Regions.region_id == self.Country_regions.c.region_id)

        df = pd.read_sql_query(query.statement, self.engine)
        df = df[df["receiver_subcategory"].notna()].drop_duplicates()
        session.close()
        return df

    def preclean_data(self, df):
        df_types_no_settled = df.groupby("id").agg(
            settled_initiator=('settled_initiator', lambda x: list(set(x)))
        ).reset_index()
        df_types_no_settled['no_settled'] = df_types_no_settled.apply(
            lambda row: "No settled" if len(row["settled_initiator"]) == 1 and row["settled_initiator"][
                0] is False else "Fine",
            axis=1
        )
        df_types_no_settled = df_types_no_settled[df_types_no_settled["no_settled"] == "No settled"]
        list_ids = df_types_no_settled["id"].to_list()
        df["settled_initiator"] = df.apply(
            lambda row: True if row["id"] in list_ids else row["settled_initiator"],
            axis=1
        )
        df = df[df["settled_initiator"] == True].drop_duplicates()

        original_labels = [
            'No data breach/exfiltration or data corruption (deletion/altering) and/or leaking of data',
            'Minor data breach/exfiltration (no critical/sensitive information), but no data corruption (deletion/altering) or leaking of data  ',
            'Minor data breach/exfiltration (no critical/sensitive information), data corruption (deletion/altering) and/or leaking of data  ',
            'Data corruption (deletion/altering) but no leaking of data, no data breach/exfiltration OR major data breach / exfiltration, but no data corruption and/or leaking of data',
            'Major data breach/exfiltration (critical/sensitive information) & data corruption (deletion/altering) and/or leaking of data ',
            "Not available"
        ]

        new_labels = [
            'No data breach/corruption/leak',
            'Minor data breach',
            'Moderate data breach',
            'Significant data breach',
            'Major data breach',
            'Unknown'
        ]

        descriptive_text = [
            "No data breach/exfiltration, data corruption<br>nor leaking of data",
            "Data breach/exfiltration of non-critical/sensitive information<br>but no data corruption nor leaking of data",
            "Data breach/exfiltration of non-critical/sensitive information<br>and data corruption or leaking of data",
            "Data corruption but no leaking of data<br>nor data breach/exfiltration<br>OR major data breach/exfiltration<br>but no data corruption nor leaking of data",
            "Data breach/exfiltration of critical/sensitive information<br>& data corruption or leaking of data",
            "Unknown intelligence impact"
        ]

        label_mapping = dict(zip(original_labels, new_labels))
        text_mapping = dict(zip(new_labels, descriptive_text))

        df['intelligence_impact'] = df['intelligence_impact'].replace(label_mapping)
        df['intelligence_impact_text'] = df['intelligence_impact'].map(text_mapping)

        df['functional_impact'] = df['functional_impact'].replace("Not available", "Unknown")
        df["impact"] = df["impact"].replace("Not available", "Unknown")


        cutoff_date = datetime.strptime('2020-02-01', '%Y-%m-%d')

        return df[~((df['start_date'] > cutoff_date) &
                    (df['receiver_country'] == 'United Kingdom') &
                    (df['region_name'] == 'EU'))]

    def clean_initiators(self, df):
        df["initiator_country_clean"] = df["initiator_country"]

        def clean_initiator(row):
            if row["initiator_name"] in ["", "None", "Not available", "Unknown", None] and \
                    row["initiator_country"] in ["Unknown", "Not available", None] and \
                    row["initiator_category"] in ["Unknown - not attributed", "Not available", "Unknown", None]:
                row["initiator_country_clean"] = "Not attributed"
            return row

        df = df.apply(clean_initiator, axis=1)

        df["initiator_category"] = df.apply(
            lambda row: "Not attributed" if row["initiator_country_clean"] == "Not attributed" else row[
                "initiator_category"],
            axis=1
        )
        df["initiator_category"] = df["initiator_category"].replace(
            "Unknown - not attributed", "Unknown"
        )
        df["initiator_country_clean"] = df["initiator_country_clean"].replace(
            "Not available", "Unknown"
        )
        df["initiator_name"] = df.apply(
            lambda row: "Not attributed" if row["initiator_country_clean"] == "Not attributed" else row[
                "initiator_name"],
            axis=1
        )
        df["initiator_name"] = df["initiator_name"].replace(
            "Not available", "Unknown"
        )
        df["initiator_name"] = df["initiator_name"].fillna("Unknown")
        df["initiator_category"] = df["initiator_category"].replace(
            "Non-state actor, state-affiliation suggested", "State affiliated actor"
        )
        df["initiator_category"] = df.apply(
            lambda row: "Not attributed" if
            row["initiator_country_clean"] == "Unknown" and row["initiator_name"] == "Unknown" and
            row["initiator_category"] == "Not available" else row["initiator_category"], axis=1
        )
        df["initiator_category"] = df["initiator_category"].replace("Not available", "Unknown")
        df["initiator_category"] = df["initiator_category"].fillna("Not attributed")
        df["initiator_country_clean"] = df["initiator_country_clean"].fillna("Not attributed")
        df["initiator_country_clean"] = df.apply(
            lambda row: "Not attributed" if
            row["initiator_country_clean"] == "Unknown" and row["initiator_name"] == "Unknown"
            and row["initiator_category"] == "Not attributed" else row["initiator_country_clean"], axis=1
        )

        return df.drop(columns=["initiator_country"]).rename(columns={"initiator_country_clean": "initiator_country"})

    def clean_initiator_names(self, df):
        def most_common(series):
            return series.mode()[0] if not series.empty else "Not available"

        def extract_initiator_name(name):
            match = re.match(r'([^/]*/[^/]*)/.*', name)
            return match.group(1) if match else name

        features = ["type_clean", "initial_access", "initiator_country", "initiator_category"]

        for feature in features:
            df_feature = df[["id", "initiator_name", feature]].drop_duplicates()
            if feature == "initial_access":
                df_feature = df_feature[df_feature[feature] != "Not available"]
            result = df_feature.groupby('initiator_name')[feature].agg(most_common).reset_index()
            df = df.merge(result, on='initiator_name', how='left', suffixes=('', f'_most_common'))

        df['initiator_name'] = df['initiator_name'].apply(extract_initiator_name)
        df["initial_access_most_common"] = df["initial_access_most_common"].fillna("Unknown")

        chosen_types = ["Data theft", "DDoS/Defacement", "Ransomware", "Wiper", "Hack and leak", "Other"]
        df['type_clean'] = df['type_clean'].apply(lambda x: x if x in chosen_types else "Other")
        df['receiver_subcategory'] = df['receiver_subcategory'].apply(lambda x: "Other" if x == "Not available" else x)
        df['weighted_intensity'] = pd.to_numeric(df['weighted_intensity'], errors='coerce')

        df = df.merge(iso_codes, left_on="initiator_country_most_common", right_on="country_name", how="left")
        df = df.drop(columns=["country_name"])

        df["initiator_country"] = df["initiator_country"].replace("Iran, Islamic Republic of", "Iran")
        df["initiator_country"] = df["initiator_country"].replace("Korea, Democratic People's Republic of", "North Korea")

        return df

    def dispose(self):
        self.engine.dispose()
