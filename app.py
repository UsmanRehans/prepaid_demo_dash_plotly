import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Data ──────────────────────────────────────────────────────────────────────
df = pd.read_csv("isp_pricing_data.csv")
df["date"] = pd.to_datetime(df["date"])

carriers = sorted(df["pr__vendor"].unique().tolist())

# ── Color Palette ─────────────────────────────────────────────────────────────
CARRIER_COLORS = {
    "AT&T Fiber":   "#5BBFDE",   # sky blue
    "Spectrum":     "#72C472",   # soft green
    "Verizon Fios": "#A8D8EA",   # pale blue
}

BG        = "#F5FAFB"           # off-white/ice
CARD      = "#FFFFFF"
HEADER_BG = "#EAF6F6"           # very light teal-white
ACCENT    = "#5BBFDE"           # sky blue
TEXT_DARK = "#2C3E50"
TEXT_MUTE = "#90A4AE"

# ── App ───────────────────────────────────────────────────────────────────────
app = dash.Dash(__name__)
app.title = "ISP Prepaid Pricing Dashboard"
server = app.server  # expose Flask server for gunicorn

app.layout = html.Div(
    style={"fontFamily": "Inter, sans-serif", "backgroundColor": BG,
           "minHeight": "100vh", "padding": "28px 32px"},
    children=[

        # ── Header ────────────────────────────────────────────────────────────
        html.Div(
            style={
                "backgroundColor": CARD,
                "borderRadius": "12px",
                "padding": "20px 28px",
                "marginBottom": "20px",
                "boxShadow": "0 2px 8px rgba(91,191,222,0.10)",
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "borderLeft": f"5px solid {ACCENT}",
            },
            children=[
                html.Div([
                    html.H1("ISP Prepaid Pricing Dashboard",
                            style={"margin": "0 0 4px 0", "color": TEXT_DARK,
                                   "fontSize": "22px", "fontWeight": "700"}),
                    html.P("Click any location on the map to explore carrier pricing trends.",
                           style={"color": TEXT_MUTE, "margin": "0", "fontSize": "13px"}),
                ]),
                html.Div("Usman Rehan",
                         style={"fontSize": "12px", "color": TEXT_MUTE,
                                "fontStyle": "italic"}),
            ]
        ),

        # ── Carrier Filter ────────────────────────────────────────────────────
        html.Div(
            style={"backgroundColor": CARD, "padding": "14px 24px",
                   "borderRadius": "10px", "boxShadow": "0 1px 6px rgba(0,0,0,0.06)",
                   "marginBottom": "20px", "display": "flex",
                   "alignItems": "center", "gap": "20px"},
            children=[
                html.Label("Filter Carrier:",
                           style={"fontWeight": "600", "color": TEXT_DARK,
                                  "fontSize": "13px", "whiteSpace": "nowrap"}),
                dcc.Checklist(
                    id="carrier-filter",
                    options=[{"label": f"  {c}", "value": c} for c in carriers],
                    value=carriers,
                    inline=True,
                    inputStyle={"marginRight": "5px", "accentColor": ACCENT},
                    labelStyle={"marginRight": "24px", "cursor": "pointer",
                                "fontSize": "13px", "color": TEXT_DARK},
                ),
            ]
        ),

        # ── Map + Line Chart ──────────────────────────────────────────────────
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr",
                   "gap": "20px", "marginBottom": "20px"},
            children=[

                # Map card
                html.Div(
                    style={"backgroundColor": CARD, "borderRadius": "10px",
                           "boxShadow": "0 1px 6px rgba(0,0,0,0.06)", "padding": "18px"},
                    children=[
                        html.Div(style={"display": "flex", "alignItems": "center",
                                        "marginBottom": "4px", "gap": "8px"},
                                 children=[
                                     html.Span("📍", style={"fontSize": "16px"}),
                                     html.H3("Location Map",
                                             style={"margin": "0", "color": TEXT_DARK,
                                                    "fontSize": "15px", "fontWeight": "600"}),
                                 ]),
                        html.P("Click a pin to see pricing trends",
                               style={"color": TEXT_MUTE, "fontSize": "12px",
                                      "margin": "0 0 10px 0"}),
                        dcc.Graph(id="map-chart", style={"height": "430px"},
                                  config={"scrollZoom": True}),
                    ]
                ),

                # Line chart card
                html.Div(
                    style={"backgroundColor": CARD, "borderRadius": "10px",
                           "boxShadow": "0 1px 6px rgba(0,0,0,0.06)", "padding": "18px"},
                    children=[
                        html.Div(style={"display": "flex", "alignItems": "center",
                                        "marginBottom": "4px", "gap": "8px"},
                                 children=[
                                     html.Span("📈", style={"fontSize": "16px"}),
                                     html.H3(id="line-title", children="Select a location",
                                             style={"margin": "0", "color": TEXT_DARK,
                                                    "fontSize": "15px", "fontWeight": "600"}),
                                 ]),
                        html.P("Price over time by carrier",
                               style={"color": TEXT_MUTE, "fontSize": "12px",
                                      "margin": "0 0 10px 0"}),
                        dcc.Graph(id="line-chart", style={"height": "430px"}),
                    ]
                ),
            ]
        ),

        # ── Data Table ────────────────────────────────────────────────────────
        html.Div(
            style={"backgroundColor": CARD, "borderRadius": "10px",
                   "boxShadow": "0 1px 6px rgba(0,0,0,0.06)", "padding": "18px"},
            children=[
                html.Div(style={"display": "flex", "alignItems": "center",
                                "marginBottom": "12px", "gap": "8px"},
                         children=[
                             html.Span("🗂️", style={"fontSize": "16px"}),
                             html.H3("Pricing Data",
                                     style={"margin": "0", "color": TEXT_DARK,
                                            "fontSize": "15px", "fontWeight": "600"}),
                         ]),
                dash_table.DataTable(
                    id="data-table",
                    page_size=15,
                    sort_action="native",
                    filter_action="native",
                    style_table={"overflowX": "auto"},
                    style_header={
                        "backgroundColor": ACCENT, "color": "white",
                        "fontWeight": "600", "fontSize": "13px",
                        "border": "none", "padding": "12px 14px",
                    },
                    style_cell={
                        "padding": "10px 14px", "fontSize": "13px",
                        "border": "1px solid #EDF2F7", "textAlign": "left",
                        "color": TEXT_DARK,
                    },
                    style_data_conditional=[
                        {"if": {"row_index": "odd"},
                         "backgroundColor": "#F0F9FC"},
                        {"if": {"column_id": "Price"},
                         "fontWeight": "600", "color": "#2E7D32"},
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
        size_max=35,
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
        color_continuous_scale=["#A8D8EA", "#72C472", "#5BBFDE"],
        labels={"avg_price": "Avg Price ($)", "carrier_count": "# Carriers"},
    )
    fig.update_traces(
        marker=dict(sizemin=18, opacity=0.85),
        selector=dict(type="scattermapbox"),
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor=CARD,
        coloraxis_colorbar=dict(
            title="Avg $",
            tickprefix="$",
            bgcolor="white",
            bordercolor="#eee",
            borderwidth=1,
            thickness=12,
        ),
    )
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

    # ── No selection yet ──────────────────────────────────────────────────────
    if click_data is None:
        placeholder = go.Figure()
        placeholder.update_layout(
            xaxis={"visible": False},
            yaxis={"visible": False},
            plot_bgcolor=CARD,
            paper_bgcolor=CARD,
            annotations=[{
                "text": "👆 Click a location on the map",
                "xref": "paper", "yref": "paper",
                "x": 0.5, "y": 0.5, "showarrow": False,
                "font": {"size": 15, "color": TEXT_MUTE},
            }],
        )
        return placeholder, "Select a location", [], []

    selected_zip     = click_data["points"][0]["customdata"][0]
    selected_address = click_data["points"][0]["customdata"][1]

    filtered = df[
        (df["location_zip"] == selected_zip) &
        (df["pr__vendor"].isin(selected_carriers))
    ].copy()

    # ── Line chart ────────────────────────────────────────────────────────────
    fig = px.line(
        filtered,
        x="date", y="price", color="pr__vendor",
        markers=True,
        labels={"price": "Price ($)", "date": "Date", "pr__vendor": "Carrier"},
        color_discrete_map=CARRIER_COLORS,
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    fig.update_layout(
        margin={"r": 10, "t": 10, "l": 10, "b": 10},
        plot_bgcolor=CARD,
        paper_bgcolor=CARD,
        legend=dict(
            title="Carrier",
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(size=12),
        ),
        yaxis=dict(
            gridcolor="#EDF2F7",
            tickprefix="$",
            tickfont=dict(color=TEXT_MUTE),
            title_font=dict(color=TEXT_DARK),
        ),
        xaxis=dict(
            gridcolor="#EDF2F7",
            tickfont=dict(color=TEXT_MUTE),
        ),
    )

    # ── Table ─────────────────────────────────────────────────────────────────
    table_df = filtered[[
        "location_address", "pr__vendor", "price", "date",
        "location_zip", "location_census_block"
    ]].copy()
    table_df["date"]  = table_df["date"].dt.strftime("%Y-%m-%d")
    table_df["price"] = table_df["price"].apply(lambda x: f"${x:.2f}")
    table_df = table_df.rename(columns={
        "location_address":    "Address",
        "pr__vendor":          "Carrier",
        "price":               "Price",
        "date":                "Date",
        "location_zip":        "ZIP",
        "location_census_block": "Census Block",
    }).sort_values("Date")

    cols = [{"name": c, "id": c} for c in table_df.columns]
    return fig, f"Pricing — {selected_address}", table_df.to_dict("records"), cols


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)
