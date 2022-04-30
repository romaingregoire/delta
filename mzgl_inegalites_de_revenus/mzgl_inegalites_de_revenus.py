import dash
import numpy as np
from dash import html, dcc
import plotly.graph_objects as go
import plotly.express as px
import mzgl_inegalites_de_revenus.data.get_data as gd

list_percentile = [f"p{i}p{i+1}" for i in range(0, 100)]


def gini(array):
    """
    Calculate the Gini coefficient
    """
    array, cumul = np.sort(array), 0.0
    sum = array[0]
    for i in range(1, array.shape[0]):
        sum += cumul * 0.01 + ((0.01 * array[i]) / 2)
        cumul += array[i]
    return round((0.5 - sum) * 2.0, 4)


class Inegalites_de_revenus:
    def __init__(self, application=None):
        self.continent_colors = {
            "Afrique": "brown",
            "Amérique": "navy",
            "Asie": "gold",
            "Europe": "green",
            "Océanie": "red",
        }
        self.percentile_colors = {
            "p0p10": "red",
            "p0p50": "blue",
            "p90p100": "green",
            "p99p100": "yellow",
        }
        self.countries_df = gd.get_countries_df()
        self.populations_df = gd.get_population_df()
        self.gdp_df = gd.get_gdp_df()
        self.cpi_df = gd.get_corruption_df()
        self.dem_df = gd.get_democratie_index_df()
        self.ine_df = gd.get_inegalities_df()

        self.gini_df = (
            self.ine_df[self.ine_df.index.isin(list_percentile, level="Percentile")]
            .groupby(level=[0, 2])["value"]
            .agg([gini])
        )

        self.main_layout = html.Div(
            [
                html.Div(
                    className="row",
                    children=[html.H2("Inégalités de revenus dans le monde")],
                ),
                html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className="ten columns",
                            children=[
                                html.Center(
                                    [
                                        html.H4(children=[], id="title-main-graph"),
                                        html.Div([dcc.Graph(id="main-graph")]),
                                        html.Br(),
                                        html.Div(
                                            [
                                                dcc.Slider(
                                                    id="Year-Slider", step=1, value=1995
                                                )
                                            ]
                                        ),
                                        html.Br(),
                                        html.Div(id="div-country"),
                                        html.Div(
                                            children=[
                                                dcc.Graph(
                                                    id="left-graph",
                                                    style={
                                                        "width": "49.5%",
                                                        "display": "inline-block",
                                                    },
                                                ),
                                                dcc.Graph(
                                                    id="right-graph",
                                                    style={
                                                        "width": "50%",
                                                        "display": "inline-block",
                                                    },
                                                ),
                                            ],
                                            style={
                                                "display": "flex",
                                                "borderTop": "thin lightgrey solid",
                                                "borderBottom": "thin lightgrey solid",
                                                "justifyContent": "center",
                                            },
                                        ),
                                    ]
                                ),
                                dcc.Markdown(
                                    """
                                #### À propos
                                Données :
                                - [Population, Banque mondiale](https://data.worldbank.org/indicator/SP.POP.TOTL?name_desc=false)
                                - [PIB par personnes, Banque mondiale](https://data.worldbank.org/indicator/NY.GDP.PCAP.CD)
                                - [Inégalités de revenus, World inegalities database](https://wid.world/data/)
                                - [Index de corruption, Transparency International](https://www.transparency.org/en/cpi/2021)
                                - [Index de démocratie, Gapminder](https://www.gapminder.org/data/documentation/democracy-index/)
                                * (c) 2022 Gauthier Lombard, Mathieu Zimmermann
                                """
                                ),
                            ],
                        ),
                        html.Div(
                            className="two columns",
                            children=[
                                html.Div("Indicateurs en ordonnée"),
                                dcc.RadioItems(
                                    id="select-Y",
                                    options=[
                                        {
                                            "label": "1% les plus riches",
                                            "value": "p99p100",
                                        },
                                        {
                                            "label": "10% les plus riches",
                                            "value": "p90p100",
                                        },
                                        {
                                            "label": "50% les plus pauvres",
                                            "value": "p0p50",
                                        },
                                        {
                                            "label": "10% les plus pauvres",
                                            "value": "p0p10",
                                        },
                                        {
                                            "label": "Coefficient de Gini",
                                            "value": "G",
                                        },
                                    ],
                                    value="p99p100",
                                    labelStyle={"display": "block"},
                                ),
                                html.Br(),
                                html.Div("Indicateurs en abscisse"),
                                dcc.RadioItems(
                                    id="select-X",
                                    options=[
                                        {
                                            "label": "Indice de corruption",
                                            "value": "C",
                                        },
                                        {
                                            "label": "Indice de démocratie",
                                            "value": "Indice de démocratie",
                                        },
                                        {
                                            "label": "PIB par habitant",
                                            "value": "P",
                                        },
                                    ],
                                    value="C",
                                    labelStyle={"display": "block"},
                                ),
                                html.Br(),
                                html.Div("Continents"),
                                html.Div(
                                    [
                                        dcc.Checklist(
                                            id="checklist-continent",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in sorted(
                                                    self.continent_colors.keys()
                                                )
                                            ],
                                            value=sorted(self.continent_colors.keys()),
                                            labelStyle={"display": "block"},
                                        ),
                                    ]
                                ),
                            ],
                        ),
                    ],
                ),
            ]
        )
        # application should have its own layout and use self.main_layout as a page or in a component
        if application:
            self.app = application
        else:
            self.app = dash.Dash(
                __name__, title="Les inégalités de revenus dans le monde"
            )
            self.app.layout = self.main_layout

        self.app.callback(
            [
                dash.dependencies.Output("Year-Slider", "min"),
                dash.dependencies.Output("Year-Slider", "max"),
                dash.dependencies.Output("Year-Slider", "value"),
                dash.dependencies.Output("Year-Slider", "marks"),
            ],
            [
                dash.dependencies.Input("select-X", "value"),
            ],
        )(self.update_year_slider)
        self.app.callback(
            dash.dependencies.Output("main-graph", "figure"),
            [
                dash.dependencies.Input("select-Y", "value"),
                dash.dependencies.Input("select-X", "value"),
                dash.dependencies.Input("Year-Slider", "value"),
                dash.dependencies.Input("checklist-continent", "value"),
            ],
        )(self.update_main_graph)
        self.app.callback(
            dash.dependencies.Output("title-main-graph", "children"),
            [
                dash.dependencies.Input("select-Y", "value"),
                dash.dependencies.Input("select-X", "value"),
            ],
        )(self.update_title)
        self.app.callback(
            dash.dependencies.Output("div-country", "children"),
            dash.dependencies.Input("main-graph", "hoverData"),
        )(self.get_country)
        self.app.callback(
            dash.dependencies.Output("left-graph", "figure"),
            [
                dash.dependencies.Input("main-graph", "hoverData"),
                dash.dependencies.Input("Year-Slider", "value"),
                dash.dependencies.Input("select-Y", "value"),
            ],
        )(self.create_left_graph)
        self.app.callback(
            dash.dependencies.Output("right-graph", "figure"),
            [
                dash.dependencies.Input("main-graph", "hoverData"),
                dash.dependencies.Input("select-X", "value"),
            ],
        )(self.create_right_graph)

    def update_title(self, percentile, xaxis):
        yaxis = "les 10% les plus pauvres"
        if percentile == "p99p100":
            yaxis = "les 1% les plus riches"
        elif percentile == "p0p50":
            yaxis = "les 50% les plus pauvres"
        elif percentile == "p90p100":
            yaxis = "les 10% les plus riches"
        title = " ".join(
            ["Évolution par pays de la part des revenus détenus par", yaxis, "vs "]
        )
        if xaxis == "C":
            title += "Indice de corruption"
        elif xaxis == "P":
            title += "Produit intérieur brut par habitant"
        else:
            title += "Indice de démocratie"
        return title

    def get_country(self, hoverData):
        if hoverData is None:
            country = self.countries_df.iloc[np.random.randint(len(self.countries_df))]
            return country["Country_Name"]
        return hoverData["points"][0]["hovertext"]

    def percentile_graph(self, code, yaxis):
        title, y_axis_title = (
            "Évolution de la part des revenus des 1% les plus riches",
            "Pourcentage des revenus des 1% les plus riches",
        )
        df = self.ine_df.loc[(code, yaxis, slice(None)), :].sort_index()
        if yaxis == "p0p50":
            title, y_axis_title = (
                "Évolution de la part des revenus des 50% les plus pauvres",
                "Pourcentage des revenus des 50% les plus pauvres",
            )
        elif yaxis == "p0p10":
            title, y_axis_title = (
                "Évolution de la part des revenus des 10% les plus pauvres",
                "Pourcentage des revenus des 10% les plus pauvres",
            )
        elif yaxis == "p90p100":
            title, y_axis_title = (
                "Évolution de la part des revenus des 10% les plus riches",
                "Pourcentage des revenus des 10% les plus riches",
            )
        data = [
            go.Scatter(
                name="Indice de corruption",
                x=df.index.get_level_values(level=2).array,
                y=df["value"].array,
                mode="lines",
                hovertemplate="Année: %{x}<br>Part des revenus: %{y}%<extra></extra>",
            )
        ]
        fig = go.Figure(
            data=data,
            layout={
                "title": title,
                "xaxis": {"title": "Années"},
                "yaxis": {"title": y_axis_title, "type": "linear"},
                "autosize": True,
                "showlegend": False,
            },
        )
        return fig

    def create_left_graph(self, hoverData, year, yaxis):
        country_name = (self.get_country(hoverData),)
        code = (
            self.countries_df.reset_index()
            .set_index(["Country_Name"])
            .loc[country_name]["alpha2"]
        )
        if yaxis != "G":
            return self.percentile_graph(code, yaxis)
        tmp = self.ine_df.reset_index(level=1).sort_index().loc[(code, year), :]
        tmp = tmp[tmp["Percentile"].isin(list_percentile)]
        cumsum = list(np.cumsum(np.sort(tmp["value"].array)) * 100)
        cumsum[-1] = 100.0
        data, layout = [
            go.Scatter(
                x=np.arange(1, 101, 1),
                y=cumsum,
                hovertemplate="%{x}% des adultes les moins aisées se partagent %{y:.2f}% des revenues avant taxes<extra></extra>",
                mode="lines",
            ),
            go.Scatter(
                name="Ligne d'égalité",
                x=[0, 100],
                y=[0, 100],
                mode="lines",
                hoverinfo=["skip", "skip"],
            ),
        ], {
            "title": f"Indice de Gini - {year}",
            "xaxis": {
                "title": "Part cumulée des plus de 20 ans avec les revenus du plus faible au plus élevé",
                "fixedrange": True,
            },
            "yaxis": {
                "title": f"Partage cumulé des revenus en {year}",
                "type": "linear",
                "fixedrange": True,
            },
            "autosize": True,
            "showlegend": False,
            "margin": {"l": 40, "b": 40, "r": 20, "t": 30},
        }
        fig = go.Figure(data=data, layout=layout)
        fig.add_annotation(
            xref="paper",
            yref="paper",
            font=dict(color="black", size=14),
            x=0.05,
            y=0.95,
            text=f"Coefficient de Gini: {self.gini_df.loc[(code, year)].gini}",
            showarrow=False,
        )
        fig.add_annotation(
            xref="paper",
            yref="paper",
            font=dict(color="black", size=14),
            x=0.5,
            y=0.55,
            text="Ligne d'égalité",
            showarrow=False,
            textangle=-31.5,
        )
        return fig

    def create_right_graph(self, hoverData, xaxis):
        x_axis_df, title, y_axis_title, country_name = (
            self.dem_df,
            "Évolution de l'indice de démocratie",
            "Indice de démocratie",
            self.get_country(hoverData),
        )
        code, data = (
            self.countries_df.reset_index()
            .set_index(["Country_Name"])
            .loc[country_name]["alpha3"],
            None,
        )
        if xaxis == "C":
            x_axis_df, title, y_axis_title = (
                self.cpi_df,
                "Évolution de la corruption",
                "Indice de corruption",
            )
            x_axis_df = x_axis_df.loc[(code)]
            data = [
                go.Scatter(
                    name="Indice de corruption",
                    x=x_axis_df.index.get_level_values(level=0).array,
                    y=x_axis_df["score"].array,
                    mode="lines",
                    hovertemplate="Année: %{x}<br>Indice de corruption: %{y}<extra></extra>",
                )
            ]
        elif xaxis == "P":
            x_axis_df, title, y_axis_title = (
                self.gdp_df,
                "Produit intérieur brut par habitant (en US $ de 2021)",
                "",
            )
            try:
                x_axis_df = x_axis_df.loc[(code)]
            except:
                return None
            data = [
                go.Scatter(
                    name="Produit intérieur brut par habitant",
                    x=x_axis_df.index.array,
                    y=x_axis_df.values,
                    mode="lines",
                    hovertemplate="Année: %{x}<br>PIB par habitant: %{y}<extra></extra>",
                )
            ]
        else:
            x_axis_df = x_axis_df.loc[(code)]
            data = [
                go.Scatter(
                    name="Indice de démocratie",
                    x=x_axis_df.index.get_level_values(level=0).array,
                    y=x_axis_df["score"].array,
                    mode="lines",
                    hovertemplate="Année: %{x}<br>Indice de démocratie: %{y}<extra></extra>",
                )
            ]
        fig = go.Figure(
            data=data,
            layout={
                "title": title,
                "xaxis": {"title": "Années"},
                "yaxis": {"title": y_axis_title, "type": "linear"},
                "autosize": True,
                "showlegend": False,
            },
        )
        return fig

    def update_year_slider(self, xaxis):
        x_axis_df = self.dem_df
        if xaxis == "C":
            x_axis_df = self.cpi_df
        elif xaxis == "P":
            return (
                1995,
                2020,
                1995,
                {str(year): str(year) for year in range(1995, 2021, 5)},
            )
        years = x_axis_df.reset_index()["Year"]
        min_year, max_year = years.min(), years.max()
        return (
            min_year,
            max_year,
            min_year,
            {str(year): str(year) for year in range(min_year, max_year + 1, 5)},
        )

    def update_main_graph(self, percentile, xaxis, year, regions):
        x_axis_df, yaxis, xmax = self.dem_df, "10% les plus pauvres", 100
        tmp = self.ine_df.loc[(slice(None), percentile, year), :]
        tmp = (
            tmp.join(self.countries_df, sort=False)
            .reset_index()
            .set_index(["alpha3", "Year"])
            .sort_index()
        )
        if len(regions) != 5:
            tmp = tmp[tmp["region"].isin(regions)]
        if xaxis == "C":
            x_axis_df, xaxis = self.cpi_df, "Indice de corruption"
        elif xaxis == "P":
            xmax, x_axis_df = -1, self.gdp_df.loc[slice(None), [str(year)]]
            x_axis_df["Year"], xaxis = (
                year,
                "Produit intérieur brut par habitant (en US $ de 2021)",
            )
            x_axis_df = (
                x_axis_df.reset_index()
                .set_index(["alpha3", "Year"])
                .rename(columns={str(year): "score"})
            )
        res = (
            tmp.join(x_axis_df, on=["alpha3", "Year"], sort=True)
            .join(
                self.populations_df.loc[:, str(year)]
                .rename("population")
                .astype("int64")
            )
            .dropna()
        )
        res["value"] *= 100
        fig = px.scatter(
            res,
            x="score",
            y="value",
            size="population",
            size_max=60,
            hover_name="Country_Name",
            color="region",
            color_discrete_map=self.continent_colors,
            custom_data=["Country_Name", "population"],
        )
        if xmax != -1:
            fig.update_xaxes(range=[0, xmax])
        fig.update_yaxes(range=[0, 0.7])
        if percentile == "p99p100":
            fig.update_yaxes(range=[0, 35.0])
            yaxis = "1% les plus riches"
        elif percentile == "p0p50":
            fig.update_yaxes(range=[0, 30.0])
            yaxis = "50% les plus pauvres"
        elif percentile == "p90p100":
            fig.update_yaxes(range=[25.0, 70.0])
            yaxis = "10% les plus riches"
        fig.update_layout(
            xaxis=dict(title=xaxis, type="linear"),
            yaxis=dict(title=yaxis, type="linear"),
            margin={"l": 0, "b": 1, "t": 1, "r": 0},
            hovermode="closest",
            showlegend=False,
        )
        fig.update_traces(
            hovertemplate="".join(
                [
                    "<b>%{customdata[0]}</b><br><br>Part des revenus: %{y} %<br>Population: %{customdata[1]:,}<br>",
                    xaxis,
                    ": %{x}<extra></extra>",
                ]
            )
        )
        return fig

    def run(self, debug=False, port=8050):
        self.app.run_server(host="0.0.0.0", debug=debug, port=port)


if __name__ == "__main__":
    ine = Inegalites_de_revenus()
    ine.app.run_server(debug=True, port=8051)
