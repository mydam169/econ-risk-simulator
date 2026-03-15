from dash import html, dcc, callback, Input, Output, register_page
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np

register_page(
    __name__,
    path="/",
    name="Risk Explorer",
    title="Risk Explorer – Decision Making Under Risk"
)

# ===================== LAYOUT =====================
layout = html.Div([
    html.H2("Risk Aversion Explorer: CRRA Utility", className="mt-4 mb-4"),
    html.P("Explore how probability of loss, size of loss, and risk aversion affect the Certainty Equivalent and Risk Premium.", 
           className="lead text-muted"),

    dbc.Row([
        dbc.Col([
            html.Label("Probability of loss (p)", className="fw-bold"),
            dcc.Slider(
                id="p-slider",
                min=0, max=1, step=0.01, value=0.5,
                marks={0: "0", 0.25: "0.25", 0.5: "0.5", 0.75: "0.75", 1: "1"},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], md=4),

        dbc.Col([
            html.Label("Loss as proportion of wealth (λ)", className="fw-bold"),
            dcc.Slider(
                id="lambda-slider",
                min=0.01, max=0.99, step=0.01, value=0.20,
                marks={0.1: "0.1", 0.3: "0.3", 0.5: "0.5", 0.7: "0.7", 0.9: "0.9"},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], md=4),

        dbc.Col([
            html.Label("Degree of risk aversion (CRRA utility)", className="fw-bold"),
            dcc.Slider(
                id="rho-slider",
                min=-5, max=5, step=0.1, value=0,
                marks={-5: "-5", -2: "-2", 0: "0 (risk neutral)", 2: "2", 5: "5"},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], md=4),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Checklist(
                id="show-ce",
                options=[{"label": "Show Certainty Equivalent (CE)", "value": "ce"}],
                value=["ce"],
                inline=True,
                className="mt-2"
            )
        ], md=6),
        # dbc.Col([
        #     dbc.Checklist(
        #         id="show-rp",
        #         options=[{"label": "Show Risk Premium (RP)", "value": "rp"}],
        #         value=["rp"],
        #         inline=True,
        #         className="mt-2"
        #     )
        # ], md=6),
    ]),

    dcc.Graph(id="risk-plot", style={"height": "620px"}),

    html.Div(id="value-display", className="mt-4")
])


# ===================== CALLBACK =====================
@callback(
    [Output("risk-plot", "figure"),
     Output("value-display", "children")],
    [Input("p-slider", "value"),
     Input("lambda-slider", "value"),
     Input("rho-slider", "value"),
     Input("show-ce", "value"),
    ]
)
def update_risk_plot(p, lam, rho, show_ce_list):
    W = 1  # Initial wealth
    W_good = W
    W_bad = W * (1 - lam)
    EV = (1 - p) * W_good + p * W_bad

    # CRRA utility function
    def u(w, r):
        if abs(r - 1) < 1e-6:
            return np.log(w)
        else:
            return (w ** (1 - r)) / (1 - r)

    EU = p * u(W_bad, rho) + (1 - p) * u(W_good, rho)

    # Certainty Equivalent
    if abs(rho - 1) < 1e-6:
        CE = np.exp(EU)
    else:
        CE = (EU * (1 - rho)) ** (1 / (1 - rho))

    RP = EV - CE

    # Set wealth range and compute utility values over that range
    w_min = max(0.01, W_bad * 0.85)
    w_max = max(1.05, W_good * 1.05)
    w = np.linspace(w_min, w_max, 400)
    u_curve = np.array([u(ww, rho) for ww in w])

    # ==================== BUILD FIGURE ====================
    fig = go.Figure()

    # 1. Utility curve
    fig.add_trace(go.Scatter(
        x=w, y=u_curve, mode="lines",
        name="Utility u(w)",
        line=dict(color="#1f77b4", width=3)
    ))

    # 2. Lottery outcomes
    fig.add_trace(go.Scatter(
        x=[W_bad, W_good],
        y=[u(W_bad, rho), u(W_good, rho)],
        mode="markers+text",
        marker=dict(size=16, color=["#d62728", "#2ca02c"], line=dict(width=2)),
        text=["Bad outcome", "Good outcome"],
        textfont=dict(size=16, color="#333"),
        textposition="top left",
        name="Lottery outcomes",
        showlegend=False
    ))

    # 3. Expected Utility (horizontal line)
    fig.add_hline(y=EU, line=dict(color="#9467bd", dash="dot", width=2),
                  annotation_text=f"EU = {EU:.2f}", annotation_position="top right", annotation_font=dict(size=16))

    # 4. Expected Value (vertical line)
    fig.add_vline(x=EV, line=dict(color="#ff7f0e", dash="dash", width=2),
                  annotation_text=f"EV = {EV:.2f}", annotation_position="top", annotation_font=dict(size=16))

    # 5. Certainty Equivalent (if toggled)
    show_ce = "ce" in show_ce_list

    if show_ce:
        u_ce = u(CE, rho)
        fig.add_trace(go.Scatter(
            x=[CE], y=[u_ce],
            mode="markers+text",
            marker=dict(size=16, color="black", symbol="star"),
            # text=[f"CE = {CE:.2f}"],
            textposition="bottom right",
            textfont=dict(size=16, color="black"),
            name="Certainty Equivalent"
        ))
        fig.add_vline(x=CE, line=dict(color="black", width=2, dash="dash"),
                      annotation_text=f"CE = {CE:.2f}", annotation_position="bottom right", annotation_font=dict(size=16))


    fig.update_layout(
        title="CRRA utility visualization (Initial Wealth = 1)",
        xaxis_title="Wealth (W)",
        yaxis_title="Utility u(W)",
        template="plotly_white",
        height=620,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=40, r=40, t=60, b=40)
    )

    # ===================== NUMERICAL DISPLAY =====================
    value_display = dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col(html.H5(f"Expected Value (EV): {EV:.2}"), md=4),
                dbc.Col(html.H5(f"Certainty Equivalent (CE): {CE:.2f}"), md=4),
                dbc.Col(html.H5(f"Risk Premium (RP): {RP:.2f}"), md=4),
            ], className="text-center"),
            html.Hr(),
            html.P(f"Initial Wealth = 1 | Loss proportion λ = {lam:.2f} | "
                   f"Probability of loss p = {p:.2f} | Risk aversion ρ = {rho:.1f}",
                   className="text-muted text-center")
        ])
    ], color="light", outline=True)

    
    return fig, value_display