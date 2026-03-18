import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Data ──────────────────────────────────────────────────────────────────────
df = pd.read_csv("isp_pricing_data.csv")
df["date"] = pd.to_datetime(df["date"])

carriers = sorted(df["pr__vendor"].unique().tolist())

# ── App ───────────────────────────────────────────────────────────────────────
app = dash.Dash(__name__)
app.title = "ISP Prepaid Pricing Dashboard"

app.layout = html.Div(
    style={"fontFamily": "Inter, sans-serif", "backgroundColor": "#f8f9fa", "minHeight": "100vh", "padding": "24px"},
    children=[

        # Header
        html.Div(
            style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start", "marginBottom": "20px"},
            children=[
                html.Div([
                    html.H1("ISP Prepaid Pricing Dashboard",
                            style={"margin": "0 0 4px 0", "color": "#1a1a2e"}),
                    html.P("Click any location on the map to see carrier pricing trends.",
                           style={"color": "#666", "margin": "0"}),
                ]),
                html.Div("Usman Rehan", style={
                    "fontSize": "13px", "color": "#999", "paddingTop": "6px"
                }),
            ]
        ),

        # Carrier filter
        html.Div(
            style={"backgroundColor": "white", "padding": "16px 20px", "borderRadius": "8px",
                   "boxShadow": "0 1px 4px rgba(0,0,0,0.08)", "marginBottom": "20px",
                   "display": "flex", "alignItems": "center", "gap": "16px"},
            children=[
                html.Label("Carrier:", style={"fontWeight": "600", "whiteSpace": "nowrap"}),
                dcc.Checklist(
                    id="carrier-filter",
                    options=[{"label": f"  {c}", "value": c} for c in carriers],
                    value=carriers,
                    inline=True,
                    inputStyle={"marginRight": "4px"},
                    labelStyle={"marginRight": "20px", "cursor": "pointer"}
                ),
            ]
        ),

        # Map + Line chart row
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px", "marginBottom": "20px"},
            children=[

                # Map
                html.Div(
                    style={"backgroundColor": "white", "borderRadius": "8px",
                           "boxShadow": "0 1px 4px rgba(0,0,0,0.08)", "padding": "16px"},
                    children=[
                        html.H3("Location Map", style={"margin": "0 0 12px 0", "color": "#1a1a2e", "fontSize": "16px"}),
                        html.P("Click a dot to drill in", style={"color": "#999", "fontSize": "12px", "margin": "0 0 8px 0"}),
                        dcc.Graph(id="map-chart", style={"height": "420px"},
                                  config={"scrollZoom": True}),
                    ]
                ),

                # Line chart
                html.Div(
                    style={"backgroundColor": "white", "borderRadius": "8px",
                           "boxShadow": "0 1px 4px rgba(0,0,0,0.08)", "padding": "16px"},
                    children=[
                        html.H3(id="line-title", children="Select a location",
                                style={"margin": "0 0 12px 0", "color": "#1a1a2e", "fontSize": "16px"}),
                        dcc.Graph(id="line-chart", style={"height": "420px"}),
                    ]
                ),
            ]
        ),

        # Table
        html.Div(
            style={"backgroundColor": "white", "borderRadius": "8px",
                   "boxShadow": "0 1px 4px rgba(0,0,0,0.08)", "padding": "16px"},
            children=[
                html.H3("Pricing Data", style={"margin": "0 0 12px 0", "color": "#1a1a2e", "fontSize": "16px"}),
                dash_table.DataTable(
                    id="data-table",
                    page_size=15,
                    sort_action="native",
                    filter_action="native",
                    style_table={"overflowX": "auto"},
                    style_header={
                        "backgroundColor": "#1a1a2e", "color": "white",
                        "fontWeight": "600", "fontSize": "13px"
                    },
                    style_cell={
                        "padding": "10px 14px", "fontSize": "13px",
                        "border": "1px solid #eee", "textAlign": "left"
                    },
                    style_data_conditional=[
                        {"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"}
                    ],
                ),
            ]
        ),
    ]
)


# ── Callbacks ─────────────────────────────────────────────────────────────────

@app.callback(
    Output("map-chart", "figure"),
    Input("carrier-filter", "value"),
)
def update_map(selected_carriers):
    filtered = df[df["pr__vendor"].isin(selected_carriers)]
    map_df = (
        filtered
        .groupby(["location_zip", "location_lat", "location_long", "location_address"])
        .agg(avg_price=("price", "mean"), carrier_count=("pr__vendor", "nunique"))
        .reset_index()
    )
    map_df["avg_price"] = map_df["avg_price"].round(2)

    fig = px.scatter_mapbox(
        map_df,
        lat="location_lat",
        lon="location_long",
        color="avg_price",
        size="avg_price",
        size_max=30,
        hover_name="location_address",
        hover_data={
            "location_zip": True,
            "avg_price": ":.2f",
            "carrier_count": True,
            "location_lat": False,
            "location_long": False,
        },
        custom_data=["location_zip", "location_address"],
        zoom=11,
        mapbox_style="carto-positron",
        color_continuous_scale="RdYlGn_r",
        labels={"avg_price": "Avg Price ($)", "carrier_count": "# Carriers"},
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      coloraxis_colorbar=dict(title="Avg $"))
    return fig


@app.callback(
    Output("line-chart", "figure"),
    Output("line-title", "children"),
    Output("data-table", "data"),
    Output("data-table", "columns"),
    Input("map-chart", "clickData"),
    Input("carrier-filter", "value"),
)
def update_detail(click_data, selected_carriers):
    # ── No selection yet ──
    if click_data is None:
        placeholder = go.Figure()
        placeholder.update_layout(
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[{
                "text": "Click a location on the map",
                "xref": "paper", "yref": "paper",
                "x": 0.5, "y": 0.5,
                "showarrow": False,
                "font": {"size": 16, "color": "#aaa"},
            }],
            plot_bgcolor="white",
        )
        return placeholder, "Select a location", [], []

    selected_zip = click_data["points"][0]["customdata"][0]
    selected_address = click_data["points"][0]["customdata"][1]

    filtered = df[
        (df["location_zip"] == selected_zip) &
        (df["pr__vendor"].isin(selected_carriers))
    ].copy()

    # Line chart
    fig = px.line(
        filtered,
        x="date", y="price", color="pr__vendor",
        markers=True,
        labels={"price": "Monthly Price ($)", "date": "Date", "pr__vendor": "Carrier"},
        color_discrete_map={
            "AT&T Fiber": "#00a8e0",
            "Spectrum": "#6c2d8a",
            "Verizon Fios": "#cd040b",
        },
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=7))
    fig.update_layout(
        margin={"r": 10, "t": 10, "l": 10, "b": 10},
        legend=dict(title="Carrier", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#f0f0f0", tickprefix="$"),
        xaxis=dict(gridcolor="#f0f0f0"),
    )

    # Table
    table_df = filtered[[
        "location_address", "pr__vendor", "price", "date",
        "location_zip", "location_census_block"
    ]].copy()
    table_df["date"] = table_df["date"].dt.strftime("%Y-%m-%d")
    table_df["price"] = table_df["price"].apply(lambda x: f"${x:.2f}")
    table_df = table_df.rename(columns={
        "location_address": "Address",
        "pr__vendor": "Carrier",
        "price": "Price",
        "date": "Date",
        "location_zip": "ZIP",
        "location_census_block": "Census Block",
    }).sort_values("Date")

    cols = [{"name": c, "id": c} for c in table_df.columns]
    return fig, f"Pricing Trend — {selected_address}", table_df.to_dict("records"), cols


if __name__ == "__main__":
    app.run(debug=True)
