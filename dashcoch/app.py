# -*- coding: utf-8 -*-
#import i18n
from dashcoch import DataLoader, StyleLoader
import math
from configparser import ConfigParser
from datetime import date
from pytz import timezone
import geojson
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
parser = ConfigParser()
parser.read("settings.ini")

data = DataLoader(parser)
style = StyleLoader()


#
# General app settings
#
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Italia COVID19 Tracker"

#
# Show the data
#
app.layout = html.Div(
    id="main",
    children=[
        html.Div(
            id="header",
            children=[
                html.H4(children="Casi di COVID-19 in Italia"),
                html.P(
                    id="description",
                    children=[
                        dcc.Markdown(
                            """
                        Numeri di casi COVID-19 in Italia. Dati compilati da [Alice Lo Valvo](https://www.linkedin.com/in/alice-lo-valvo-7b39755b/) e visualizzati da [@sketpeis](https://twitter.com/skepteis).

                        I dati possono essere trovati [qui](https://github.com/alicelovalvo/covid19-cases-italy), e sono stati presi dai dati ufficiali della [Protezione Civile](https://github.com/pcm-dpc/COVID-19).
                        """
                        )
                    ],
                ),
            ],
        ),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="twelve columns",
                    children=[
                        html.Div(
                            className="total-container",
                            children=[
                                html.P(className="total-title", children="Casi Totali"),
                                html.Div(
                                    className="total-content",
                                    children=str(int(data.total_italian_cases)),
                                ),
                            ],
                        ),
                        html.Div(
                            className="total-container",
                            children=[
                                html.P(
                                    className="total-title", children="Nuovi Casi Oggi"
                                ),
                                html.Div(
                                    className="total-content",
                                    children="+" + str(int(data.new_italian_cases)),
                                ),
                            ],
                        ),
                        html.Div(
                            className="total-container",
                            children=[
                                html.P(
                                    className="total-title", children="Deceduti Totali"
                                ),
                                html.Div(
                                    className="total-content",
                                    children=str(int(data.total_italian_fatalities)),
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(className="six columns"),
                html.Div(className="six columns"),
            ],
        ),
        html.Br(),
        html.Div(
            id="slider-container",
            children=[
                html.P(
                    id="slider-text", children="Sposta lo slider per cambiare la data:",
                ),
                dcc.Slider(
                    id="slider-date",
                    min=0,
                    max=len(data.italian_cases["Date"]) - 1,
                    marks={
                        i: date.fromisoformat(d).strftime("%d. %m.")
                        for i, d in enumerate(data.italian_cases["Date"])
                    },
                    value=len(data.italian_cases["Date"]) - 1,
                ),
                html.Br(),
                dcc.RadioItems(
                    id="radio-prevalence",
                    options=[
                        {"label": "Numeri di Casi", "value": "number"},
                        {"label": "Diffusione (per 10,000)", "value": "prevalence"},
                        {"label": "Numero di Deceduti", "value": "fatalities"},
                    ],
                    value="number",
                    labelStyle={
                        "display": "inline-block",
                        "color": style.theme["foreground"],
                    },
                ),
            ],
        ),
        html.Div(children=[dcc.Graph(id="graph-map", config={"staticPlot": True},),]),
        html.Div(
            children=[
                "Regioni: ",
                html.Span(", ".join(data.updated_regions)),
            ]
        ),
        html.Br(),
        html.H4(
            children="Dati per l'Italia", style={"color": style.theme["accent"]}
        ),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="six columns", children=[dcc.Graph(id="case-it-graph")]
                ),
                html.Div(
                    className="six columns",
                    children=[dcc.Graph(id="case-world-graph")],
                ),
            ],
        ),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="six columns",
                    children=[dcc.Graph(id="fatalities-it-graph")],
                ),
                html.Div(
                    className="six columns",
                    children=[dcc.Graph(id="fatalities-world-graph")],
                ),
            ],
        ),
        html.Br(),
        html.H4(children="Dati per Regioni", style={"color": style.theme["accent"]}),
        html.Div(
            id="plot-settings-container",
            children=[
                html.P(
                    id="plot-settings-text",
                    children="Seleziona la scala e la regione per vederli nei grafici:",
                ),
                dcc.RadioItems(
                    id="radio-scale",
                    options=[
                        {"label": "Scala Lineare", "value": "linear"},
                        {"label": "Scala Logaritmica", "value": "log"},
                    ],
                    value="linear",
                    labelStyle={
                        "display": "inline-block",
                        "color": style.theme["foreground"],
                    },
                ),
                html.Br(),
                dcc.Dropdown(
                    id="dropdown-regions",
                    options=[
                        {"label": region, "value": region}
                        for region in data.regional_labels
                    ],
                    value=data.regional_labels,
                    multi=True,
                ),
            ],
        ),
        html.Br(),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="six columns", children=[dcc.Graph(id="case-graph")]
                ),
                html.Div(
                    className="six columns", children=[dcc.Graph(id="case-pc-graph"),],
                ),
            ],
        ),
        html.Br(),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="twelve columns",
                    children=[dcc.Graph(id="case-graph-diff")],
                ),
            ],
        ),
        html.Br(),
        html.H4(children="Raw Data", style={"color": style.theme["accent"]}),
        dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in data.italian_cases.columns],
            data=data.italian_cases.to_dict("records"),
        ),
    ],
)

# -------------------------------------------------------------------------------
# Callbacks
# -------------------------------------------------------------------------------
@app.callback(
    Output("graph-map", "figure"),
    [Input("slider-date", "value"), Input("radio-prevalence", "value")],
)
def update_graph_map(selected_date_index, mode):
    date = data.italian_cases["Date"].iloc[selected_date_index]

    map_data = data.italian_cases_by_date_filled
    labels = [
        region + ": " + str(int(map_data[region][date]))
        for region in data.regional_centres
    ]

    if mode == "prevalence":
        map_data = data.italian_cases_by_date_filled_per_capita
        labels = [
            region + ": " + str(round((map_data[region][date]), 1))
            for region in data.regional_centres
        ]
    elif mode == "fatalities":
        map_data = data.italian_fatalities_by_date
        labels = [
            region + ": " + str(int(map_data[region][date]))
            if not math.isnan(float(map_data[region][date]))
            else ""
            for region in data.regional_centres
        ]

    return {
        "data": [
            {
                "lat": [
                    data.regional_centres[region]["lat"]
                    for region in data.regional_centres
                ],
                "lon": [
                    data.regional_centres[region]["lon"]
                    for region in data.regional_centres
                ],
                "text": labels,
                "mode": "text",
                "type": "scattergeo",
                "textfont": {
                    "family": "sans serif",
                    "size": 18,
                    "color": "white",
                    "weight": "bold",
                },
            },
            {
                "type": "choropleth",
                "locations": data.regional_labels,
                "z": [map_data[region][date] for region in map_data if region != "Italia"],
                "colorscale": style.turbo,
                "geojson": "/assets/italy.geojson",
                "marker": {"line": {"width": 0.0, "color": "#08302A"}},
                "colorbar": {
                    "thickness": 10,
                    "bgcolor": "#252e3f",
                    "tickfont": {"color": "white"},
                },
            },
        ],
        "layout": {
            "geo": {
                "visible": False,
                "center": {"lat": 41.26486, "lon": 14.00376},
                "lataxis": {"range": [36.58843, 48.94129]},
                "lonaxis": {"range": [6.38737, 24.62015]},
                # "fitbounds": "geojson",
                "projection": {"type": "transverse mercator"},
                # "landcolor": "#1f2630",
                # "showland": True,
                # "showcountries": True,
            },
            "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
            "height": 600,
            "plot_bgcolor": "#252e3f",
            "paper_bgcolor": "#252e3f",
        }
        # "layout": {
        #     "mapbox": {
        #         "accesstoken": "pk.eyJ1IjoiZGFlbnVwcm9ic3QiLCJhIjoiY2s3eDR2dmRyMDg0ajN0cDlkaDNmM3J0NyJ9.tcJPFQkbsVGlWpyQaKPtiw",
        #         "style": "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz",
        #         "center": {"lat": 46.8181877, "lon": 8.2275124},
        #         "pitch": 0,
        #         "zoom": 7,
        #     },
        #     "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
        #     "height": 600,
        #     "plot_bgcolor": "#1f2630",
        #     "paper_bgcolor": "#1f2630",
        # },
    }


#
# Total cases Italy
#
@app.callback(
    Output("case-it-graph", "figure"), [Input("radio-scale", "value")],
)
def update_case_it_graph(selected_scale):
    return {
        "data": [
            {
                "x": data.italian_cases_as_dict["Date"],
                "y": data.italian_cases_as_dict["Italia"],
                "name": "Italia",
                "marker": {"color": style.theme["foreground"]},
                "type": "bar",
            }
        ],
        "layout": {
            "title": "Casi Totali in Italia",
            "height": 400,
            "xaxis": {"showgrid": True, "color": "#ffffff"},
            "yaxis": {
                "type": selected_scale,
                "showgrid": True,
                "color": "#ffffff",
                "rangemode": "tozero",
            },
            "plot_bgcolor": style.theme["background"],
            "paper_bgcolor": style.theme["background"],
            "font": {"color": style.theme["foreground"]},
        },
    }


@app.callback(
    Output("fatalities-it-graph", "figure"), [Input("radio-scale", "value")],
)
def update_fatalities_it_graph(selected_scale):
    return {
        "data": [
            {
                "x": data.italian_fatalities["Date"],
                "y": data.italian_fatalities["Italia"],
                "name": "Italia",
                "marker": {"color": style.theme["foreground"]},
                "type": "bar",
            }
        ],
        "layout": {
            "title": "Totali Deceduti in Italia",
            "height": 400,
            "xaxis": {"showgrid": True, "color": "#ffffff"},
            "yaxis": {
                "type": selected_scale,
                "showgrid": True,
                "color": "#ffffff",
                "rangemode": "tozero",
            },
            "plot_bgcolor": style.theme["background"],
            "paper_bgcolor": style.theme["background"],
            "font": {"color": style.theme["foreground"]},
        },
    }


#
# Total cases world
#
@app.callback(
    Output("case-world-graph", "figure"), [Input("radio-scale", "value")],
)
def update_case_world_graph(selected_scale):
    return {
        "data": [
            {
                "x": data.italian_world_cases_normalized.index.values,
                "y": data.italian_world_cases_normalized[country],
                "name": country,
                # "marker": {"color": theme["foreground"]},
                # "type": "bar",
            }
            for country in data.italian_world_cases_normalized
            if country != "Day"
        ],
        "layout": {
            "title": "Diffusione per 10,000 abitanti",
            "height": 400,
            "xaxis": {
                "showgrid": True,
                "color": "#ffffff",
                "title": "Giorni da quando diffusione >0.4 per 10,000",
            },
            "yaxis": {"type": selected_scale, "showgrid": True, "color": "#ffffff",},
            "plot_bgcolor": style.theme["background"],
            "paper_bgcolor": style.theme["background"],
            "font": {"color": style.theme["foreground"]},
        },
    }


@app.callback(
    Output("fatalities-world-graph", "figure"), [Input("radio-scale", "value")],
)
def update_fatalities_world_graph(selected_scale):
    return {
        "data": [
            {
                "x": ["Italy"]
                + data.world_case_fatality_rate.index.values.tolist(),
                "y": [data.italian_case_fatality_rate]
                + [val for val in data.world_case_fatality_rate],
                "name": "Italy",
                "marker": {"color": style.theme["foreground"]},
                "type": "bar",
            }
        ],
        "layout": {
            "title": "Rate di mortalità (Deceduti / Casi Totali)",
            "height": 400,
            "xaxis": {"showgrid": True, "color": "#ffffff"},
            "yaxis": {
                "type": selected_scale,
                "showgrid": True,
                "color": "#ffffff",
                "rangemode": "tozero",
            },
            "plot_bgcolor": style.theme["background"],
            "paper_bgcolor": style.theme["background"],
            "font": {"color": style.theme["foreground"]},
        },
    }


#
# Regional Data
#
@app.callback(
    Output("case-graph", "figure"),
    [Input("dropdown-regions", "value"), Input("radio-scale", "value")],
)
def update_case_graph(selected_regions, selected_scale):
    return {
        "data": [
            {
                "x": data.italian_cases_as_dict["Date"],
                "y": data.italian_cases_as_dict[region],
                "name": region,
                "marker": {"color": style.colors[i - 1]},
            }
            for i, region in enumerate(data.italian_cases_as_dict)
            if region in selected_regions
        ],
        "layout": {
            "title": "Casi per Regione",
            "height": 750,
            "xaxis": {"showgrid": True, "color": "#ffffff"},
            "yaxis": {"type": selected_scale, "showgrid": True, "color": "#ffffff"},
            "plot_bgcolor": style.theme["background"],
            "paper_bgcolor": style.theme["background"],
            "font": {"color": style.theme["foreground"]},
        },
    }


@app.callback(
    Output("case-pc-graph", "figure"),
    [Input("dropdown-regions", "value"), Input("radio-scale", "value")],
)
def update_case_pc_graph(selected_regions, selected_scale):
    return {
        "data": [
            {
                "x": data.italian_cases_normalized_as_dict["Date"],
                "y": data.italian_cases_normalized_as_dict[region],
                "name": region,
                "marker": {"color": style.colors[i - 1]},
            }
            for i, region in enumerate(data.italian_cases_normalized_as_dict)
            if region in selected_regions
        ],
        "layout": {
            "title": "Casi per Regione (per 10,000 abitanti)",
            "height": 750,
            "xaxis": {"showgrid": True, "color": "#ffffff"},
            "yaxis": {"type": selected_scale, "showgrid": True, "color": "#ffffff"},
            "plot_bgcolor": style.theme["background"],
            "paper_bgcolor": style.theme["background"],
            "font": {"color": style.theme["foreground"]},
        },
    }


@app.callback(
    Output("case-graph-diff", "figure"),
    [Input("dropdown-regions", "value"), Input("radio-scale", "value")],
)
def update_case_graph_diff(selected_regions, selected_scale):
    data_non_nan = {}
    data_non_nan["Date"] = data.italian_cases_as_dict["Date"]

    for region in data.italian_cases_as_dict:
        if region == "Date":
            continue
        values = []
        last_value = 0
        for _, v in enumerate(data.italian_cases_as_dict[region]):
            if math.isnan(float(v)):
                values.append(last_value)
            else:
                last_value = v
                values.append(v)
        data_non_nan[region] = values

    return {
        "data": [
            {
                "x": data_non_nan["Date"],
                "y": [0]
                + [
                    j - i
                    for i, j in zip(data_non_nan[region][:-1], data_non_nan[region][1:])
                ],
                "name": region,
                "marker": {"color": style.colors[i - 1]},
                "type": "bar",
            }
            for i, region in enumerate(data.italian_cases_as_dict)
            if region in selected_regions
        ],
        "layout": {
            "title": "Nuovi Casi per Regione",
            "height": 750,
            "xaxis": {"showgrid": True, "color": "#ffffff"},
            "yaxis": {"type": selected_scale, "showgrid": True, "color": "#ffffff"},
            "plot_bgcolor": style.theme["background"],
            "paper_bgcolor": style.theme["background"],
            "font": {"color": style.theme["foreground"]},
            "barmode": "stack",
        },
    }


if __name__ == "__main__":
    app.run_server(
        # debug=True,
        # dev_tools_hot_reload=True,
        # dev_tools_hot_reload_interval=50,
        # dev_tools_hot_reload_max_retry=30,
    )
