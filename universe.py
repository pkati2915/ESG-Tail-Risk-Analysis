"""
universe.py — Stock universe definition
========================================
139 S&P 500 constituent stocks with ESG scores,
sectors, carbon intensity, and market cap.

ESG scores are MSCI-style (0–100):
  80–100 : AAA / AA  — ESG Leaders    (Q1)
  65–79  : A         — Above Average  (Q2)
  50–64  : BBB       — Middle         (Q3)
  35–49  : BB        — Below Average  (Q4)
  0–34   : B / CCC   — ESG Laggards   (Q5)
"""

import pandas as pd
import numpy as np

UNIVERSE = [
    # ── RENEWABLE ENERGY / CLEAN TECH ────────────────────────────────────────
    {"ticker":"NEE",   "name":"NextEra Energy",         "sector":"Utilities",        "industry":"Renewable Energy",   "esg":91, "carbon":12,  "market_cap":130},
    {"ticker":"ENPH",  "name":"Enphase Energy",          "sector":"Technology",       "industry":"Solar",              "esg":85, "carbon":8,   "market_cap":15},
    {"ticker":"SEDG",  "name":"SolarEdge",               "sector":"Technology",       "industry":"Solar",              "esg":84, "carbon":10,  "market_cap":8},
    {"ticker":"BEP",   "name":"Brookfield Renewable",    "sector":"Utilities",        "industry":"Renewable Energy",   "esg":89, "carbon":6,   "market_cap":12},
    {"ticker":"ITRI",  "name":"Itron",                   "sector":"Technology",       "industry":"Smart Grid",         "esg":82, "carbon":22,  "market_cap":4},
    {"ticker":"FSLR",  "name":"First Solar",             "sector":"Technology",       "industry":"Solar",              "esg":88, "carbon":14,  "market_cap":20},
    {"ticker":"RUN",   "name":"Sunrun",                  "sector":"Utilities",        "industry":"Solar",              "esg":80, "carbon":9,   "market_cap":3},
    {"ticker":"PLUG",  "name":"Plug Power",              "sector":"Industrials",      "industry":"Hydrogen",           "esg":79, "carbon":5,   "market_cap":2},
    {"ticker":"BE",    "name":"Bloom Energy",            "sector":"Industrials",      "industry":"Fuel Cells",         "esg":81, "carbon":11,  "market_cap":3},

    # ── ELECTRIC VEHICLES ────────────────────────────────────────────────────
    {"ticker":"TSLA",  "name":"Tesla",                   "sector":"Consumer Disc.",   "industry":"EVs",                "esg":78, "carbon":0,   "market_cap":800},
    {"ticker":"RIVN",  "name":"Rivian",                  "sector":"Consumer Disc.",   "industry":"EVs",                "esg":76, "carbon":0,   "market_cap":15},
    {"ticker":"LCID",  "name":"Lucid Group",             "sector":"Consumer Disc.",   "industry":"EVs",                "esg":75, "carbon":0,   "market_cap":8},

    # ── TECHNOLOGY (high ESG) ────────────────────────────────────────────────
    {"ticker":"MSFT",  "name":"Microsoft",               "sector":"Technology",       "industry":"Software",           "esg":93, "carbon":15,  "market_cap":2800},
    {"ticker":"AAPL",  "name":"Apple",                   "sector":"Technology",       "industry":"Hardware",           "esg":87, "carbon":22,  "market_cap":2900},
    {"ticker":"GOOGL", "name":"Alphabet",                "sector":"Technology",       "industry":"Internet",           "esg":82, "carbon":18,  "market_cap":1800},
    {"ticker":"CRM",   "name":"Salesforce",              "sector":"Technology",       "industry":"Software",           "esg":90, "carbon":12,  "market_cap":230},
    {"ticker":"ADBE",  "name":"Adobe",                   "sector":"Technology",       "industry":"Software",           "esg":88, "carbon":10,  "market_cap":230},
    {"ticker":"INTC",  "name":"Intel",                   "sector":"Technology",       "industry":"Semiconductors",     "esg":85, "carbon":35,  "market_cap":200},
    {"ticker":"TXN",   "name":"Texas Instruments",       "sector":"Technology",       "industry":"Semiconductors",     "esg":83, "carbon":28,  "market_cap":170},
    {"ticker":"HPQ",   "name":"HP Inc",                  "sector":"Technology",       "industry":"Hardware",           "esg":86, "carbon":20,  "market_cap":30},
    {"ticker":"CSCO",  "name":"Cisco Systems",           "sector":"Technology",       "industry":"Networking",         "esg":89, "carbon":16,  "market_cap":210},
    {"ticker":"QCOM",  "name":"Qualcomm",                "sector":"Technology",       "industry":"Semiconductors",     "esg":80, "carbon":25,  "market_cap":180},

    # ── HEALTHCARE ───────────────────────────────────────────────────────────
    {"ticker":"JNJ",   "name":"Johnson & Johnson",       "sector":"Healthcare",       "industry":"Pharma",             "esg":78, "carbon":38,  "market_cap":430},
    {"ticker":"UNH",   "name":"UnitedHealth",            "sector":"Healthcare",       "industry":"Insurance",          "esg":72, "carbon":20,  "market_cap":480},
    {"ticker":"ABT",   "name":"Abbott Labs",             "sector":"Healthcare",       "industry":"Medical Devices",    "esg":80, "carbon":30,  "market_cap":200},
    {"ticker":"BMY",   "name":"Bristol-Myers Squibb",    "sector":"Healthcare",       "industry":"Pharma",             "esg":76, "carbon":42,  "market_cap":160},
    {"ticker":"MDT",   "name":"Medtronic",               "sector":"Healthcare",       "industry":"Medical Devices",    "esg":82, "carbon":28,  "market_cap":110},
    {"ticker":"ISRG",  "name":"Intuitive Surgical",      "sector":"Healthcare",       "industry":"Robotics",           "esg":79, "carbon":18,  "market_cap":140},
    {"ticker":"AMGN",  "name":"Amgen",                   "sector":"Healthcare",       "industry":"Biotech",            "esg":75, "carbon":35,  "market_cap":150},
    {"ticker":"GILD",  "name":"Gilead Sciences",         "sector":"Healthcare",       "industry":"Biotech",            "esg":73, "carbon":32,  "market_cap":90},
    {"ticker":"VRTX",  "name":"Vertex Pharma",           "sector":"Healthcare",       "industry":"Biotech",            "esg":77, "carbon":22,  "market_cap":110},
    {"ticker":"REGN",  "name":"Regeneron",               "sector":"Healthcare",       "industry":"Biotech",            "esg":71, "carbon":26,  "market_cap":95},
    {"ticker":"DHR",   "name":"Danaher",                 "sector":"Healthcare",       "industry":"Life Sciences",      "esg":82, "carbon":25,  "market_cap":195},
    {"ticker":"TMO",   "name":"Thermo Fisher",           "sector":"Healthcare",       "industry":"Life Sciences",      "esg":80, "carbon":28,  "market_cap":220},
    {"ticker":"BDX",   "name":"Becton Dickinson",        "sector":"Healthcare",       "industry":"Medical Devices",    "esg":78, "carbon":30,  "market_cap":70},

    # ── FINANCIALS ───────────────────────────────────────────────────────────
    {"ticker":"JPM",   "name":"JPMorgan Chase",          "sector":"Financials",       "industry":"Banking",            "esg":68, "carbon":45,  "market_cap":480},
    {"ticker":"BAC",   "name":"Bank of America",         "sector":"Financials",       "industry":"Banking",            "esg":70, "carbon":40,  "market_cap":290},
    {"ticker":"GS",    "name":"Goldman Sachs",           "sector":"Financials",       "industry":"Investment Banking", "esg":62, "carbon":30,  "market_cap":130},
    {"ticker":"MS",    "name":"Morgan Stanley",          "sector":"Financials",       "industry":"Investment Banking", "esg":65, "carbon":28,  "market_cap":150},
    {"ticker":"WFC",   "name":"Wells Fargo",             "sector":"Financials",       "industry":"Banking",            "esg":58, "carbon":42,  "market_cap":200},
    {"ticker":"BLK",   "name":"BlackRock",               "sector":"Financials",       "industry":"Asset Management",   "esg":74, "carbon":22,  "market_cap":110},
    {"ticker":"SCHW",  "name":"Charles Schwab",          "sector":"Financials",       "industry":"Brokerage",          "esg":67, "carbon":18,  "market_cap":130},
    {"ticker":"AXP",   "name":"American Express",        "sector":"Financials",       "industry":"Payments",           "esg":69, "carbon":25,  "market_cap":140},
    {"ticker":"V",     "name":"Visa",                    "sector":"Financials",       "industry":"Payments",           "esg":72, "carbon":15,  "market_cap":500},
    {"ticker":"MA",    "name":"Mastercard",              "sector":"Financials",       "industry":"Payments",           "esg":73, "carbon":14,  "market_cap":420},

    # ── CONSUMER STAPLES ─────────────────────────────────────────────────────
    {"ticker":"PG",    "name":"Procter & Gamble",        "sector":"Consumer Staples", "industry":"Household Products", "esg":76, "carbon":55,  "market_cap":360},
    {"ticker":"KO",    "name":"Coca-Cola",               "sector":"Consumer Staples", "industry":"Beverages",          "esg":68, "carbon":60,  "market_cap":260},
    {"ticker":"PEP",   "name":"PepsiCo",                 "sector":"Consumer Staples", "industry":"Beverages",          "esg":70, "carbon":58,  "market_cap":240},
    {"ticker":"COST",  "name":"Costco",                  "sector":"Consumer Staples", "industry":"Retail",             "esg":65, "carbon":48,  "market_cap":280},
    {"ticker":"WMT",   "name":"Walmart",                 "sector":"Consumer Staples", "industry":"Retail",             "esg":63, "carbon":72,  "market_cap":450},
    {"ticker":"MDLZ",  "name":"Mondelez",                "sector":"Consumer Staples", "industry":"Food",               "esg":67, "carbon":62,  "market_cap":90},
    {"ticker":"CL",    "name":"Colgate-Palmolive",       "sector":"Consumer Staples", "industry":"Household Products", "esg":74, "carbon":50,  "market_cap":65},
    {"ticker":"GIS",   "name":"General Mills",           "sector":"Consumer Staples", "industry":"Food",               "esg":66, "carbon":65,  "market_cap":40},
    {"ticker":"KHC",   "name":"Kraft Heinz",             "sector":"Consumer Staples", "industry":"Food",               "esg":55, "carbon":80,  "market_cap":40},
    {"ticker":"HRL",   "name":"Hormel Foods",            "sector":"Consumer Staples", "industry":"Food",               "esg":52, "carbon":88,  "market_cap":20},

    # ── INDUSTRIALS ──────────────────────────────────────────────────────────
    {"ticker":"HON",   "name":"Honeywell",               "sector":"Industrials",      "industry":"Conglomerate",       "esg":75, "carbon":55,  "market_cap":140},
    {"ticker":"MMM",   "name":"3M",                      "sector":"Industrials",      "industry":"Conglomerate",       "esg":60, "carbon":70,  "market_cap":55},
    {"ticker":"GE",    "name":"GE Aerospace",            "sector":"Industrials",      "industry":"Aerospace",          "esg":65, "carbon":80,  "market_cap":160},
    {"ticker":"CAT",   "name":"Caterpillar",             "sector":"Industrials",      "industry":"Machinery",          "esg":58, "carbon":95,  "market_cap":150},
    {"ticker":"DE",    "name":"Deere & Co",              "sector":"Industrials",      "industry":"Machinery",          "esg":62, "carbon":90,  "market_cap":120},
    {"ticker":"EMR",   "name":"Emerson Electric",        "sector":"Industrials",      "industry":"Automation",         "esg":70, "carbon":60,  "market_cap":65},
    {"ticker":"ETN",   "name":"Eaton Corp",              "sector":"Industrials",      "industry":"Power Mgmt",         "esg":78, "carbon":45,  "market_cap":100},
    {"ticker":"ROK",   "name":"Rockwell Automation",     "sector":"Industrials",      "industry":"Automation",         "esg":80, "carbon":38,  "market_cap":35},
    {"ticker":"XYL",   "name":"Xylem",                   "sector":"Industrials",      "industry":"Water Tech",         "esg":85, "carbon":30,  "market_cap":20},
    {"ticker":"CARR",  "name":"Carrier Global",          "sector":"Industrials",      "industry":"HVAC",               "esg":72, "carbon":65,  "market_cap":55},

    # ── REAL ESTATE ──────────────────────────────────────────────────────────
    {"ticker":"AMT",   "name":"American Tower",          "sector":"Real Estate",      "industry":"Cell Towers",        "esg":72, "carbon":40,  "market_cap":100},
    {"ticker":"PLD",   "name":"Prologis",                "sector":"Real Estate",      "industry":"Logistics REITs",    "esg":80, "carbon":35,  "market_cap":110},
    {"ticker":"EQIX",  "name":"Equinix",                 "sector":"Real Estate",      "industry":"Data Centers",       "esg":83, "carbon":28,  "market_cap":80},
    {"ticker":"PSA",   "name":"Public Storage",          "sector":"Real Estate",      "industry":"Self-Storage",       "esg":65, "carbon":50,  "market_cap":55},
    {"ticker":"CBRE",  "name":"CBRE Group",              "sector":"Real Estate",      "industry":"Real Estate Svcs",   "esg":78, "carbon":22,  "market_cap":35},

    # ── MATERIALS ────────────────────────────────────────────────────────────
    {"ticker":"LIN",   "name":"Linde",                   "sector":"Materials",        "industry":"Industrial Gases",   "esg":74, "carbon":110, "market_cap":200},
    {"ticker":"APD",   "name":"Air Products",            "sector":"Materials",        "industry":"Industrial Gases",   "esg":72, "carbon":120, "market_cap":60},
    {"ticker":"NEM",   "name":"Newmont",                 "sector":"Materials",        "industry":"Gold Mining",        "esg":55, "carbon":180, "market_cap":45},
    {"ticker":"FCX",   "name":"Freeport-McMoRan",        "sector":"Materials",        "industry":"Copper Mining",      "esg":48, "carbon":220, "market_cap":55},
    {"ticker":"NUE",   "name":"Nucor",                   "sector":"Materials",        "industry":"Steel",              "esg":52, "carbon":280, "market_cap":35},
    {"ticker":"ALB",   "name":"Albemarle",               "sector":"Materials",        "industry":"Lithium",            "esg":68, "carbon":95,  "market_cap":15},
    {"ticker":"CF",    "name":"CF Industries",           "sector":"Materials",        "industry":"Fertilizers",        "esg":42, "carbon":380, "market_cap":15},
    {"ticker":"MOS",   "name":"Mosaic",                  "sector":"Materials",        "industry":"Fertilizers",        "esg":40, "carbon":360, "market_cap":12},
    {"ticker":"IP",    "name":"International Paper",     "sector":"Materials",        "industry":"Packaging",          "esg":58, "carbon":200, "market_cap":18},

    # ── ENERGY — TRADITIONAL (low ESG) ───────────────────────────────────────
    {"ticker":"XOM",   "name":"ExxonMobil",              "sector":"Energy",           "industry":"Oil & Gas",          "esg":32, "carbon":580, "market_cap":450},
    {"ticker":"CVX",   "name":"Chevron",                 "sector":"Energy",           "industry":"Oil & Gas",          "esg":35, "carbon":540, "market_cap":300},
    {"ticker":"COP",   "name":"ConocoPhillips",          "sector":"Energy",           "industry":"Oil & Gas",          "esg":38, "carbon":490, "market_cap":140},
    {"ticker":"EOG",   "name":"EOG Resources",           "sector":"Energy",           "industry":"Oil & Gas",          "esg":40, "carbon":460, "market_cap":75},
    {"ticker":"SLB",   "name":"Schlumberger",            "sector":"Energy",           "industry":"Oil Services",       "esg":42, "carbon":420, "market_cap":75},
    {"ticker":"MPC",   "name":"Marathon Petroleum",      "sector":"Energy",           "industry":"Refining",           "esg":30, "carbon":650, "market_cap":60},
    {"ticker":"VLO",   "name":"Valero Energy",           "sector":"Energy",           "industry":"Refining",           "esg":28, "carbon":680, "market_cap":55},
    {"ticker":"PSX",   "name":"Phillips 66",             "sector":"Energy",           "industry":"Refining",           "esg":33, "carbon":620, "market_cap":55},
    {"ticker":"OXY",   "name":"Occidental Petroleum",    "sector":"Energy",           "industry":"Oil & Gas",          "esg":36, "carbon":500, "market_cap":55},
    {"ticker":"HAL",   "name":"Halliburton",             "sector":"Energy",           "industry":"Oil Services",       "esg":34, "carbon":440, "market_cap":35},

    # ── UTILITIES — FOSSIL ───────────────────────────────────────────────────
    {"ticker":"DUK",   "name":"Duke Energy",             "sector":"Utilities",        "industry":"Electric Utility",   "esg":45, "carbon":380, "market_cap":80},
    {"ticker":"SO",    "name":"Southern Company",        "sector":"Utilities",        "industry":"Electric Utility",   "esg":43, "carbon":400, "market_cap":75},
    {"ticker":"D",     "name":"Dominion Energy",         "sector":"Utilities",        "industry":"Electric Utility",   "esg":48, "carbon":350, "market_cap":45},
    {"ticker":"AEP",   "name":"American Elec Power",     "sector":"Utilities",        "industry":"Electric Utility",   "esg":44, "carbon":420, "market_cap":45},
    {"ticker":"EXC",   "name":"Exelon",                  "sector":"Utilities",        "industry":"Nuclear/Electric",   "esg":62, "carbon":180, "market_cap":40},

    # ── SIN STOCKS / ESG LAGGARDS ─────────────────────────────────────────────
    {"ticker":"PM",    "name":"Philip Morris",           "sector":"Consumer Staples", "industry":"Tobacco",            "esg":18, "carbon":120, "market_cap":165},
    {"ticker":"MO",    "name":"Altria Group",            "sector":"Consumer Staples", "industry":"Tobacco",            "esg":15, "carbon":130, "market_cap":80},
    {"ticker":"BTI",   "name":"British American Tobacco","sector":"Consumer Staples", "industry":"Tobacco",            "esg":14, "carbon":140, "market_cap":75},
    {"ticker":"LMT",   "name":"Lockheed Martin",         "sector":"Industrials",      "industry":"Defense",            "esg":22, "carbon":200, "market_cap":120},
    {"ticker":"RTX",   "name":"RTX Corp",                "sector":"Industrials",      "industry":"Defense",            "esg":25, "carbon":190, "market_cap":145},
    {"ticker":"NOC",   "name":"Northrop Grumman",        "sector":"Industrials",      "industry":"Defense",            "esg":24, "carbon":195, "market_cap":75},
    {"ticker":"GD",    "name":"General Dynamics",        "sector":"Industrials",      "industry":"Defense",            "esg":23, "carbon":185, "market_cap":75},
    {"ticker":"WYNN",  "name":"Wynn Resorts",            "sector":"Consumer Disc.",   "industry":"Gambling",           "esg":20, "carbon":150, "market_cap":12},
    {"ticker":"MGM",   "name":"MGM Resorts",             "sector":"Consumer Disc.",   "industry":"Gambling",           "esg":22, "carbon":145, "market_cap":15},
    {"ticker":"CZR",   "name":"Caesars Entertainment",   "sector":"Consumer Disc.",   "industry":"Gambling",           "esg":19, "carbon":155, "market_cap":10},

    # ── CONSUMER DISCRETIONARY ───────────────────────────────────────────────
    {"ticker":"AMZN",  "name":"Amazon",                  "sector":"Consumer Disc.",   "industry":"E-Commerce",         "esg":66, "carbon":75,  "market_cap":1900},
    {"ticker":"HD",    "name":"Home Depot",              "sector":"Consumer Disc.",   "industry":"Home Improvement",   "esg":64, "carbon":68,  "market_cap":360},
    {"ticker":"MCD",   "name":"McDonald's",              "sector":"Consumer Disc.",   "industry":"Restaurants",        "esg":50, "carbon":160, "market_cap":220},
    {"ticker":"NKE",   "name":"Nike",                    "sector":"Consumer Disc.",   "industry":"Apparel",            "esg":72, "carbon":45,  "market_cap":150},
    {"ticker":"SBUX",  "name":"Starbucks",               "sector":"Consumer Disc.",   "industry":"Restaurants",        "esg":68, "carbon":55,  "market_cap":100},
    {"ticker":"TGT",   "name":"Target",                  "sector":"Consumer Disc.",   "industry":"Retail",             "esg":67, "carbon":62,  "market_cap":65},
    {"ticker":"LOW",   "name":"Lowe's",                  "sector":"Consumer Disc.",   "industry":"Home Improvement",   "esg":60, "carbon":70,  "market_cap":150},
    {"ticker":"F",     "name":"Ford Motor",              "sector":"Consumer Disc.",   "industry":"Autos",              "esg":48, "carbon":180, "market_cap":55},
    {"ticker":"GM",    "name":"General Motors",          "sector":"Consumer Disc.",   "industry":"Autos",              "esg":46, "carbon":200, "market_cap":55},

    # ── COMMUNICATION SERVICES ───────────────────────────────────────────────
    {"ticker":"META",  "name":"Meta Platforms",          "sector":"Comm. Services",   "industry":"Social Media",       "esg":58, "carbon":35,  "market_cap":1200},
    {"ticker":"NFLX",  "name":"Netflix",                 "sector":"Comm. Services",   "industry":"Streaming",          "esg":62, "carbon":22,  "market_cap":260},
    {"ticker":"DIS",   "name":"Walt Disney",             "sector":"Comm. Services",   "industry":"Entertainment",      "esg":70, "carbon":42,  "market_cap":200},
    {"ticker":"CMCSA", "name":"Comcast",                 "sector":"Comm. Services",   "industry":"Telecom",            "esg":55, "carbon":55,  "market_cap":170},
    {"ticker":"T",     "name":"AT&T",                    "sector":"Comm. Services",   "industry":"Telecom",            "esg":52, "carbon":65,  "market_cap":130},
    {"ticker":"VZ",    "name":"Verizon",                 "sector":"Comm. Services",   "industry":"Telecom",            "esg":56, "carbon":60,  "market_cap":170},
    {"ticker":"TMUS",  "name":"T-Mobile US",             "sector":"Comm. Services",   "industry":"Telecom",            "esg":60, "carbon":48,  "market_cap":220},

    # ── ADDITIONAL TECH ──────────────────────────────────────────────────────
    {"ticker":"NVDA",  "name":"Nvidia",                  "sector":"Technology",       "industry":"Semiconductors",     "esg":68, "carbon":20,  "market_cap":2200},
    {"ticker":"AMD",   "name":"AMD",                     "sector":"Technology",       "industry":"Semiconductors",     "esg":70, "carbon":18,  "market_cap":250},
    {"ticker":"AVGO",  "name":"Broadcom",                "sector":"Technology",       "industry":"Semiconductors",     "esg":65, "carbon":22,  "market_cap":700},
    {"ticker":"ORCL",  "name":"Oracle",                  "sector":"Technology",       "industry":"Software",           "esg":72, "carbon":14,  "market_cap":380},
    {"ticker":"NOW",   "name":"ServiceNow",              "sector":"Technology",       "industry":"Software",           "esg":80, "carbon":10,  "market_cap":180},
    {"ticker":"SNOW",  "name":"Snowflake",               "sector":"Technology",       "industry":"Cloud",              "esg":74, "carbon":8,   "market_cap":60},
    {"ticker":"PANW",  "name":"Palo Alto Networks",      "sector":"Technology",       "industry":"Cybersecurity",      "esg":75, "carbon":8,   "market_cap":110},
    {"ticker":"SAP",   "name":"SAP SE",                  "sector":"Technology",       "industry":"Software",           "esg":85, "carbon":12,  "market_cap":230},
    {"ticker":"AES",   "name":"AES Corp",                "sector":"Utilities",        "industry":"Power",              "esg":70, "carbon":120, "market_cap":15},
]


def get_universe_df():
    """
    Return the universe as a clean DataFrame with quintile
    assignments and ESG grade labels.
    """
    df = pd.DataFrame(UNIVERSE).drop_duplicates(subset="ticker").reset_index(drop=True)

    # Assign ESG quintiles: Q1 = best ESG, Q5 = worst
    df["quintile_num"] = pd.qcut(
        df["esg"], q=5, labels=[5, 4, 3, 2, 1]
    ).astype(int)

    # MSCI-style letter grade
    def grade(s):
        if s >= 85: return "AAA"
        if s >= 75: return "AA"
        if s >= 65: return "A"
        if s >= 50: return "BBB"
        if s >= 35: return "BB"
        if s >= 20: return "B"
        return "CCC"

    df["esg_grade"] = df["esg"].apply(grade)
    return df


def fetch_live_prices(tickers, start, end):
    """
    Download adjusted close prices from Yahoo Finance.
    Drops tickers that fail to download cleanly.
    Returns a DataFrame with SP500 as the last column.
    """
    import yfinance as yf

    all_tickers = tickers + ["^GSPC"]
    print(f"  Downloading {len(all_tickers)} tickers from Yahoo Finance...")

    raw = yf.download(
        all_tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=True,
    )["Close"]

    raw = raw.rename(columns={"^GSPC": "SP500"})

    # Drop columns that are entirely NaN
    raw = raw.dropna(axis=1, how="all")

    # Forward-fill then drop any remaining NaN rows
    raw = raw.ffill().dropna()

    n_dropped = len(all_tickers) - len(raw.columns)
    if n_dropped > 0:
        missing = set(all_tickers) - set(raw.columns)
        missing = {t.replace("^GSPC","SP500") for t in missing}
        print(f"  Dropped {n_dropped} tickers with no data: {', '.join(sorted(missing))}")

    return raw
