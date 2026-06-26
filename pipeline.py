"""
pipeline.py — Analytics engine
================================
Runs the full analytics pipeline:
  1. Download prices from Yahoo Finance
  2. Validate and clean data
  3. Compute daily / monthly returns
  4. Build equal-weighted quintile portfolios
  5. Risk metrics: Sharpe, Sortino, VaR, CVaR, drawdown, beta, alpha
  6. CAPM regression per quintile
  7. Rolling beta, Sharpe, volatility
  8. Correlation matrices
  9. Per-stock metrics

Usage:
  import pipeline as pl
  data = pl.run(df_universe)
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

# ── CONFIG ────────────────────────────────────────────────────────────────────

START       = "2020-01-01"
END         = "2026-06-01"
RISK_FREE   = 0.05          # annual risk-free rate (approx US 3m T-bill)
VAR_LEVEL   = 0.95          # confidence level for VaR / CVaR
ROLLING_WIN = 63            # rolling window in trading days (~3 months)

QUINTILE_COLORS = {
    1: "#1b4332",   # deep green  — ESG Leaders
    2: "#2d6a4f",
    3: "#74c69d",
    4: "#f4a261",
    5: "#c1121f",   # red         — ESG Laggards
}
QUINTILE_LABELS = {
    1: "Q1 – ESG Leaders",
    2: "Q2 – Above Average",
    3: "Q3 – Middle",
    4: "Q4 – Below Average",
    5: "Q5 – ESG Laggards",
}

# ── STAGE 1: LOAD ─────────────────────────────────────────────────────────────

def load(df_universe):
    from universe import fetch_live_prices

    tickers = df_universe["ticker"].tolist()
    prices  = fetch_live_prices(tickers, START, END)

    # Keep only tickers that downloaded successfully
    available   = [t for t in tickers if t in prices.columns]
    df_universe = df_universe[df_universe["ticker"].isin(available)].copy().reset_index(drop=True)

    # Re-assign quintiles on the surviving universe so each Q stays balanced
    df_universe["quintile_num"] = pd.qcut(
        df_universe["esg"], q=5, labels=[5, 4, 3, 2, 1]
    ).astype(int)

    print(f"  {len(df_universe)} stocks retained  |  "
          f"{len(prices)} trading days  |  "
          f"{prices.index[0].date()} → {prices.index[-1].date()}")

    return prices, df_universe

# ── STAGE 2: RETURNS ──────────────────────────────────────────────────────────

def compute_returns(prices):
    daily   = prices.pct_change().dropna()
    monthly = prices.resample("ME").last().pct_change().dropna()
    return daily, monthly

# ── STAGE 3: QUINTILE PORTFOLIOS ─────────────────────────────────────────────

def build_quintile_portfolios(daily, df_universe):
    """
    Equal-weight all stocks within each quintile.
    Always creates keys 1–5 so downstream code never sees KeyError.
    """
    portfolios = {}
    for q in range(1, 6):
        members = df_universe[df_universe["quintile_num"] == q]["ticker"].tolist()
        members = [t for t in members if t in daily.columns]
        if members:
            portfolios[q] = daily[members].mean(axis=1)
            print(f"  Q{q}: {len(members)} stocks")
        else:
            portfolios[q] = pd.Series(0.0, index=daily.index)
            print(f"  Q{q}: no stocks available (filled with zeros)")

    portfolios["LS"] = portfolios[1] - portfolios[5]   # long Q1 / short Q5 factor
    return portfolios

# ── STAGE 4: RISK METRICS ─────────────────────────────────────────────────────

def risk_metrics(ret_series, label="Portfolio"):
    """
    Full risk metric suite for a daily return series.
    Returns NaN for all metrics if fewer than 30 observations.
    """
    r = ret_series.dropna()

    null = {
        "label": label, "n_obs": len(r),
        "ann_return": np.nan, "ann_vol": np.nan,
        "sharpe": np.nan, "sortino": np.nan,
        "max_dd": np.nan, "calmar": np.nan,
        "var_95": np.nan, "cvar_95": np.nan,
        "skewness": np.nan, "kurtosis": np.nan,
        "win_rate": np.nan,
    }

    if len(r) < 30 or r.std() == 0:
        return null

    rf_d    = RISK_FREE / 252
    ann_ret = r.mean() * 252
    ann_vol = r.std()  * np.sqrt(252)

    # Sharpe & Sortino
    sharpe   = (r.mean() - rf_d) / r.std() * np.sqrt(252)
    downside = r[r < rf_d].std()
    sortino  = (ann_ret - RISK_FREE) / (downside * np.sqrt(252)) if downside > 0 else np.nan

    # Drawdown
    cum      = (1 + r).cumprod()
    roll_max = cum.cummax()
    dd       = (cum - roll_max) / roll_max
    mdd      = dd.min()
    calmar   = ann_ret / abs(mdd) if mdd != 0 else np.nan

    # Tail risk
    var  = np.percentile(r, (1 - VAR_LEVEL) * 100)
    tail = r[r <= var]
    cvar = tail.mean() if len(tail) > 0 else np.nan

    return {
        "label":      label,
        "n_obs":      len(r),
        "ann_return": ann_ret,
        "ann_vol":    ann_vol,
        "sharpe":     sharpe,
        "sortino":    sortino,
        "max_dd":     mdd,
        "calmar":     calmar,
        "var_95":     var,
        "cvar_95":    cvar,
        "skewness":   stats.skew(r),
        "kurtosis":   stats.kurtosis(r),   # excess kurtosis
        "win_rate":   (r > 0).mean(),
    }

# ── STAGE 5: CAPM REGRESSION ─────────────────────────────────────────────────

def capm_regression(port_ret, sp500_ret):
    """OLS regression: Rp = α + β·Rm + ε"""
    aligned = pd.concat([port_ret, sp500_ret], axis=1).dropna()
    aligned.columns = ["port", "mkt"]

    null = {"beta": np.nan, "alpha": np.nan, "r2": np.nan,
            "p_value": np.nan, "se": np.nan}

    if len(aligned) < 30 or aligned["port"].std() == 0:
        return null

    slope, intercept, r, p, se = stats.linregress(aligned["mkt"], aligned["port"])
    return {
        "beta":    slope,
        "alpha":   intercept * 252,   # annualised
        "r2":      r ** 2,
        "p_value": p,
        "se":      se,
    }

# ── STAGE 6: ROLLING METRICS ──────────────────────────────────────────────────

def rolling_metrics(port_ret, sp500_ret, window=ROLLING_WIN):
    """Rolling beta, Sharpe, and volatility over a fixed window."""
    aligned = pd.concat([port_ret, sp500_ret], axis=1).dropna()
    aligned.columns = ["port", "mkt"]
    rf_d = RISK_FREE / 252

    betas, sharpes, vols, idx = [], [], [], []
    for i in range(window, len(aligned)):
        w  = aligned.iloc[i - window:i]
        cv = np.cov(w["port"], w["mkt"])
        b  = cv[0, 1] / cv[1, 1] if cv[1, 1] > 0 else np.nan
        s  = ((w["port"].mean() - rf_d) / w["port"].std() * np.sqrt(252)
              if w["port"].std() > 0 else np.nan)
        v  = w["port"].std() * np.sqrt(252)
        betas.append(b); sharpes.append(s); vols.append(v)
        idx.append(aligned.index[i])

    return pd.DataFrame({"beta": betas, "sharpe": sharpes, "vol": vols}, index=idx)

# ── HELPERS ───────────────────────────────────────────────────────────────────

def drawdown_series(ret):
    cum      = (1 + ret).cumprod()
    roll_max = cum.cummax()
    return (cum - roll_max) / roll_max

def cumulative_wealth(ret):
    return (1 + ret).cumprod()

# ── MAIN PIPELINE ─────────────────────────────────────────────────────────────

def run(df_universe):
    """
    Run the full pipeline and return a dict of everything
    needed by export_html.py.
    """

    # 1 — Load
    print("  Loading prices from Yahoo Finance...")
    prices, df_universe = load(df_universe)

    # 2 — Returns
    print("  Computing returns...")
    daily, monthly = compute_returns(prices)
    sp500 = daily["SP500"]

    # 3 — Quintile portfolios
    print("  Building quintile portfolios...")
    quint_rets = build_quintile_portfolios(daily, df_universe)

    # 4 — Risk metrics per quintile
    print("  Computing risk metrics...")
    metrics_rows = []
    for q in range(1, 6):
        m = risk_metrics(quint_rets[q], label=QUINTILE_LABELS[q])
        m["quintile"] = q
        capm = capm_regression(quint_rets[q], sp500)
        m.update(capm)
        metrics_rows.append(m)

    # S&P 500 baseline row
    sp_m = risk_metrics(sp500, "S&P 500 Benchmark")
    sp_m["quintile"] = 0
    sp_m.update({"beta": 1.0, "alpha": 0.0, "r2": 1.0, "p_value": 0.0, "se": 0.0})
    metrics_rows.append(sp_m)
    metrics_df = pd.DataFrame(metrics_rows)

    # 5 — Rolling metrics
    print("  Computing rolling metrics...")
    rolling = {}
    for q in range(1, 6):
        r = quint_rets[q]
        if r.std() > 0 and len(r) > ROLLING_WIN:
            rolling[q] = rolling_metrics(r, sp500)
        else:
            rolling[q] = pd.DataFrame(columns=["beta", "sharpe", "vol"])

    # 6 — Drawdown and wealth series
    print("  Computing drawdown & wealth series...")
    drawdowns = {q: drawdown_series(quint_rets[q]) for q in range(1, 6)}
    drawdowns["SP500"] = drawdown_series(sp500)
    wealth    = {q: cumulative_wealth(quint_rets[q]) for q in range(1, 6)}
    wealth["SP500"] = cumulative_wealth(sp500)

    # 7 — Correlation matrices
    print("  Computing correlations...")
    quint_ret_df = pd.DataFrame({QUINTILE_LABELS[q]: quint_rets[q] for q in range(1, 6)})
    quint_ret_df["S&P 500"] = sp500
    cross_corr = quint_ret_df.corr()

    # 8 — Per-stock metrics
    print("  Computing per-stock metrics...")
    stock_rows = []
    for _, row in df_universe.iterrows():
        t = row["ticker"]
        if t not in daily.columns:
            continue
        m    = risk_metrics(daily[t], label=row["name"])
        capm = capm_regression(daily[t], sp500)
        stock_rows.append({
            "ticker":     t,
            "name":       row["name"],
            "sector":     row["sector"],
            "industry":   row["industry"],
            "esg":        row["esg"],
            "esg_grade":  row["esg_grade"],
            "carbon":     row["carbon"],
            "market_cap": row["market_cap"],
            "quintile":   row["quintile_num"],
            **{k: m[k] for k in ["ann_return","ann_vol","sharpe","max_dd",
                                  "var_95","cvar_95","skewness","kurtosis"]},
            **{k: capm[k] for k in ["beta","alpha","r2"]},
        })
    stock_df = pd.DataFrame(stock_rows)

    # Clean market_cap — Plotly size param cannot have NaN or 0
    stock_df["market_cap"] = (
        pd.to_numeric(stock_df["market_cap"], errors="coerce")
        .fillna(1).replace(0, 1).clip(lower=1)
    )

    print("  Done.\n")

    return {
        "universe":   df_universe,
        "prices":     prices,
        "daily":      daily,
        "monthly":    monthly,
        "sp500":      sp500,
        "quint_rets": quint_rets,
        "metrics_df": metrics_df,
        "rolling":    rolling,
        "drawdowns":  drawdowns,
        "wealth":     wealth,
        "cross_corr": cross_corr,
        "stock_df":   stock_df,
        "q_colors":   QUINTILE_COLORS,
        "q_labels":   QUINTILE_LABELS,
    }
