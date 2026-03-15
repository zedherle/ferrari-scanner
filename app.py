"""
Scuderia Ferrari Mission Control Dashboard
==========================================
A high-fidelity F1 telemetry dashboard built with Streamlit, FastF1, and Plotly.
Includes mock data fallback for immediate demonstration.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import random
from datetime import datetime

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Scuderia Ferrari | Mission Control",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Attempt FastF1 Import ────────────────────────────────────────────────────
USE_MOCK = False
try:
    import fastf1
    import fastf1.plotting
    fastf1.Cache.enable_cache("./f1_cache")
    FASTF1_AVAILABLE = True
except Exception:
    FASTF1_AVAILABLE = False
    USE_MOCK = True

# ─── Global Constants ─────────────────────────────────────────────────────────
FERRARI_RED    = "#EF1A2D"
CARBON_GREY    = "#343F47"
SILVER         = "#C0C0C0"
GOLD           = "#FFD700"
DARK_BG        = "#0A0A0A"
SURFACE_BG     = "#111318"
CARD_BG        = "#181C23"
BORDER_SUBTLE  = "#2A2F3A"
TEXT_PRIMARY   = "#F0F0F0"
TEXT_SECONDARY = "#8A9BB0"
GREEN_DELTA    = "#39FF14"
ORANGE_WARN    = "#FF8C00"

DRIVER_INFO = {
    "HAM": {"name": "Lewis Hamilton",   "num": 44, "team": "Ferrari",   "nationality": "🇬🇧"},
    "LEC": {"name": "Charles Leclerc",  "num": 16, "team": "Ferrari",   "nationality": "🇲🇨"},
    "ANT": {"name": "Kimi Antonelli",   "num": 12, "team": "Mercedes",  "nationality": "🇮🇹"},
    "RUS": {"name": "George Russell",   "num": 63, "team": "Mercedes",  "nationality": "🇬🇧"},
    "VER": {"name": "Max Verstappen",   "num": 1,  "team": "Red Bull",  "nationality": "🇳🇱"},
    "NOR": {"name": "Lando Norris",     "num": 4,  "team": "McLaren",   "nationality": "🇬🇧"},
    "PIA": {"name": "Oscar Piastri",    "num": 81, "team": "McLaren",   "nationality": "🇦🇺"},
    "ALO": {"name": "Fernando Alonso",  "num": 14, "team": "Aston Martin", "nationality": "🇪🇸"},
    "SAI": {"name": "Carlos Sainz Jr.", "num": 55, "team": "Williams",  "nationality": "🇪🇸"},
    "TSU": {"name": "Yuki Tsunoda",     "num": 22, "team": "Red Bull",  "nationality": "🇯🇵"},
}

TEAM_COLORS = {
    "Ferrari":      FERRARI_RED,
    "Mercedes":     "#00D2BE",
    "Red Bull":     "#3671C6",
    "McLaren":      "#FF8000",
    "Aston Martin": "#358C75",
    "Williams":     "#64C4FF",
}

CONSTRUCTOR_STANDINGS = [
    {"pos": 1, "team": "Mercedes",     "pts": 98,  "color": "#00D2BE", "change": "+2"},
    {"pos": 2, "team": "Ferrari",      "pts": 67,  "color": FERRARI_RED, "change": "+18"},
    {"pos": 3, "team": "McLaren",      "pts": 18,  "color": "#FF8000", "change": "+4"},
    {"pos": 4, "team": "Red Bull",     "pts": 12,  "color": "#3671C6", "change": "0"},
    {"pos": 5, "team": "Aston Martin", "pts": 6,   "color": "#358C75", "change": "0"},
]

TOTAL_LAPS = 56
CIRCUIT    = "Shanghai International Circuit"
ROUND      = "Round 3 · Chinese Grand Prix"

# ─── Inject CSS ───────────────────────────────────────────────────────────────
def inject_css(tifosi_mode: bool):
    glow = f"0 0 12px {FERRARI_RED}80, 0 0 30px {FERRARI_RED}40" if tifosi_mode else "none"
    pulse_anim = """
    @keyframes pulse-glow {
        0%   { box-shadow: 0 0 8px #EF1A2D60, 0 0 20px #EF1A2D30; }
        50%  { box-shadow: 0 0 22px #EF1A2D90, 0 0 50px #EF1A2D50; }
        100% { box-shadow: 0 0 8px #EF1A2D60, 0 0 20px #EF1A2D30; }
    }
    @keyframes scanline {
        0%   { transform: translateY(-100%); }
        100% { transform: translateY(100vh); }
    }
    @keyframes counter-tick {
        0%   { transform: translateY(0); }
        50%  { transform: translateY(-3px); }
        100% { transform: translateY(0); }
    }
    """ if tifosi_mode else ""

    border_rule = "animation: pulse-glow 2s ease-in-out infinite;" if tifosi_mode else f"box-shadow: {glow};"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');

    {pulse_anim}

    /* ── Root reset ── */
    html, body, [class*="css"] {{
        background-color: {DARK_BG} !important;
        color: {TEXT_PRIMARY} !important;
        font-family: 'Rajdhani', sans-serif;
    }}
    .stApp {{ background-color: {DARK_BG} !important; }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0E1117 0%, #0A0D12 100%) !important;
        border-right: 1px solid {FERRARI_RED}50 !important;
        {border_rule}
    }}
    [data-testid="stSidebar"] * {{ color: {TEXT_PRIMARY} !important; }}

    /* ── Top area ── */
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* ── Metric widgets ── */
    [data-testid="metric-container"] {{
        background: {CARD_BG} !important;
        border: 1px solid {BORDER_SUBTLE} !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }}
    [data-testid="stMetricValue"] {{
        font-family: 'Orbitron', monospace !important;
        font-size: 1.4rem !important;
        color: {FERRARI_RED} !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {TEXT_SECONDARY} !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background: linear-gradient(135deg, {FERRARI_RED} 0%, #B01020 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        font-family: 'Orbitron', monospace !important;
        font-size: 0.7rem !important;
        letter-spacing: 0.12em !important;
        font-weight: 700 !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px {FERRARI_RED}60 !important;
    }}

    /* ── Sliders ── */
    [data-testid="stSlider"] > div > div > div {{
        background: {FERRARI_RED} !important;
    }}

    /* ── Cards ── */
    .mc-card {{
        background: {CARD_BG};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
    }}
    .mc-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, {FERRARI_RED}, transparent);
    }}
    .mc-card-ferrari::before {{
        background: linear-gradient(90deg, {FERRARI_RED}, #FF6B6B, transparent);
    }}

    .driver-card {{
        background: linear-gradient(135deg, {CARD_BG} 0%, #1A1E28 100%);
        border: 1px solid {BORDER_SUBTLE};
        border-left: 3px solid {FERRARI_RED};
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
    }}
    .driver-name {{
        font-family: 'Orbitron', monospace;
        font-size: 0.85rem;
        font-weight: 700;
        color: {TEXT_PRIMARY};
        letter-spacing: 0.05em;
    }}
    .driver-number {{
        font-family: 'Orbitron', monospace;
        font-size: 1.6rem;
        font-weight: 900;
        color: {FERRARI_RED};
        opacity: 0.3;
        float: right;
        line-height: 1;
    }}
    .telemetry-row {{
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
        gap: 6px;
    }}
    .telem-box {{
        background: {DARK_BG};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 5px;
        padding: 6px 8px;
        text-align: center;
        flex: 1;
    }}
    .telem-label {{
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.55rem;
        color: {TEXT_SECONDARY};
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}
    .telem-value {{
        font-family: 'Orbitron', monospace;
        font-size: 0.9rem;
        font-weight: 700;
        color: {TEXT_PRIMARY};
    }}
    .telem-value.speed {{ color: #64C4FF; }}
    .telem-value.throttle {{ color: {GREEN_DELTA}; }}
    .telem-value.brake {{ color: {FERRARI_RED}; }}
    .telem-value.gear {{ color: {GOLD}; }}

    /* ── Tyre badge ── */
    .tyre-badge {{
        display: inline-block;
        background: #F0F0F0;
        color: #111;
        border-radius: 50%;
        width: 22px; height: 22px;
        text-align: center;
        line-height: 22px;
        font-family: 'Orbitron', monospace;
        font-size: 0.65rem;
        font-weight: 900;
        margin-right: 6px;
    }}
    .tyre-badge.medium {{ background: #FFD700; }}
    .tyre-badge.soft {{ background: {FERRARI_RED}; color: white; }}
    .tyre-badge.hard {{ background: #E0E0E0; }}

    /* ── Section headers ── */
    .section-header {{
        font-family: 'Orbitron', monospace;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: {FERRARI_RED};
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 1px solid {FERRARI_RED}30;
    }}

    /* ── Timing tower rows ── */
    .timing-row {{
        display: flex;
        align-items: center;
        padding: 8px 12px;
        margin-bottom: 4px;
        border-radius: 6px;
        background: {CARD_BG};
        border: 1px solid {BORDER_SUBTLE};
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.82rem;
        transition: all 0.2s;
    }}
    .timing-row.ferrari {{
        border-left: 3px solid {FERRARI_RED};
        background: linear-gradient(90deg, {FERRARI_RED}15 0%, {CARD_BG} 40%);
    }}
    .timing-row.p1 {{
        border-left: 3px solid {GOLD};
    }}

    /* ── Race progress bar ── */
    .progress-container {{
        background: {CARD_BG};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 6px;
        padding: 10px 16px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 14px;
    }}
    .lap-label {{
        font-family: 'Orbitron', monospace;
        font-size: 0.7rem;
        color: {TEXT_SECONDARY};
        white-space: nowrap;
    }}
    .lap-number {{
        font-family: 'Orbitron', monospace;
        font-size: 1.1rem;
        font-weight: 700;
        color: {FERRARI_RED};
        white-space: nowrap;
    }}
    .progress-bar-track {{
        flex: 1;
        height: 6px;
        background: {BORDER_SUBTLE};
        border-radius: 3px;
        overflow: hidden;
    }}
    .progress-bar-fill {{
        height: 100%;
        background: linear-gradient(90deg, {FERRARI_RED}, #FF6060);
        border-radius: 3px;
        transition: width 0.4s ease;
    }}

    /* ── Championship badge ── */
    .champ-badge {{
        background: {CARD_BG};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .champ-pos {{
        font-family: 'Orbitron', monospace;
        font-size: 1.1rem;
        font-weight: 900;
        color: {TEXT_SECONDARY};
        width: 24px;
        text-align: center;
    }}
    .champ-pos.p1 {{ color: {GOLD}; }}
    .champ-pos.p2 {{ color: #C0C0C0; }}
    .champ-pos.p3 {{ color: #CD7F32; }}
    .champ-bar-track {{
        flex: 1;
        height: 5px;
        background: {BORDER_SUBTLE};
        border-radius: 3px;
        overflow: hidden;
    }}

    /* ── Status pill ── */
    .status-pill {{
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.1em;
    }}
    .status-live {{ background: {FERRARI_RED}25; color: {FERRARI_RED}; border: 1px solid {FERRARI_RED}50; }}
    .status-mock {{ background: #FF8C0025; color: {ORANGE_WARN}; border: 1px solid {ORANGE_WARN}50; }}

    /* ── Tifosi overlay scan effect ── */
    {''.join(['''
    .tifosi-active {
        position: relative;
    }
    .tifosi-active::after {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, transparent, ''' + FERRARI_RED + '''80, transparent);
        animation: scanline 4s linear infinite;
        pointer-events: none;
        z-index: 9999;
    }
    ''' if tifosi_mode else ''])}

    /* ── Plotly overrides ── */
    .js-plotly-plot .plotly, .js-plotly-plot .plotly div {{
        font-family: 'Rajdhani', sans-serif !important;
    }}

    /* ── Hide default streamlit chrome ── */
    #MainMenu, footer, .viewerBadge_container__1QSob {{ display: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# ─── Mock Data Generator ──────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def generate_mock_telemetry(driver_id: str, seed: int = 42):
    """Generate realistic mock telemetry for the Shanghai circuit (~5.4 km)."""
    rng = np.random.default_rng(seed)
    n = 800  # data points per lap

    dist = np.linspace(0, 5451, n)

    # Shanghai-ish speed profile (simplified sector model)
    base_speed = np.zeros(n)
    # Sector 1: Long straight + hairpin
    base_speed[:100]  = np.linspace(180, 320, 100)
    base_speed[100:130] = np.linspace(320, 80, 30)
    base_speed[130:180] = np.linspace(80, 200, 50)
    # Sector 2: Twisty section
    base_speed[180:220] = np.linspace(200, 140, 40)
    base_speed[220:260] = np.linspace(140, 180, 40)
    base_speed[260:300] = np.linspace(180, 120, 40)
    base_speed[300:340] = np.linspace(120, 160, 40)
    # Sector 3: Back straight + chicane
    base_speed[340:460] = np.linspace(160, 330, 120)
    base_speed[460:490] = np.linspace(330, 100, 30)
    base_speed[490:540] = np.linspace(100, 250, 50)
    base_speed[540:600] = np.linspace(250, 280, 60)
    # Final sector
    base_speed[600:700] = np.linspace(280, 320, 100)
    base_speed[700:730] = np.linspace(320, 90, 30)
    base_speed[730:]    = np.linspace(90, 180, n - 730)

    # Add driver character offset
    offsets = {"HAM": 3, "LEC": -2, "ANT": -5, "RUS": 1, "VER": 4}
    speed = base_speed + offsets.get(driver_id, 0) + rng.normal(0, 4, n)
    speed = np.clip(speed, 40, 340)

    # Throttle: high where speed is increasing
    throttle = np.gradient(speed)
    throttle = np.clip((throttle + 10) * 8, 0, 100)

    # Brake: high where speed drops sharply
    brake_signal = -np.gradient(speed)
    brake = np.clip(brake_signal * 10, 0, 100)

    # Gear (1-8)
    gear = np.clip(np.round(speed / 42).astype(int), 1, 8)

    return pd.DataFrame({
        "Distance": dist,
        "Speed":    speed,
        "Throttle": throttle,
        "Brake":    brake,
        "nGear":    gear,
    })

@st.cache_data(ttl=60)
def generate_mock_timing(lap: int, tifosi_pin: bool = False):
    """Generate mock timing tower data."""
    base_data = [
        {"pos": 1,  "code": "ANT", "team": "Mercedes",     "lap_time": "1:35.412", "interval": "LEADER",   "pts_gain": "+25", "tyre": "H", "stint": 21},
        {"pos": 2,  "code": "RUS", "team": "Mercedes",     "lap_time": "1:35.589", "interval": "+1.827s",  "pts_gain": "+18", "tyre": "H", "stint": 21},
        {"pos": 3,  "code": "HAM", "team": "Ferrari",      "lap_time": "1:35.701", "interval": "+3.214s",  "pts_gain": "+15", "tyre": "H", "stint": 18},
        {"pos": 4,  "code": "LEC", "team": "Ferrari",      "lap_time": "1:35.834", "interval": "+5.102s",  "pts_gain": "+12", "tyre": "H", "stint": 18},
        {"pos": 5,  "code": "NOR", "team": "McLaren",      "lap_time": "1:36.012", "interval": "+8.441s",  "pts_gain": "+10", "tyre": "M", "stint": 14},
        {"pos": 6,  "code": "PIA", "team": "McLaren",      "lap_time": "1:36.199", "interval": "+11.20s",  "pts_gain": "+8",  "tyre": "M", "stint": 14},
        {"pos": 7,  "code": "VER", "team": "Red Bull",     "lap_time": "1:36.544", "interval": "+18.77s",  "pts_gain": "+6",  "tyre": "H", "stint": 22},
        {"pos": 8,  "code": "TSU", "team": "Red Bull",     "lap_time": "1:36.788", "interval": "+23.41s",  "pts_gain": "+4",  "tyre": "H", "stint": 22},
        {"pos": 9,  "code": "ALO", "team": "Aston Martin", "lap_time": "1:37.021", "interval": "+31.88s",  "pts_gain": "+2",  "tyre": "M", "stint": 10},
        {"pos": 10, "code": "SAI", "team": "Williams",     "lap_time": "1:37.244", "interval": "+38.12s",  "pts_gain": "+1",  "tyre": "S", "stint": 6},
    ]
    if tifosi_pin:
        ferrari = [r for r in base_data if r["team"] == "Ferrari"]
        others  = [r for r in base_data if r["team"] != "Ferrari"]
        for i, r in enumerate(ferrari): r["pos"] = i + 1
        for i, r in enumerate(others):  r["pos"] = len(ferrari) + i + 1
        base_data = ferrari + others
    return base_data

@st.cache_data(ttl=60)
def generate_driver_standings(tifosi_pin: bool = False):
    base = [
        {"pos": 1, "code": "ANT", "name": "Antonelli",  "team": "Mercedes",     "pts": 50, "flag": "🇮🇹"},
        {"pos": 2, "code": "RUS", "name": "Russell",    "team": "Mercedes",     "pts": 48, "flag": "🇬🇧"},
        {"pos": 3, "code": "HAM", "name": "Hamilton",   "team": "Ferrari",      "pts": 37, "flag": "🇬🇧"},
        {"pos": 4, "code": "LEC", "name": "Leclerc",    "team": "Ferrari",      "pts": 30, "flag": "🇲🇨"},
        {"pos": 5, "code": "NOR", "name": "Norris",     "team": "McLaren",      "pts": 12, "flag": "🇬🇧"},
        {"pos": 6, "code": "PIA", "name": "Piastri",    "team": "McLaren",      "pts": 6,  "flag": "🇦🇺"},
        {"pos": 7, "code": "VER", "name": "Verstappen", "team": "Red Bull",     "pts": 6,  "flag": "🇳🇱"},
        {"pos": 8, "code": "TSU", "name": "Tsunoda",    "team": "Red Bull",     "pts": 4,  "flag": "🇯🇵"},
        {"pos": 9, "code": "ALO", "name": "Alonso",     "team": "Aston Martin", "pts": 4,  "flag": "🇪🇸"},
        {"pos":10, "code": "SAI", "name": "Sainz",      "team": "Williams",     "pts": 2,  "flag": "🇪🇸"},
    ]
    if tifosi_pin:
        ferrari = [r for r in base if r["team"] == "Ferrari"]
        others  = [r for r in base if r["team"] != "Ferrari"]
        for i, r in enumerate(ferrari): r["pos"] = i + 1
        for i, r in enumerate(others):  r["pos"] = len(ferrari) + i + 1
        base = ferrari + others
    return base

# ─── FastF1 Real Data Loader ──────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_f1_session():
    try:
        session = fastf1.get_session(2026, "Shanghai", "R")
        session.load(telemetry=True, laps=True)
        return session, None
    except Exception as e:
        return None, str(e)

def get_real_telemetry(session, driver: str):
    try:
        lap = session.laps.pick_driver(driver).pick_fastest()
        tel = lap.get_telemetry().add_distance()
        return tel[["Distance", "Speed", "Throttle", "Brake", "nGear"]].dropna()
    except:
        return None

# ─── Plotly Chart: Battle Trace ───────────────────────────────────────────────
def render_battle_trace(ham_tel, ant_tel, lap_num):
    fig = go.Figure()

    # HAM trace
    fig.add_trace(go.Scatter(
        x=ham_tel["Distance"],
        y=ham_tel["Speed"],
        name="HAM · Hamilton",
        line=dict(color=FERRARI_RED, width=2.5),
        fill="tozeroy",
        fillcolor=f"{FERRARI_RED}12",
        hovertemplate="<b>HAM</b><br>Dist: %{x:.0f}m<br>Speed: %{y:.0f} km/h<extra></extra>",
    ))

    # ANT trace
    fig.add_trace(go.Scatter(
        x=ant_tel["Distance"],
        y=ant_tel["Speed"],
        name="ANT · Antonelli",
        line=dict(color=SILVER, width=2, dash="dot"),
        hovertemplate="<b>ANT</b><br>Dist: %{x:.0f}m<br>Speed: %{y:.0f} km/h<extra></extra>",
    ))

    # Speed delta shading (HAM advantage zones)
    common_dist = np.linspace(0, 5451, 300)
    ham_interp = np.interp(common_dist, ham_tel["Distance"], ham_tel["Speed"])
    ant_interp = np.interp(common_dist, ant_tel["Distance"], ant_tel["Speed"])
    delta = ham_interp - ant_interp

    # Highlight zones where HAM leads
    fig.add_trace(go.Scatter(
        x=common_dist, y=ham_interp,
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=common_dist, y=ant_interp,
        line=dict(width=0),
        fill="tonexty",
        fillcolor=f"{FERRARI_RED}20",
        showlegend=False, hoverinfo="skip",
        name="HAM Delta",
    ))

    # Corner labels (Shanghai approximate)
    corners = {
        "T1": 200, "T2": 600, "T6": 2000, "T11": 3100, "T13": 3900, "T16": 4900
    }
    for corner, pos in corners.items():
        fig.add_vline(
            x=pos, line_color=BORDER_SUBTLE,
            line_width=1, line_dash="dot",
            annotation_text=corner,
            annotation_font=dict(color=TEXT_SECONDARY, size=9, family="Share Tech Mono"),
            annotation_position="top",
        )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=f"{DARK_BG}",
        font=dict(family="Rajdhani", color=TEXT_SECONDARY),
        title=dict(
            text=f"⚡ Battle Trace · Lap {lap_num} · HAM vs ANT",
            font=dict(family="Orbitron", size=13, color=TEXT_PRIMARY),
            x=0.01,
        ),
        xaxis=dict(
            title="Track Position (m)",
            gridcolor=BORDER_SUBTLE, gridwidth=1,
            zeroline=False, color=TEXT_SECONDARY,
            titlefont=dict(family="Share Tech Mono", size=10),
        ),
        yaxis=dict(
            title="Speed (km/h)",
            gridcolor=BORDER_SUBTLE, gridwidth=1,
            zeroline=False, color=TEXT_SECONDARY,
            titlefont=dict(family="Share Tech Mono", size=10),
        ),
        legend=dict(
            font=dict(family="Share Tech Mono", size=10, color=TEXT_SECONDARY),
            bgcolor="rgba(0,0,0,0)",
            bordercolor=BORDER_SUBTLE,
            borderwidth=1,
            x=0.01, y=0.99,
        ),
        margin=dict(l=50, r=20, t=50, b=50),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=CARD_BG,
            bordercolor=FERRARI_RED,
            font=dict(family="Share Tech Mono", size=11),
        ),
    )
    return fig

# ─── Plotly Chart: Constructor Standings Bar ──────────────────────────────────
def render_constructor_chart():
    teams = [c["team"] for c in CONSTRUCTOR_STANDINGS]
    pts   = [c["pts"]  for c in CONSTRUCTOR_STANDINGS]
    colors = [c["color"] for c in CONSTRUCTOR_STANDINGS]

    fig = go.Figure(go.Bar(
        x=pts, y=teams,
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(color=BORDER_SUBTLE, width=1),
        ),
        text=[f"  {p} pts" for p in pts],
        textposition="outside",
        textfont=dict(family="Orbitron", size=10, color=TEXT_PRIMARY),
        hovertemplate="<b>%{y}</b><br>Points: %{x}<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Rajdhani", color=TEXT_SECONDARY),
        title=dict(
            text="🏆 Constructor Championship · 2026",
            font=dict(family="Orbitron", size=12, color=TEXT_PRIMARY),
            x=0.01,
        ),
        xaxis=dict(
            gridcolor=BORDER_SUBTLE, color=TEXT_SECONDARY,
            range=[0, 120],
        ),
        yaxis=dict(
            autorange="reversed", color=TEXT_SECONDARY,
            tickfont=dict(family="Rajdhani", size=12),
        ),
        margin=dict(l=20, r=80, t=50, b=30),
        height=220,
        showlegend=False,
    )
    return fig

# ─── Plotly Chart: Throttle/Brake comparison ─────────────────────────────────
def render_pedal_trace(ham_tel, ant_tel):
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.5, 0.5],
        vertical_spacing=0.04,
    )
    dist_common = np.linspace(0, 5451, 400)

    for driver, tel, color, row_t, row_b in [
        ("HAM", ham_tel, FERRARI_RED, 1, 2),
        ("ANT", ant_tel, SILVER,     1, 2),
    ]:
        t_interp = np.interp(dist_common, tel["Distance"], tel["Throttle"])
        b_interp = np.interp(dist_common, tel["Distance"], tel["Brake"])

        fig.add_trace(go.Scatter(
            x=dist_common, y=t_interp,
            name=f"{driver} Throttle",
            line=dict(color=color, width=1.5),
            fill="tozeroy",
            fillcolor=f"{color}18",
            legendgroup=driver,
            hovertemplate=f"<b>{driver}</b> Throttle: %{{y:.0f}}%<extra></extra>",
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=dist_common, y=b_interp,
            name=f"{driver} Brake",
            line=dict(color=color, width=1.5, dash="dot"),
            fill="tozeroy",
            fillcolor=f"{color}10",
            legendgroup=driver,
            showlegend=False,
            hovertemplate=f"<b>{driver}</b> Brake: %{{y:.0f}}%<extra></extra>",
        ), row=2, col=1)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Rajdhani", color=TEXT_SECONDARY),
        title=dict(
            text="🎮 Pedal Trace · Throttle & Brake",
            font=dict(family="Orbitron", size=12, color=TEXT_PRIMARY),
            x=0.01,
        ),
        height=280,
        margin=dict(l=50, r=20, t=50, b=30),
        hovermode="x unified",
        legend=dict(
            font=dict(family="Share Tech Mono", size=9),
            bgcolor="rgba(0,0,0,0)",
            orientation="h", y=1.08, x=0,
        ),
    )
    for row in [1, 2]:
        fig.update_xaxes(gridcolor=BORDER_SUBTLE, zeroline=False, row=row, col=1)
        fig.update_yaxes(gridcolor=BORDER_SUBTLE, zeroline=False, row=row, col=1,
                         range=[0, 105], tickfont=dict(size=9))

    fig.update_xaxes(title_text="Distance (m)", row=2, col=1,
                     titlefont=dict(family="Share Tech Mono", size=10))
    fig.update_yaxes(title_text="Throttle %", row=1, col=1)
    fig.update_yaxes(title_text="Brake %",    row=2, col=1)
    return fig

# ─── Render Sidebar ───────────────────────────────────────────────────────────
def render_sidebar(tifosi_mode: bool, lap: int):
    with st.sidebar:
        # Logo / Title
        st.markdown(f"""
        <div style="text-align:center; padding: 16px 0 8px;">
            <div style="font-family:'Orbitron',monospace; font-size:0.65rem; 
                        letter-spacing:0.3em; color:{TEXT_SECONDARY}; 
                        text-transform:uppercase; margin-bottom:4px;">SCUDERIA</div>
            <div style="font-family:'Orbitron',monospace; font-size:1.4rem; 
                        font-weight:900; color:{FERRARI_RED}; letter-spacing:0.05em;">
                FERRARI
            </div>
            <div style="font-family:'Share Tech Mono',monospace; font-size:0.6rem; 
                        color:{TEXT_SECONDARY}; letter-spacing:0.2em; margin-top:2px;">
                MISSION CONTROL
            </div>
            <div style="margin-top:8px; width:40px; height:2px; 
                        background:{FERRARI_RED}; margin-left:auto; margin-right:auto;"></div>
        </div>
        """, unsafe_allow_html=True)

        # Status badge
        status_class = "status-mock" if USE_MOCK else "status-live"
        status_text  = "◉ MOCK MODE" if USE_MOCK else "◉ LIVE"
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:14px;">
            <span class="status-pill {status_class}">{status_text}</span>
        </div>
        """, unsafe_allow_html=True)

        # Tifosi Toggle
        st.markdown(f'<div class="section-header">⚙ Controls</div>', unsafe_allow_html=True)
        tifosi = st.toggle("🔴 TIFOSI MODE", value=tifosi_mode, key="tifosi_toggle")

        st.divider()
        st.markdown(f'<div class="section-header">🏎 Ferrari Hub</div>', unsafe_allow_html=True)

        # Live telemetry values (randomized slightly to simulate live feed)
        seed = int(time.time()) // 3  # update every 3s
        rng = random.Random(seed)

        drivers_data = {
            "HAM": {
                "speed":    rng.randint(285, 318),
                "throttle": rng.randint(88, 100),
                "brake":    rng.randint(0, 5),
                "gear":     rng.randint(7, 8),
                "tyre_lap": 18,
                "compound": "H",
                "pos":      3,
            },
            "LEC": {
                "speed":    rng.randint(282, 316),
                "throttle": rng.randint(85, 99),
                "brake":    rng.randint(0, 8),
                "gear":     rng.randint(7, 8),
                "tyre_lap": 18,
                "compound": "H",
                "pos":      4,
            },
        }

        for code, data in drivers_data.items():
            info = DRIVER_INFO[code]
            tyre_pct = min(100, (data["tyre_lap"] / 30) * 100)
            tyre_color = (
                FERRARI_RED    if tyre_pct > 70 else
                ORANGE_WARN    if tyre_pct > 40 else
                GREEN_DELTA
            )

            st.markdown(f"""
            <div class="driver-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.6rem; 
                                    color:{TEXT_SECONDARY}; letter-spacing:0.1em;">
                            {info['nationality']} P{data['pos']}
                        </div>
                        <div class="driver-name">{code}</div>
                        <div style="font-family:'Rajdhani',sans-serif; font-size:0.75rem; 
                                    color:{TEXT_SECONDARY};">
                            {info['name'].split()[1]}
                        </div>
                    </div>
                    <div class="driver-number">#{info['num']}</div>
                </div>
                <div class="telemetry-row">
                    <div class="telem-box">
                        <div class="telem-label">SPD</div>
                        <div class="telem-value speed">{data['speed']}</div>
                    </div>
                    <div class="telem-box">
                        <div class="telem-label">THR</div>
                        <div class="telem-value throttle">{data['throttle']}%</div>
                    </div>
                    <div class="telem-box">
                        <div class="telem-label">BRK</div>
                        <div class="telem-value brake">{data['brake']}%</div>
                    </div>
                    <div class="telem-box">
                        <div class="telem-label">GER</div>
                        <div class="telem-value gear">{data['gear']}</div>
                    </div>
                </div>
                <div style="margin-top:10px; display:flex; align-items:center; gap:8px;">
                    <span class="tyre-badge hard">{data['compound']}</span>
                    <div style="flex:1;">
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.6rem; 
                                    color:{TEXT_SECONDARY}; margin-bottom:3px;">
                            TYRE LIFE · LAP {data['tyre_lap']}/~30
                        </div>
                        <div style="background:{BORDER_SUBTLE}; border-radius:3px; height:4px; overflow:hidden;">
                            <div style="width:{tyre_pct:.0f}%; height:100%; 
                                        background:{tyre_color}; border-radius:3px;
                                        transition: width 0.5s ease;"></div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Session info
        st.markdown(f"""
        <div style="font-family:'Share Tech Mono',monospace; font-size:0.65rem; 
                    color:{TEXT_SECONDARY}; line-height:2;">
            <div>📍 {CIRCUIT}</div>
            <div>🗓 {ROUND}</div>
            <div>🌡 28°C Track · 22°C Air</div>
            <div>💨 NE 12 km/h</div>
        </div>
        """, unsafe_allow_html=True)

        return tifosi

# ─── Main Dashboard ───────────────────────────────────────────────────────────
def main():
    # Initialize session state
    if "tifosi_mode" not in st.session_state:
        st.session_state.tifosi_mode = False

    inject_css(st.session_state.tifosi_mode)

    # ── Sidebar ──────────────────────────────────────────────────────────────
    tifosi = render_sidebar(st.session_state.tifosi_mode, 51)
    st.session_state.tifosi_mode = tifosi

    # ── Top Bar ───────────────────────────────────────────────────────────────
    top_col1, top_col2, top_col3 = st.columns([2, 5, 1])

    with top_col1:
        st.markdown(f"""
        <div style="padding-top:8px;">
            <div style="font-family:'Orbitron',monospace; font-size:0.6rem; 
                        color:{TEXT_SECONDARY}; letter-spacing:0.2em;">2026 FORMULA 1</div>
            <div style="font-family:'Orbitron',monospace; font-size:1.1rem; 
                        font-weight:900; color:{TEXT_PRIMARY};">CHINESE GRAND PRIX</div>
            {'<div style="font-family:Orbitron,monospace; font-size:0.6rem; color:' + FERRARI_RED + '; letter-spacing:0.15em; animation:pulse-glow 1s infinite;">🔴 TIFOSI MODE ACTIVE</div>' if tifosi else ''}
        </div>
        """, unsafe_allow_html=True)

    with top_col2:
        lap = st.slider(
            "Current Lap",
            min_value=1, max_value=TOTAL_LAPS,
            value=51,
            format="Lap %d",
            label_visibility="collapsed",
        )
        pct = (lap / TOTAL_LAPS) * 100
        st.markdown(f"""
        <div class="progress-container">
            <div class="lap-label">LAP</div>
            <div class="lap-number">{lap}</div>
            <div class="progress-bar-track">
                <div class="progress-bar-fill" style="width:{pct:.1f}%"></div>
            </div>
            <div class="lap-label">/ {TOTAL_LAPS}</div>
            <div style="font-family:'Share Tech Mono',monospace; font-size:0.65rem; 
                        color:{TEXT_SECONDARY};">
                {pct:.0f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with top_col3:
        st.markdown(f"""
        <div style="text-align:right; padding-top:8px;">
            <div style="font-family:'Share Tech Mono',monospace; font-size:0.65rem; 
                        color:{TEXT_SECONDARY};">{datetime.now().strftime('%H:%M:%S')} CST</div>
            <div style="font-family:'Orbitron',monospace; font-size:0.75rem; 
                        color:{FERRARI_RED};">{'⚡ MOCK' if USE_MOCK else '◉ LIVE'}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#2A2F3A; margin: 4px 0 16px;'>", unsafe_allow_html=True)

    # ── Load telemetry ────────────────────────────────────────────────────────
    session_data = None
    if FASTF1_AVAILABLE and not USE_MOCK:
        with st.spinner("Loading FastF1 session data..."):
            session_data, err = load_f1_session()
            if err:
                st.warning(f"FastF1 error: {err}. Using mock data.")

    ham_tel = ant_tel = None
    if session_data:
        ham_tel = get_real_telemetry(session_data, "HAM")
        ant_tel = get_real_telemetry(session_data, "ANT")

    if ham_tel is None:
        ham_tel = generate_mock_telemetry("HAM", seed=44)
    if ant_tel is None:
        ant_tel = generate_mock_telemetry("ANT", seed=12)

    # ── Main Grid ─────────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1.15, 2], gap="medium")

    # ── Module A: Timing Tower ────────────────────────────────────────────────
    with col_left:
        st.markdown(f'<div class="section-header">⏱ Timing Tower · Lap {lap}/{TOTAL_LAPS}</div>',
                    unsafe_allow_html=True)

        timing = generate_mock_timing(lap, tifosi_pin=tifosi)

        # Column headers
        st.markdown(f"""
        <div style="display:flex; font-family:'Share Tech Mono',monospace; 
                    font-size:0.6rem; color:{TEXT_SECONDARY}; 
                    padding: 0 12px 4px; letter-spacing:0.08em;">
            <span style="width:28px;">POS</span>
            <span style="width:40px;">DRV</span>
            <span style="flex:1;">INTERVAL</span>
            <span style="width:45px; text-align:right;">PTS</span>
            <span style="width:35px; text-align:center;">TYR</span>
        </div>
        """, unsafe_allow_html=True)

        for row in timing:
            is_ferrari = row["team"] == "Ferrari"
            is_p1      = row["pos"] == 1
            row_class  = "ferrari" if is_ferrari else ("p1" if is_p1 else "")
            pos_color  = GOLD if is_p1 else (FERRARI_RED if is_ferrari else TEXT_SECONDARY)
            name_color = FERRARI_RED if is_ferrari else TEXT_PRIMARY
            team_color = TEAM_COLORS.get(row["team"], TEXT_SECONDARY)

            tyre_colors = {"H": "#E0E0E0", "M": "#FFD700", "S": FERRARI_RED}
            tyre_bg     = tyre_colors.get(row["tyre"], TEXT_SECONDARY)
            tyre_txt    = "#111" if row["tyre"] in ("H", "M") else "white"

            st.markdown(f"""
            <div class="timing-row {row_class}">
                <span style="width:28px; font-family:'Orbitron',monospace; 
                             font-size:0.75rem; color:{pos_color}; font-weight:700;">
                    {row['pos']}
                </span>
                <span style="width:40px; font-weight:700; 
                             color:{name_color}; font-size:0.85rem;">
                    {row['code']}
                </span>
                <span style="flex:1; color:{TEXT_SECONDARY}; font-size:0.75rem;">
                    {row['interval']}
                </span>
                <span style="width:45px; text-align:right; 
                             color:{GREEN_DELTA}; font-size:0.75rem; font-weight:700;">
                    {row['pts_gain']}
                </span>
                <span style="width:35px; text-align:center;">
                    <span style="background:{tyre_bg}; color:{tyre_txt}; 
                                 border-radius:50%; display:inline-block;
                                 width:20px; height:20px; line-height:20px; 
                                 font-family:'Orbitron',monospace; font-size:0.6rem;
                                 font-weight:900;">
                        {row['tyre']}
                    </span>
                </span>
            </div>
            """, unsafe_allow_html=True)

        # Championship gain this race
        st.markdown(f"""
        <div style="margin-top:14px; padding:10px 12px; background:{CARD_BG}; 
                    border:1px solid {FERRARI_RED}30; border-radius:7px;">
            <div style="font-family:'Orbitron',monospace; font-size:0.6rem; 
                        color:{FERRARI_RED}; letter-spacing:0.15em; margin-bottom:8px;">
                △ CHAMPIONSHIP GAIN (THIS RACE)
            </div>
            <div style="display:flex; justify-content:space-between; 
                        font-family:'Share Tech Mono',monospace; font-size:0.75rem;">
                <span>Ferrari vs Mercedes</span>
                <span style="color:{FERRARI_RED}; font-weight:700;">+27 pts gap cut</span>
            </div>
            <div style="margin-top:4px; font-family:'Share Tech Mono',monospace; 
                        font-size:0.65rem; color:{TEXT_SECONDARY};">
                PRE: −31 pts → POST: −4 pts
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Module B: Charts ──────────────────────────────────────────────────────
    with col_right:
        tab1, tab2, tab3 = st.tabs(["⚡ Battle Trace", "🎮 Pedal Trace", "🏆 Championship"])

        with tab1:
            st.plotly_chart(
                render_battle_trace(ham_tel, ant_tel, lap),
                use_container_width=True,
                config={"displayModeBar": False},
            )

            # Speed delta summary
            dist_c = np.linspace(0, 5451, 400)
            ham_s = np.interp(dist_c, ham_tel["Distance"], ham_tel["Speed"])
            ant_s = np.interp(dist_c, ant_tel["Distance"], ant_tel["Speed"])
            delta_avg = ham_s.mean() - ant_s.mean()
            delta_max = (ham_s - ant_s).max()
            delta_min = (ham_s - ant_s).min()

            d1, d2, d3, d4 = st.columns(4)
            with d1:
                st.metric("HAM Avg Speed", f"{ham_s.mean():.0f} km/h")
            with d2:
                st.metric("ANT Avg Speed", f"{ant_s.mean():.0f} km/h")
            with d3:
                color = "normal" if delta_avg >= 0 else "inverse"
                st.metric("HAM Delta", f"{delta_avg:+.1f} km/h")
            with d4:
                st.metric("Max HAM Adv", f"+{delta_max:.0f} km/h")

        with tab2:
            st.plotly_chart(
                render_pedal_trace(ham_tel, ant_tel),
                use_container_width=True,
                config={"displayModeBar": False},
            )

        with tab3:
            # Constructor chart
            st.plotly_chart(
                render_constructor_chart(),
                use_container_width=True,
                config={"displayModeBar": False},
            )

            st.markdown(f'<div class="section-header" style="margin-top:8px;">👤 Driver Standings · 2026</div>',
                        unsafe_allow_html=True)

            drivers = generate_driver_standings(tifosi_pin=tifosi)
            max_pts = max(d["pts"] for d in drivers)

            for d in drivers[:8]:
                team_color = TEAM_COLORS.get(d["team"], TEXT_SECONDARY)
                is_ferrari = d["team"] == "Ferrari"
                pos_cls    = {1: "p1", 2: "p2", 3: "p3"}.get(d["pos"], "")
                bar_pct    = (d["pts"] / max_pts) * 100

                st.markdown(f"""
                <div class="champ-badge" style="{'border-left: 3px solid ' + FERRARI_RED + ';' if is_ferrari else ''}">
                    <div class="champ-pos {pos_cls}">{d['pos']}</div>
                    <div style="font-family:'Share Tech Mono',monospace; font-size:0.7rem; 
                                width:30px; color:{TEXT_SECONDARY};">
                        {d['flag']}
                    </div>
                    <div style="flex:1; min-width:0;">
                        <div style="font-family:'Orbitron',monospace; font-size:0.8rem; 
                                    font-weight:700; color:{''+FERRARI_RED if is_ferrari else TEXT_PRIMARY};">
                            {d['code']}
                        </div>
                        <div class="champ-bar-track" style="margin-top:4px;">
                            <div style="width:{bar_pct:.0f}%; height:100%; 
                                        background:{team_color}; border-radius:3px;"></div>
                        </div>
                    </div>
                    <div style="font-family:'Orbitron',monospace; font-size:0.85rem; 
                                font-weight:700; color:{TEXT_PRIMARY}; width:40px; text-align:right;">
                        {d['pts']}
                    </div>
                    <div style="font-family:'Share Tech Mono',monospace; font-size:0.6rem; 
                                color:{TEXT_SECONDARY}; width:60px; text-align:right;">
                        {d['team']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Bottom: Gap to Leader mini-chart ─────────────────────────────────────
    st.markdown("<hr style='border-color:#2A2F3A; margin: 16px 0;'>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-header">📈 Gap Evolution · HAM to ANT</div>',
                unsafe_allow_html=True)

    laps_range = np.arange(1, TOTAL_LAPS + 1)
    rng2 = np.random.default_rng(77)
    gap = np.cumsum(rng2.normal(-0.08, 0.4, TOTAL_LAPS))
    gap = gap - gap[0] + 12.5
    gap = np.clip(gap, 0.5, 20)

    fig_gap = go.Figure()
    fig_gap.add_trace(go.Scatter(
        x=laps_range, y=gap,
        line=dict(color=FERRARI_RED, width=2.5),
        fill="tozeroy",
        fillcolor=f"{FERRARI_RED}18",
        name="HAM Gap to Leader",
        hovertemplate="Lap %{x}<br>Gap: +%{y:.2f}s<extra></extra>",
    ))
    fig_gap.add_vline(x=lap, line_color=GOLD, line_width=1.5, line_dash="dash",
                      annotation_text=f"  Lap {lap}", annotation_font=dict(color=GOLD, size=9))
    fig_gap.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=130,
        margin=dict(l=40, r=20, t=10, b=30),
        xaxis=dict(gridcolor=BORDER_SUBTLE, color=TEXT_SECONDARY, zeroline=False,
                   title_text="Lap", title_font=dict(size=9, family="Share Tech Mono")),
        yaxis=dict(gridcolor=BORDER_SUBTLE, color=TEXT_SECONDARY, zeroline=False,
                   title_text="Gap (s)", title_font=dict(size=9, family="Share Tech Mono")),
        showlegend=False,
        hovermode="x",
    )
    st.plotly_chart(fig_gap, use_container_width=True, config={"displayModeBar": False})

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center; padding:16px 0 8px; 
                font-family:'Share Tech Mono',monospace; font-size:0.6rem; 
                color:{TEXT_SECONDARY}; letter-spacing:0.15em;">
        SCUDERIA FERRARI MISSION CONTROL · 2026 FIA FORMULA ONE WORLD CHAMPIONSHIP
        {'· TIFOSI MODE ACTIVE 🔴' if tifosi else ''}
        {'· ⚠ MOCK DATA MODE — FastF1 2026 cache not available' if USE_MOCK else '· FASTF1 LIVE DATA'}
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
