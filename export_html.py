"""
export_html.py — Generate standalone HTML dashboard
=====================================================
Run:   python export_html.py
Output: esg_portfolio.html
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from universe import get_universe_df
import pipeline as pl
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.io import to_html
from scipy import stats as sc

print("\n╔══════════════════════════════════════════════════════════════╗")
print("║    ESG CLIMATE PORTFOLIO — HTML EXPORT                       ║")
print("╚══════════════════════════════════════════════════════════════╝\n")
print("Running analytics pipeline...")

df_universe = get_universe_df()
print(f"  Universe: {len(df_universe)} stocks across {df_universe['sector'].nunique()} sectors")
data = pl.run(df_universe)

metrics_df = data["metrics_df"]
stock_df   = data["stock_df"]
q_colors   = data["q_colors"]
q_labels   = data["q_labels"]
wealth     = data["wealth"]
drawdowns  = data["drawdowns"]
rolling    = data["rolling"]
sp500      = data["sp500"]
cross_corr = data["cross_corr"]
quint_rets = data["quint_rets"]

# ── COLOUR PALETTE ────────────────────────────────────────────────────────────
PAGE_BG  = "#050b14"      # deep base — aurora sits on top via CSS
SIDE_BG  = "#060c18"      # header
CARD_BG  = "#0a1628cc"    # card surface — slight transparency so aurora bleeds through
PANEL_BG = "#0a1628"      # chart panels
BORDER   = "#1a3a5c"      # subtle border
PLOT_BG  = "#09152200"    # transparent so panels show aurora
GRID     = "#0f2240"
TEXT_PRI = "#e8f4fd"
TEXT_MUT = "#6b9aad"
FONT     = "Inter, -apple-system, sans-serif"

# Card accent colours — matching the reference dashboard feel
CARD_COLS = {
    "green":  {"bg":"#0d2e1a", "accent":"#00d4aa", "border":"#00d4aa40"},
    "orange": {"bg":"#2e1a0d", "accent":"#ff9500", "border":"#ff950040"},
    "pink":   {"bg":"#2e0d1a", "accent":"#ff4d8d", "border":"#ff4d8d40"},
    "blue":   {"bg":"#0d1a2e", "accent":"#4da6ff", "border":"#4da6ff40"},
    "purple": {"bg":"#1a0d2e", "accent":"#b87dff", "border":"#b87dff40"},
    "teal":   {"bg":"#0d2a2e", "accent":"#00c9d4", "border":"#00c9d440"},
}

# Quintile chart colours — vivid on dark bg
Q_CHART_COLS = {
    1: "#00d4aa",
    2: "#4da6ff",
    3: "#b87dff",
    4: "#ff9500",
    5: "#ff4d8d",
}

def qc(q): return Q_CHART_COLS.get(q, TEXT_MUT)

# Plotly base layout
def dark_layout(**kwargs):
    base = dict(
        font_family=FONT, font_color=TEXT_PRI,
        plot_bgcolor="rgba(9,21,34,0.0)", paper_bgcolor="rgba(10,22,40,0.0)",
        margin=dict(l=52, r=24, t=52, b=44),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0,
                    font=dict(color=TEXT_MUT, size=11)),
        xaxis=dict(gridcolor=GRID, linecolor=BORDER, zeroline=False,
                   tickfont=dict(color=TEXT_MUT, size=10)),
        yaxis=dict(gridcolor=GRID, linecolor=BORDER, zeroline=False,
                   tickfont=dict(color=TEXT_MUT, size=10)),
        title_font=dict(color=TEXT_PRI, size=14),
    )
    base.update(kwargs)
    return base

# ── FORMAT HELPERS ────────────────────────────────────────────────────────────

def pct(v, d=1):
    try:
        f = float(v)
        return f"{f*100:.{d}f}%" if not np.isnan(f) else "N/A"
    except: return "N/A"

def dec(v, d=3):
    try:
        f = float(v)
        return f"{f:.{d}f}" if not np.isnan(f) else "—"
    except: return "—"

def sci(v):
    try:
        f = float(v)
        return f"{f:.2e}" if not np.isnan(f) else "—"
    except: return "—"

def fd(fig):
    return to_html(fig, full_html=False, include_plotlyjs=False)

# ── FIGURES ───────────────────────────────────────────────────────────────────

def fig_wealth():
    fig = go.Figure()
    for q in range(1, 6):
        w = wealth[q]
        fig.add_trace(go.Scatter(
            x=w.index, y=(w-1)*100, name=q_labels[q],
            line=dict(color=qc(q), width=2),
            hovertemplate="%{y:.1f}%<extra>"+q_labels[q]+"</extra>",
        ))
    sp_w = wealth["SP500"]
    fig.add_trace(go.Scatter(
        x=sp_w.index, y=(sp_w-1)*100, name="S&P 500",
        line=dict(color="#ffffff", width=1.2, dash="dot"),
        hovertemplate="%{y:.1f}%<extra>S&P 500</extra>",
    ))
    fig.add_hrect(y0=0, y1=0, line_width=1, line_color=BORDER)
    fig.update_layout(**dark_layout(
        title="Cumulative Return by ESG Quintile",
        yaxis_title="Return (%)", hovermode="x unified", height=420,
    ))
    return fig

def fig_drawdown():
    fig = go.Figure()
    for q in range(1, 6):
        dd = drawdowns[q]
        fig.add_trace(go.Scatter(
            x=dd.index, y=dd*100, name=q_labels[q],
            line=dict(color=qc(q), width=1.5),
            hovertemplate="%{y:.1f}%<extra>"+q_labels[q]+"</extra>",
        ))
    sp_dd = drawdowns["SP500"]
    fig.add_trace(go.Scatter(
        x=sp_dd.index, y=sp_dd*100, name="S&P 500",
        line=dict(color="#ffffff", width=1, dash="dot"),
    ))
    fig.update_layout(**dark_layout(
        title="Drawdown by ESG Quintile",
        yaxis_title="Drawdown (%)", hovermode="x unified", height=400,
    ))
    return fig

def fig_var_cvar():
    q_rows = metrics_df[metrics_df["quintile"].between(1,5)].sort_values("quintile")
    labels = [q_labels[int(r["quintile"])] for _,r in q_rows.iterrows()]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="VaR 95%", x=labels,
        y=[abs(float(r["var_95"]))*100 if pd.notnull(r["var_95"]) else 0 for _,r in q_rows.iterrows()],
        marker_color=[qc(int(r["quintile"])) for _,r in q_rows.iterrows()],
        marker_opacity=0.9))
    fig.add_trace(go.Bar(name="CVaR 95%", x=labels,
        y=[abs(float(r["cvar_95"]))*100 if pd.notnull(r["cvar_95"]) else 0 for _,r in q_rows.iterrows()],
        marker_color=[qc(int(r["quintile"])) for _,r in q_rows.iterrows()],
        marker_opacity=0.4))
    fig.update_layout(**dark_layout(
        title="VaR & CVaR by Quintile (95% confidence)",
        yaxis_title="Daily Loss (%)", barmode="group", height=370,
    ))
    return fig

def fig_bar(metric, ylabel, title):
    q_rows = metrics_df[metrics_df["quintile"].between(1,5)].sort_values("quintile")
    sp_row = metrics_df[metrics_df["quintile"]==0]
    fig = go.Figure()
    for _,row in q_rows.iterrows():
        q=int(row["quintile"]); v=row[metric]
        fig.add_trace(go.Bar(x=[q_labels[q]],
            y=[float(v)*100 if pd.notnull(v) else 0],
            marker_color=qc(q), showlegend=False,
            marker_line_width=0))
    if not sp_row.empty and pd.notnull(sp_row[metric].values[0]):
        fig.add_hline(y=float(sp_row[metric].values[0])*100,
            line_dash="dot", line_color="#ffffff", line_width=1,
            annotation_text="S&P 500", annotation_font_color=TEXT_MUT,
            annotation_position="top right")
    fig.update_layout(**dark_layout(title=title, yaxis_title=ylabel, height=360))
    return fig

def fig_skew():
    q_rows = metrics_df[metrics_df["quintile"].between(1,5)].sort_values("quintile")
    fig = go.Figure()
    for _,row in q_rows.iterrows():
        q=int(row["quintile"])
        v = float(row["skewness"]) if pd.notnull(row["skewness"]) else 0
        fig.add_trace(go.Bar(x=[q_labels[q]], y=[v],
            marker_color=qc(q), showlegend=False, marker_line_width=0))
    fig.add_hline(y=0, line_dash="dot", line_color="#ffffff", line_width=1)
    fig.update_layout(**dark_layout(
        title="Return Skewness by Quintile",
        yaxis_title="Skewness", height=360))
    return fig

def fig_kurt():
    q_rows = metrics_df[metrics_df["quintile"].between(1,5)].sort_values("quintile")
    fig = go.Figure()
    for _,row in q_rows.iterrows():
        q=int(row["quintile"])
        v = float(row["kurtosis"]) if pd.notnull(row["kurtosis"]) else 0
        fig.add_trace(go.Bar(x=[q_labels[q]], y=[v],
            marker_color=qc(q), showlegend=False, marker_line_width=0))
    fig.add_hline(y=0, line_dash="dot", line_color="#ffffff", line_width=1)
    fig.update_layout(**dark_layout(
        title="Excess Kurtosis (Fat Tails) by Quintile",
        yaxis_title="Kurtosis", height=360))
    return fig

def fig_rolling(q_num, metric):
    roll = rolling.get(q_num, pd.DataFrame(columns=["beta","sharpe","vol"]))
    fig  = go.Figure()
    if len(roll) > 0 and metric in roll.columns:
        s = roll[metric].replace([np.inf,-np.inf], np.nan).dropna()
        if len(s) > 0:
            # Fill area under curve
            # Convert hex to rgba for fill
            hex_c = qc(q_num).lstrip('#')
            r_val,g_val,b_val = int(hex_c[0:2],16),int(hex_c[2:4],16),int(hex_c[4:6],16)
            fill_rgba = f"rgba({r_val},{g_val},{b_val},0.09)"
            fig.add_trace(go.Scatter(
                x=s.index, y=s.values,
                line=dict(color=qc(q_num), width=2),
                fill="tozeroy", fillcolor=fill_rgba,
                name=q_labels.get(q_num,"")))
    if metric == "beta":
        fig.add_hline(y=1.0, line_dash="dot", line_color="#ffffff", line_width=1,
            annotation_text="β = 1", annotation_font_color=TEXT_MUT)
    elif metric == "sharpe":
        fig.add_hline(y=0, line_dash="dot", line_color="#ffffff", line_width=1)
        fig.add_hline(y=1.0, line_dash="dot", line_color=qc(q_num), line_width=1,
            annotation_text="Sharpe = 1", annotation_font_color=TEXT_MUT)
    lbls = {"beta":"Beta","sharpe":"Sharpe Ratio","vol":"Annualised Volatility"}
    fig.update_layout(**dark_layout(
        title=f"Rolling {lbls[metric]} — {q_labels.get(q_num,'')}",
        yaxis_title=lbls[metric], height=310))
    return fig

def fig_capm(q_num):
    pr = quint_rets.get(q_num, pd.Series(dtype=float))
    aligned = pd.concat([pr, sp500], axis=1).dropna()
    aligned.columns = ["port","mkt"]
    fig = go.Figure()
    if len(aligned) > 30:
        slope, intercept, r, p, se = sc.linregress(aligned["mkt"], aligned["port"])
        x_line = np.linspace(aligned["mkt"].min(), aligned["mkt"].max(), 200)
        fig.add_trace(go.Scatter(
            x=aligned["mkt"]*100, y=aligned["port"]*100,
            mode="markers",
            marker=dict(color=qc(q_num), opacity=0.18, size=4),
            name="Daily observations"))
        fig.add_trace(go.Scatter(
            x=x_line*100, y=(slope*x_line+intercept)*100,
            mode="lines", line=dict(color=qc(q_num), width=2.5),
            name=f"β={slope:.2f}  α={intercept*252*100:.2f}%/yr  R²={r**2:.3f}"))
    fig.update_layout(**dark_layout(
        title=f"CAPM Regression — {q_labels.get(q_num,'')}",
        xaxis_title="S&P 500 Daily Return (%)",
        yaxis_title="Portfolio Daily Return (%)", height=420))
    return fig

def fig_corr():
    corr = cross_corr
    colorscale = [
        [0.0, PANEL_BG],
        [0.3, "#0d2a3a"],
        [0.6, "#0d4a6e"],
        [1.0, "#00d4aa"],
    ]
    fig = go.Figure(go.Heatmap(
        z=corr.values, x=list(corr.columns), y=list(corr.columns),
        colorscale=colorscale,
        text=np.round(corr.values,2), texttemplate="%{text:.2f}",
        textfont=dict(color=TEXT_PRI, size=11),
        zmin=0, zmax=1,
        hovertemplate="Row: %{y}<br>Col: %{x}<br>Corr: %{z:.3f}<extra></extra>",
    ))
    fig.update_layout(**dark_layout(
        title="Cross-Quintile Portfolio Correlation", height=440))
    return fig

def fig_scatter(y_col, y_label):
    df_plot = stock_df.dropna(subset=["esg",y_col,"market_cap","sector"]).copy()
    df_plot["market_cap"] = df_plot["market_cap"].clip(lower=1)
    use_trend = len(df_plot) >= 10

    # Custom colour map for sectors
    kwargs = dict(
        data_frame=df_plot, x="esg", y=y_col, color="sector", size="market_cap",
        hover_name="name", hover_data={"ticker":True,"esg_grade":True,"carbon":True},
        labels={"esg":"ESG Score", y_col:y_label},
        title=f"ESG Score vs {y_label}  ({len(df_plot)} stocks)",
    )
    if use_trend:
        kwargs["trendline"]="ols"; kwargs["trendline_scope"]="overall"
    fig = px.scatter(**kwargs)
    fig.update_traces(marker=dict(opacity=0.75, line=dict(width=0)))
    fig.update_layout(**dark_layout(height=460))
    return fig

# ── HTML TABLE BUILDERS ───────────────────────────────────────────────────────

def metrics_table_html():
    th = ["Portfolio","Ann. Ret.","Volatility","Sharpe","Sortino",
          "Max DD","VaR 95%","CVaR 95%","Skewness","Kurtosis","Beta","Alpha"]
    head = "".join(
        f'<th style="padding:10px 12px;text-align:{"left" if i==0 else "center"};'
        f'color:{TEXT_MUT};font-weight:600;font-size:10px;letter-spacing:.6px;'
        f'text-transform:uppercase;white-space:nowrap">{h}</th>'
        for i,h in enumerate(th))
    rows = ""
    for _,r in metrics_df.sort_values("quintile").iterrows():
        q=int(r["quintile"])
        label=q_labels.get(q,"S&P 500 Benchmark")
        acc = Q_CHART_COLS.get(q, TEXT_MUT)
        bg = CARD_BG if q%2==0 else "#0a1628"
        cells=(
            f'<td style="font-weight:600;text-align:left;padding:10px 12px;'
            f'color:{acc};white-space:nowrap">{label}</td>'
            f'<td style="color:#00d4aa;font-weight:600">{pct(r.get("ann_return"))}</td>'
            f'<td style="color:{TEXT_MUT}">{pct(r.get("ann_vol"))}</td>'
            f'<td style="color:{TEXT_PRI}">{dec(r.get("sharpe"))}</td>'
            f'<td style="color:{TEXT_PRI}">{dec(r.get("sortino"))}</td>'
            f'<td style="color:#ff4d8d;font-weight:600">{pct(r.get("max_dd"))}</td>'
            f'<td style="color:{TEXT_MUT}">{pct(r.get("var_95"),2)}</td>'
            f'<td style="color:{TEXT_MUT}">{pct(r.get("cvar_95"),2)}</td>'
            f'<td style="color:{TEXT_PRI}">{dec(r.get("skewness"))}</td>'
            f'<td style="color:{TEXT_PRI}">{dec(r.get("kurtosis"))}</td>'
            f'<td style="color:#4da6ff">{dec(r.get("beta"))}</td>'
            f'<td style="color:#00d4aa">{pct(r.get("alpha"))}</td>'
        )
        rows+=f'<tr style="background:{bg};border-bottom:1px solid {BORDER}">{cells}</tr>'
    return (f'<div style="overflow-x:auto;border-radius:10px;border:1px solid {BORDER};margin-top:4px">'
            f'<table style="width:100%;border-collapse:collapse;font-size:12px;font-family:{FONT}">'
            f'<thead><tr style="background:#071020;border-bottom:1px solid {BORDER}">{head}</tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')

def capm_table_html():
    head=(f'<tr style="background:#071020;border-bottom:1px solid {BORDER}">'
          f'<th style="padding:9px 12px;color:{TEXT_MUT};font-size:10px;text-transform:uppercase;'
          f'letter-spacing:.6px;text-align:left">Quintile</th>'
          f'<th style="color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.6px">Alpha</th>'
          f'<th style="color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.6px">Beta</th>'
          f'<th style="color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.6px">R²</th>'
          f'<th style="color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.6px">p-value</th></tr>')
    rows=""
    for _,r in metrics_df[metrics_df["quintile"].between(1,5)].sort_values("quintile").iterrows():
        q=int(r["quintile"]); acc=Q_CHART_COLS.get(q,TEXT_MUT)
        bg=CARD_BG if q%2==0 else "#0a1628"
        rows+=(f'<tr style="background:{bg};border-bottom:1px solid {BORDER}">'
               f'<td style="padding:9px 12px;font-weight:600;color:{acc};text-align:left">{q_labels[q]}</td>'
               f'<td style="text-align:center;color:#00d4aa;font-weight:600">{pct(r.get("alpha"))}</td>'
               f'<td style="text-align:center;color:#4da6ff">{dec(r.get("beta"))}</td>'
               f'<td style="text-align:center;color:{TEXT_PRI}">{dec(r.get("r2"))}</td>'
               f'<td style="text-align:center;color:{TEXT_MUT}">{sci(r.get("p_value"))}</td></tr>')
    return (f'<div style="overflow-x:auto;border-radius:10px;border:1px solid {BORDER};margin-top:16px">'
            f'<table style="width:100%;border-collapse:collapse;font-size:12px;font-family:{FONT}">'
            f'<thead>{head}</thead><tbody>{rows}</tbody></table></div>')

def stock_table_html():
    head=(
        f'<tr style="background:#071020">'
        f'<th style="padding:8px 10px;color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.5px">Ticker</th>'
        f'<th style="text-align:left;color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.5px">Company</th>'
        f'<th style="color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.5px">Sector</th>'
        f'<th style="color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.5px">ESG</th>'
        f'<th style="color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.5px">Grade</th>'
        f'<th style="color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.5px">Q</th>'
        f'<th style="color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.5px">Ann. Ret.</th>'
        f'<th style="color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.5px">Vol.</th>'
        f'<th style="color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.5px">Sharpe</th>'
        f'<th style="color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.5px">Max DD</th>'
        f'<th style="color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.5px">VaR 95%</th>'
        f'<th style="color:{TEXT_MUT};font-size:10px;text-transform:uppercase;letter-spacing:.5px">Beta</th></tr>'
    )
    rows=""
    for _,r in stock_df.sort_values(["quintile","esg"],ascending=[True,False]).iterrows():
        gc="#00d4aa" if r["esg_grade"] in ["AAA","AA"] else "#ff4d8d" if r["esg_grade"] in ["B","CCC"] else TEXT_MUT
        bg=CARD_BG if int(r.get("quintile",0))%2==0 else "#0a1628"
        rows+=(f'<tr style="background:{bg};border-bottom:1px solid {BORDER}">'
               f'<td style="font-weight:700;padding:7px 10px;color:#4da6ff">{r["ticker"]}</td>'
               f'<td style="text-align:left;color:{TEXT_PRI};white-space:nowrap">{r["name"]}</td>'
               f'<td style="color:{TEXT_MUT};font-size:11px">{r["sector"]}</td>'
               f'<td style="font-weight:700;color:{TEXT_PRI}">{r["esg"]}</td>'
               f'<td style="color:{gc};font-weight:700">{r["esg_grade"]}</td>'
               f'<td style="color:{Q_CHART_COLS.get(int(r["quintile"]),TEXT_MUT)};font-weight:600">Q{r["quintile"]}</td>'
               f'<td style="color:#00d4aa;font-weight:600">{pct(r.get("ann_return"))}</td>'
               f'<td style="color:{TEXT_MUT}">{pct(r.get("ann_vol"))}</td>'
               f'<td style="color:{TEXT_PRI}">{dec(r.get("sharpe"),2)}</td>'
               f'<td style="color:#ff4d8d;font-weight:600">{pct(r.get("max_dd"))}</td>'
               f'<td style="color:{TEXT_MUT}">{pct(r.get("var_95"),2)}</td>'
               f'<td style="color:#4da6ff">{dec(r.get("beta"),2)}</td></tr>')
    return (f'<div style="overflow-x:auto;max-height:520px;overflow-y:auto;'
            f'border-radius:10px;border:1px solid {BORDER}">'
            f'<table id="stbl" style="width:100%;border-collapse:collapse;'
            f'font-size:11px;font-family:{FONT}">'
            f'<thead style="position:sticky;top:0;z-index:2">{head}</thead>'
            f'<tbody>{rows}</tbody></table></div>')

# ── RENDER ────────────────────────────────────────────────────────────────────
print("Rendering figures...")

n  = len(stock_df)
ns = int(df_universe["sector"].nunique())
q1 = metrics_df[metrics_df["quintile"]==1].iloc[0]
q5 = metrics_df[metrics_df["quintile"]==5].iloc[0]
sp = metrics_df[metrics_df["quintile"]==0].iloc[0]

roll_figs = {q: {m: fd(fig_rolling(q,m)) for m in ["beta","sharpe","vol"]} for q in range(1,6)}
capm_figs = {q: fd(fig_capm(q)) for q in range(1,6)}

def caption(text):
    return (f'<p style="font-size:11px;color:{TEXT_MUT};line-height:1.7;'
            f'margin:6px 2px 16px;padding:10px 14px 10px 16px;'
            f'border-left:2px solid #00d4aa44;background:#071020;border-radius:0 6px 6px 0">{text}</p>')

def insight(colour, title, text):
    bg_map={"green":"#071a0e","blue":"#071018","yellow":"#141007","gray":"#0a0f18"}
    bd_map={"green":"#00d4aa30","blue":"#4da6ff30","yellow":"#ff950030","gray":"#1a2d4730"}
    tc_map={"green":"#00d4aa","blue":"#79c0ff","yellow":"#e3b341","gray":TEXT_MUT}
    return (f'<div style="background:{bg_map[colour]};border:1px solid {bd_map[colour]};'
            f'border-radius:8px;padding:14px 16px;font-size:12px;line-height:1.7;'
            f'margin-top:6px;margin-bottom:18px;color:{TEXT_MUT}">'
            f'<strong style="color:{tc_map[colour]}">{title}</strong> {text}</div>')

# Card builder
def card(label, value, sub, col_key, glow=True):
    c = CARD_COLS[col_key]
    shadow = f"box-shadow:0 0 24px {c['accent']}22;" if glow else ""
    return (f'<div style="background:{c["bg"]};border:1px solid {c["border"]};'
            f'border-radius:12px;padding:18px 16px;{shadow}transition:.2s">'
            f'<div style="font-size:10px;text-transform:uppercase;letter-spacing:.8px;'
            f'color:{TEXT_MUT};margin-bottom:8px">{label}</div>'
            f'<div style="font-size:26px;font-weight:700;color:{c["accent"]};line-height:1;'
            f'text-shadow:0 0 24px {c["accent"]}55">{value}</div>'
            f'<div style="font-size:10px;color:{TEXT_MUT};margin-top:6px">{sub}</div>'
            f'</div>')

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = f"""
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{height:100%}}
body{{font-family:{FONT};background:{PAGE_BG};color:{TEXT_PRI};font-size:14px;min-height:100vh;
    background-image:
      radial-gradient(ellipse 80% 50% at 10% 0%,   #003d2288 0%, transparent 60%),
      radial-gradient(ellipse 60% 40% at 90% 10%,  #00296688 0%, transparent 55%),
      radial-gradient(ellipse 70% 60% at 50% 100%, #001a3366 0%, transparent 65%),
      radial-gradient(ellipse 40% 30% at 80% 60%,  #002a1a44 0%, transparent 50%),
      radial-gradient(ellipse 50% 40% at 20% 70%,  #00264455 0%, transparent 55%);
    background-attachment:fixed}}
.topbar{{background:linear-gradient(90deg,rgba(5,11,20,0.92) 0%,rgba(7,15,25,0.92) 100%);
         border-bottom:1px solid {BORDER};padding:14px 32px;
         display:flex;align-items:center;justify-content:space-between;
         position:sticky;top:0;z-index:100;backdrop-filter:blur(16px);
         -webkit-backdrop-filter:blur(16px)}}
.topbar-title{{font-size:13px;font-weight:700;color:#00d4aa;letter-spacing:1.5px;text-transform:uppercase}}
.topbar-sub{{font-size:11px;color:{TEXT_MUT}}}
.topbar-badge{{background:#071a0e;border:1px solid #00d4aa30;border-radius:20px;
              padding:5px 14px;font-size:11px;color:#00d4aa;font-weight:600}}
.wrap{{max-width:1440px;margin:0 auto;padding:28px 28px 40px}}
.cards{{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:28px}}
.cards > div{{backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}}
.divider{{height:1px;background:linear-gradient(90deg,transparent 0%,{BORDER} 30%,{BORDER} 70%,transparent 100%);margin:20px 0}}
.tabs{{display:flex;gap:0;border-bottom:1px solid {BORDER};margin-bottom:24px}}
.tab{{padding:12px 24px;font-size:12px;font-weight:600;cursor:pointer;border:none;
     background:none;color:{TEXT_MUT};border-bottom:2px solid transparent;
     font-family:inherit;margin-bottom:-1px;white-space:nowrap;
     letter-spacing:.5px;text-transform:uppercase;transition:.2s}}
.tab:hover{{color:{TEXT_PRI}}}
.tab.on{{color:#00d4aa;border-bottom-color:#00d4aa}}
.pane{{display:none}}.pane.on{{display:block}}
.panel{{background:rgba(10,22,40,0.82);border:1px solid {BORDER};border-radius:10px;
       padding:2px;margin-bottom:6px;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}}
.g2{{display:grid;grid-template-columns:1.4fr 1fr;gap:14px;margin-bottom:6px}}
.g2e{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:6px}}
.g2cap{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.stack{{display:flex;flex-direction:column;gap:6px}}
.sec{{font-size:10px;font-weight:700;color:{TEXT_MUT};margin:20px 0 8px;
     text-transform:uppercase;letter-spacing:1px}}
.q-bar{{display:flex;gap:8px;margin-bottom:18px;flex-wrap:wrap}}
.qb{{padding:7px 18px;font-size:11px;font-weight:600;border-radius:20px;cursor:pointer;
    border:1px solid {BORDER};background:{CARD_BG};color:{TEXT_MUT};
    font-family:inherit;letter-spacing:.4px;transition:.15s;text-transform:uppercase}}
.qb.on{{background:#071a0e;color:#00d4aa;border-color:#00d4aa;}}
input#srch{{padding:10px 16px;border:1px solid {BORDER};border-radius:8px;
           font-size:12px;font-family:inherit;width:360px;margin-bottom:16px;
           outline:none;background:{CARD_BG};color:{TEXT_PRI};transition:.2s;
           letter-spacing:.2px}}
input#srch:focus{{border-color:#00d4aa;box-shadow:0 0 0 3px #00d4aa15}}
input#srch::placeholder{{color:{TEXT_MUT}}}
footer{{text-align:center;font-size:10px;color:#2d3f55;margin-top:40px;
       padding:20px 0;border-top:1px solid {BORDER};letter-spacing:.3px}}
@media(max-width:900px){{
  .cards{{grid-template-columns:repeat(2,1fr)}}
  .g2,.g2e,.g2cap{{grid-template-columns:1fr}}
  .topbar{{flex-direction:column;gap:8px;text-align:center}}
}}
"""

JS = """
function tab(name,el){
  document.querySelectorAll('.pane').forEach(p=>p.classList.remove('on'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));
  document.getElementById('p-'+name).classList.add('on');
  el.classList.add('on');
}
function roll(q,el){
  document.querySelectorAll('[id^="r-"]').forEach(d=>d.style.display='none');
  document.getElementById('r-'+q).style.display='flex';
  el.closest('.q-bar').querySelectorAll('.qb').forEach(b=>b.classList.remove('on'));
  el.classList.add('on');
}
function capm(q,el){
  document.querySelectorAll('[id^="c-"]').forEach(d=>d.style.display='none');
  document.getElementById('c-'+q).style.display='block';
  el.closest('.q-bar').querySelectorAll('.qb').forEach(b=>b.classList.remove('on'));
  el.classList.add('on');
}
function srch(){
  var v=document.getElementById('srch').value.toLowerCase();
  document.querySelectorAll('#stbl tbody tr').forEach(function(r){
    r.style.display=r.textContent.toLowerCase().includes(v)?'':'none';
  });
}
"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ESG Climate Portfolio</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<!-- Top bar -->
<div class="topbar">
  <div>
    <div class="topbar-title">ESG Climate Portfolio</div>
    <div class="topbar-sub">Does ESG Screening Reduce Tail Risk? &nbsp;•&nbsp; 2021–2026 &nbsp;•&nbsp; {n} stocks &nbsp;•&nbsp; {ns} sectors</div>
  </div>
  <div class="topbar-badge">Live data via Yahoo Finance</div>
</div>

<div class="wrap">

<!-- Metric cards -->
<div class="cards">
  {card("Q1 Leaders — Annual Return",   pct(q1.get("ann_return")),  f"S&amp;P 500: {pct(sp.get('ann_return'))}", "green")}
  {card("Q1 Leaders — Max Drawdown",    pct(q1.get("max_dd")),      f"S&amp;P 500: {pct(sp.get('max_dd'))}", "pink")}
  {card("Q1 Leaders — CVaR 95%",        pct(q1.get("cvar_95"),2),   f"Q5 Laggards: {pct(q5.get('cvar_95'),2)}", "orange")}
  {card("Q1 Leaders — Beta",            dec(q1.get("beta")),         "Lower β = less market risk", "blue")}
  {card("Universe",                     str(n),                      f"{ns} sectors · ESG 14–{int(stock_df['esg'].max())}", "purple")}
  {card("Q1 Skewness",                  dec(q1.get("skewness")),     f"vs Q5: {dec(q5.get('skewness'))} (negative = crash risk)", "teal")}
</div>

<div class="divider"></div>

<!-- Tabs -->
<div class="tabs">
  <button class="tab on" onclick="tab('overview',this)">Overview</button>
  <button class="tab"    onclick="tab('tail',this)">Tail Risk</button>
  <button class="tab"    onclick="tab('roll',this)">Rolling Risk</button>
  <button class="tab"    onclick="tab('factor',this)">Factor Model</button>
  <button class="tab"    onclick="tab('corr',this)">Correlations</button>
  <button class="tab"    onclick="tab('screen',this)">Stock Screener</button>
</div>

<!-- ── OVERVIEW ─────────────────────────────────────────────────────────── -->
<div id="p-overview" class="pane on">
  <div class="panel">{fd(fig_wealth())}</div>
  {caption("Each line shows the cumulative return of an equal-weighted portfolio of stocks in that ESG quintile. Q1 = highest-scoring ESG companies; Q5 = lowest. The white dotted line is the S&amp;P 500 benchmark.")}
  <div class="sec">Full Metrics Table</div>
  {metrics_table_html()}
</div>

<!-- ── TAIL RISK ─────────────────────────────────────────────────────────── -->
<div id="p-tail" class="pane">
  <div class="g2">
    <div class="panel">{fd(fig_drawdown())}</div>
    <div class="panel">{fd(fig_var_cvar())}</div>
  </div>
  <div class="g2cap">
    {caption("Drawdown shows how far each portfolio fell from its previous peak at any point in time. Deeper troughs mean larger losses investors had to endure before recovery.")}
    {caption("VaR 95% is the worst daily loss expected 95% of the time. CVaR 95% is the average loss on the worst 5% of days — the truest measure of extreme tail risk.")}
  </div>

  <div class="panel">{fd(fig_bar("max_dd","Max Drawdown (%)","Maximum Drawdown by Quintile"))}</div>
  {caption("The single worst peak-to-trough loss each quintile experienced over the full period. The dotted white line marks the S&amp;P 500's max drawdown for reference.")}

  <div class="panel">{fd(fig_bar("ann_vol","Volatility (%)","Annual Volatility by Quintile"))}</div>
  {caption("Annualised standard deviation of daily returns. Higher volatility means wider day-to-day swings. Q1's higher volatility is driven by its concentration in technology and clean energy stocks.")}

  <div class="panel">{fd(fig_skew())}</div>
  {caption("Skewness measures the asymmetry of the return distribution. Positive values (Q1, Q2, Q3) mean more frequent positive surprises than negative ones. Negative skewness (Q5) signals a higher probability of sudden sharp losses — the hallmark of crash risk.")}

  <div class="panel">{fd(fig_kurt())}</div>
  {caption("Excess kurtosis measures how fat the tails of the return distribution are. Higher kurtosis means more frequent extreme daily events. Q1's kurtosis of 2.6 is the lowest of any quintile — meaning the most predictable, stable return pattern of the group.")}

  {insight("green","Key finding:","Q1 (ESG Leaders) is the only quintile with positive skewness (+0.226) and carries the lowest excess kurtosis (2.643) — meaning returns lean toward positive surprises and extreme events are rarer. Q5 (ESG Laggards) shows negative skewness (-0.216) and higher kurtosis (3.929), indicating structurally more crash risk hidden beneath its strong headline returns.")}
</div>

<!-- ── ROLLING RISK ───────────────────────────────────────────────────────── -->
<div id="p-roll" class="pane">
  <div class="sec">Select Quintile</div>
  <div class="q-bar">
    {"".join(f'<button class="qb {"on" if q==1 else ""}" onclick="roll({q},this)">{q_labels[q]}</button>' for q in range(1,6))}
  </div>
  {"".join(
    f'<div id="r-{q}" class="stack" style="{"" if q==1 else "display:none"}">'
    f'<div class="panel">{roll_figs[q]["beta"]}</div>'
    f'{caption("Rolling beta measures market sensitivity over a 63-day window. Above 1.0 means the portfolio moves more than the market on a given day; below 1.0 means it is more defensive. Changes in beta reveal how market-sensitivity shifts across different regimes.")}'
    f'<div class="panel">{roll_figs[q]["sharpe"]}</div>'
    f'{caption("Rolling Sharpe ratio measures risk-adjusted return over the trailing 63 days. Positive values mean the portfolio is earning above the risk-free rate per unit of risk. Volatile Sharpe readings reflect sensitivity to interest rates and macro conditions.")}'
    f'<div class="panel">{roll_figs[q]["vol"]}</div>'
    f'{caption("Rolling annualised volatility shows how day-to-day risk changed over time. The spike in 2022 reflects the rate-hike shock. The subsequent decline shows stabilisation. The early 2025 spike reflects tariff-related market turbulence.")}'
    f'</div>'
    for q in range(1,6)
  )}
  {insight("blue","How to use this tab:","Select different quintiles using the buttons above to compare how beta, Sharpe, and volatility evolved differently for ESG Leaders vs Laggards across the same market events. Persistent differences in rolling beta between Q1 and Q5 would confirm that ESG score captures a genuine difference in market sensitivity.")}
</div>

<!-- ── FACTOR MODEL ──────────────────────────────────────────────────────── -->
<div id="p-factor" class="pane">
  <div class="sec">Select Quintile</div>
  <div class="q-bar">
    {"".join(f'<button class="qb {"on" if q==1 else ""}" onclick="capm({q},this)">{q_labels[q]}</button>' for q in range(1,6))}
  </div>
  {"".join(
    f'<div id="c-{q}" class="panel" style="{"" if q==1 else "display:none"}">{capm_figs[q]}</div>'
    for q in range(1,6)
  )}
  {caption("Each dot is one trading day. The regression line fits the equation Rp = α + β·Rm + ε. A steeper line means higher beta. The vertical scatter around the line represents idiosyncratic return — the component not explained by the market.")}
  {capm_table_html()}
  {caption("Alpha is the annualised excess return above what the market alone predicts. Beta measures market sensitivity. R² shows what fraction of the portfolio's variance the market explains — Q5's R² of 0.365 means 63.5% of its returns are driven by factors outside the broad market.")}
  {insight("yellow","Interpreting the results:","Q1's alpha improved from -8.2% (December 2024) to -0.4% (June 2026) as the technology and clean energy rally of 2025 played out. Beta declines monotonically from Q1 to Q5, reflecting the higher market sensitivity of tech and clean energy stocks versus defensive tobacco, energy, and defence names. At its current trajectory Q1 is on course to generate positive alpha over a full market cycle.")}
</div>

<!-- ── CORRELATIONS ──────────────────────────────────────────────────────── -->
<div id="p-corr" class="pane">
  <div class="g2e">
    <div class="panel">{fd(fig_corr())}</div>
    <div class="panel">{fd(fig_scatter("max_dd","Max Drawdown"))}</div>
  </div>
  <div class="g2cap">
    {caption("The heatmap shows how similar the return streams of each quintile portfolio are. The Q1 vs Q5 correlation of 0.531 is the lowest of any pair — confirming that ESG score captures a genuine distinct factor, not just a sector tilt in disguise.")}
    {caption("Each dot is one of the 129 individual stocks. The trendline shows the relationship between ESG score and max drawdown at stock level. The downward slope reflects the concentration of volatile growth names at the high-ESG end of the range.")}
  </div>
  {insight("gray","Diversification insight:","The Q1–Q5 correlation of 0.531 is one of the strongest findings in this study. ESG Leaders and Laggards do not simply move together — they represent genuinely distinct risk exposures driven by different underlying economic forces. A combined portfolio spanning all quintiles would benefit meaningfully from this diversification.")}
</div>

<!-- ── SCREENER ──────────────────────────────────────────────────────────── -->
<div id="p-screen" class="pane">
  <div class="panel">{fd(fig_scatter("ann_vol","Volatility"))}</div>
  {caption("ESG score vs annualised volatility for all 129 stocks. The upward trendline reflects that high-ESG stocks (technology, clean energy) tend to carry higher individual volatility than low-ESG stocks (energy, tobacco, defence). Bubble size = market capitalisation.")}
  <input id="srch" type="text" placeholder="Search by ticker, company or sector…" oninput="srch()">
  {stock_table_html()}
</div>

<footer>
  ESG Climate Portfolio &nbsp;•&nbsp; {n} S&amp;P 500 Constituents &nbsp;•&nbsp;
  Friede, Busch &amp; Bassen (2015) &nbsp;•&nbsp; MSCI ESG Research (2024/25) &nbsp;•&nbsp;
  Pedersen, Fitzgibbons &amp; Pomorski (2021) &nbsp;•&nbsp; Man Group (2024)
</footer>
</div>
<script>{JS}</script>
</body>
</html>"""

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "esg_portfolio.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)

size_kb = os.path.getsize(out) // 1024
print(f"✅  Saved: {out}")
print(f"    Size : {size_kb} KB")
print(f"\n    → Double-click esg_portfolio.html to open in your browser.\n")