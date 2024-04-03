import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from server.utils import graph_config


initial_access_techniques = [
    {
        "id": "drive_by_compromise",
        "image": "/assets/mitre/drive_by_compromise.svg",
        "label": "Drive-By Compromise",
        "description": "Attackers infiltrate a user's system by exploiting vulnerabilities \
        or stealing credentials through compromised websites visited during regular browsing.",
    },
    {
        "id": "public_facing_application",
        "image": "/assets/mitre/public_facing_application.svg",
        "label": "Exploit Public Facing Application",
        "description": "Attackers exploit vulnerabilities in internet-exposed systems or software to gain \
        unauthorized access to a network. The weakness in the system can be a software bug, a temporary glitch, or a misconfiguration.",
    },
    {
        "id": "external_remote_services",
        "image": "/assets/mitre/external_remote_services.svg",
        "label": "External Remote Services",
        "description": "Attackers use external network services \
        (e.g. VPNs, Secure Shell (SSH), email and cloud services) to gain unauthorized access or maintain persistence within a target's network.",

    },
    {
        "id": "hardware_additions",
        "image": "/assets/mitre/hardware_additions.svg",
        "label": "Hardware Additions",
        "description": "Attackers introduce unauthorized devices, like computer accessories or network hardware, \
        into a system to create new attack vectors or functionalities for exploitation.",
    },
    {
        "id": "phishing",
        "image": "/assets/mitre/phishing.svg",
        "label": "Phishing",
        "description": "Attackers send deceptive electronic messages to manipulate individuals into providing \
        sensitive information or accessing malicious content, ranging from broadly targeted mass campaigns to highly tailored spearphishing against specific targets.",
    },
    {
        "id": "removable_media",
        "image": "/assets/mitre/removable_media.svg",
        "label": "Replication Through Removable Media",
        "description": "Attackers use portable storage devices like USB drives to transfer malware onto systems, \
        exploiting features like Autorun or deceiving users into manually executing the malware, which can compromise isolated or air-gapped networks",
    },
    {
        "id": "supply_chain_compromise",
        "image": "/assets/mitre/supply_chain_compromise.svg",
        "label": "Supply Chain Compromise",
        "description": "Attackers tamper with products or their delivery processes before they reach the final consumer, aiming to breach data or systems",
    },
    {
        "id": "trusted_relationship",
        "image": "/assets/mitre/trusted_relationship.svg",
        "label": "Trusted Relationship",
        "description": "Attackers compromise or use organisations with existing access to target victims, \
        taking advantage of the trust and potentially lower security scrutiny in these third-party connections.",
    },
    {
        "id": "valid_accounts",
        "image": "/assets/mitre/valid_accounts.svg",
        "label": "Valid Accounts",
        "description": "Attackers obtain and use legitimate user credentials to bypass security measures, \
        gain access to network resources, and potentially increase privileges, often avoiding detection by blending in with normal user activities.",
    },
]


def create_accordion_label(label, image):
    return dmc.AccordionControl(
        dmc.Group(
            [
                dmc.Avatar(src=image, size="md"),
                html.Div(
                    [
                        dmc.Text(label),
                    ]
                ),
            ]
        )
    )


def create_accordion_content(content):
    return dmc.AccordionPanel(dmc.Text(content, size="sm"))


mitre_accordion = dmc.Accordion(
    chevronPosition="right",
    variant="contained",
    children=[
        dmc.AccordionItem(
            [
                create_accordion_label(
                    technique["label"], technique["image"]
                ),
                create_accordion_content(technique["description"]),
            ],
            value=technique["id"],
        )
        for technique in initial_access_techniques
    ],
)


types_section = dbc.Row([
    dbc.Row([
        dbc.Col([
            html.H2(
                id="types-section-main-title",
                style={"text-align": "center", "padding-top": "20px", "padding-bottom": "20px", "font-weight": "700"}),
            html.H3("What are the most frequent types of cyberattacks against each critical infrastructure sector? "),
            html.P(
                "This section focused on the main targeted critical infrastructure sectors. The bar chart shows the aggregate number \
                of attacks recorded by EuRepoC per sector since 2000. The timeline shows the rolling average number of attacks \
                publicly disclosed over 30 days since January 2023, along with the rolling average intensity of these \
                attacks also over 30 days. Click on the bars to display and compare the timeline for each sector.",
                style={"text-align": "left", "padding": "10px 150px 20px 0px", "font-weight": "400"}
            )
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H5(id="types-section-aggregate-title", style={"text-align": "center"}),
            dcc.Graph(id="types-section-aggregate-graph",
                      config=graph_config("EuRepoC-top-attack-types-by-sector")),
            dcc.Store(id="types-section-bar-index-store", data=[]),
        ], md=6),
        dbc.Col([
            html.H5(id="types-section-evolution-title", style={"text-align": "center"}),
            html.P([
                html.I(
                    "Click on a sector in the bar chart to display the timeline for that sector",
                    style={"font-size": "0.8rem"}
                ),
            ], style={"text-align": "center"}),
            dcc.Graph(id="types-section-evolution-graph",
                      config=graph_config("EuRepoC-attack-types-overtime")),
            dcc.Store(id="types-section-bar-label-store", data=[]),
            html.Div([
                dmc.Button([
                    "Reset graphs",
                    ],
                    id="types-section-reset-graphs",
                    variant="outline",
                    leftIcon=DashIconify(icon="fluent:arrow-reset-24-filled"),
                    color="grey",
                    size="sm",
                ),
            ], style={"text-align": "right"})
        ], md=6)
    ]),
    html.Div(html.Hr(style={"width": "50%"}), style={"text-align": "center", "padding": "20px"}),
    dbc.Row([
        dbc.Col([
            html.H3("What are the most frequent techniques used by threat actors to gain access?"),
            html.P(
                "When it comes to cyberattacks, the initial access phase is crucial. \
                This is the stage where attackers first penetrate a network or system, or in other words \
                ‘gain a foot in the door’. Understanding this phase is essential for bolstering defenses \
                against cyber threats. The MITRE ATT&CK framework, a globally recognised knowledge base, \
                categorises various tactics and techniques used by threat actors in cyber conflicts. \
                This graphs shows the most frequent ‘Initial Access’ techniques defined under the MITRE ATT&CK \
                framework that adverseries use to gain their initial foothold within the network of \
                critical infrastructure organisations.",
                style={"text-align": "left", "padding": "10px 150px 20px 0px", "font-weight": "400"}
            )
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.H5(id="types-section-techniques-bar-title", style={"text-align": "center"}),
            html.Div([
                html.Div([
                    html.Label("Sector:"),
                    dcc.Dropdown(
                        id="types-section-techniques-sectors-dropdown",
                        options=[
                            {"label": "All", "value": "all"},
                            {"label": "Health", "value": "Health"},
                            {"label": "Finance", "value": "Finance"},
                            {"label": "Telecom", "value": "Telecommunications"},
                            {"label": "Transportation", "value": "Transportation"},
                            {"label": "Energy", "value": "Energy"},
                            {"label": "Defence industry", "value": "Defence industry"},
                            {"label": "Research", "value": "Research"},
                            {"label": "Critical Manufacturing", "value": "Critical Manufacturing"},
                            {"label": "Digital Provider", "value": "Digital Provider"},
                            {"label": "Food", "value": "Food"},
                            {"label": "Water", "value": "Water"},
                            {"label": "Chemicals", "value": "Chemicals"},
                            {"label": "Space", "value": "Space"},
                            {"label": "Waste Water Management", "value": "Waste Water Management"},
                        ],
                        value="all",
                        clearable=False,
                    ),
                ], style={"padding-top": "10px", "padding-bottom": "5px", 'padding-right': '5px', "display": "inline-block", "width": "50%"}),
                html.Div([
                    html.Label("Attack type:"),
                    dcc.Dropdown(
                        id="types-section-techniques-types-dropdown",
                        options=[
                            {"label": "All", "value": "all"},
                            {"label": "Data theft", "value": "Data theft"},
                            {"label": "DDoS/Defacement", "value": "DDoS/Defacement"},
                            {"label": "Ransomware", "value": "Ransomware"},
                            {"label": "Wiper", "value": "Wiper"},
                            {"label": "Hack and leak", "value": "Hack and leak"},
                            {"label": "Other", "value": "Other"},
                        ],
                        value="all",
                        clearable=False,
                    )
                ], style={"padding-top": "10px", "padding-bottom": "5px", 'padding-left': '5px', "display": "inline-block", "width": "50%"}),
            ]),
            dcc.Graph(id="types-section-techniques-bar-chart",
                      config=graph_config("EuRepoC-MITRE-Initial-Access-techniques-used-in-attacks"))
        ], md=6),
        dbc.Col([
            html.Br(),
            html.Br(),
            html.P(html.B("Definitions of the MITRE Initial Access techniques")),
            mitre_accordion
        ], md=6, style={"padding-left": "20px"})
    ])
], style={"padding": "20px 80px"}, className="background-container background-container-types")
