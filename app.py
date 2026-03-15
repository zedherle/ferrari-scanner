"""
Scuderia Ferrari Mission Control
=================================
Ferrari-fan-first F1 dashboard.
Select a race → live/ended status → race standings → championship table.
FastF1-powered. Graceful mock fallback.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import random
from datetime import datetime, timezone, timedelta

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ferrari Mission Control",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={},
)

# ─── FastF1 ───────────────────────────────────────────────────────────────────
USE_MOCK = False
try:
    import fastf1
    import fastf1.plotting
    fastf1.Cache.enable_cache("./f1_cache")
    FASTF1_AVAILABLE = True
except Exception:
    FASTF1_AVAILABLE = False
    USE_MOCK = True

# ─── Constants ────────────────────────────────────────────────────────────────
RED        = "#EF1A2D"
DARK       = "#08090C"
SURFACE    = "#0F1117"
CARD       = "#14171F"
CARD2      = "#1A1E28"
BORDER     = "#1F2433"
BORDER2    = "#2A3045"
TEXT       = "#EEF0F5"
MUTED      = "#5A6A82"
MUTED2     = "#8A9BB0"
GOLD       = "#F5C518"
SILVER     = "#A8B8C8"
GREEN      = "#22C55E"
ORANGE     = "#F97316"

TEAM_COLORS = {
    "Ferrari":      RED,
    "Mercedes":     "#00D2BE",
    "Red Bull":     "#3671C6",
    "McLaren":      "#FF8000",
    "Aston Martin": "#358C75",
    "Williams":     "#64C4FF",
    "Alpine":       "#0090FF",
    "Haas":         "#B6BABD",
    "Kick Sauber":  "#52E252",
    "RB":           "#6692FF",
}

DRIVER_INFO = {
    "HAM": {"name": "Lewis Hamilton",   "short": "Hamilton",   "num": 44, "team": "Ferrari",      "flag": "🇬🇧"},
    "LEC": {"name": "Charles Leclerc",  "short": "Leclerc",    "num": 16, "team": "Ferrari",      "flag": "🇲🇨"},
    "ANT": {"name": "Kimi Antonelli",   "short": "Antonelli",  "num": 12, "team": "Mercedes",     "flag": "🇮🇹"},
    "RUS": {"name": "George Russell",   "short": "Russell",    "num": 63, "team": "Mercedes",     "flag": "🇬🇧"},
    "VER": {"name": "Max Verstappen",   "short": "Verstappen", "num": 1,  "team": "Red Bull",     "flag": "🇳🇱"},
    "NOR": {"name": "Lando Norris",     "short": "Norris",     "num": 4,  "team": "McLaren",      "flag": "🇬🇧"},
    "PIA": {"name": "Oscar Piastri",    "short": "Piastri",    "num": 81, "team": "McLaren",      "flag": "🇦🇺"},
    "ALO": {"name": "Fernando Alonso",  "short": "Alonso",     "num": 14, "team": "Aston Martin", "flag": "🇪🇸"},
    "SAI": {"name": "Carlos Sainz Jr.", "short": "Sainz",      "num": 55, "team": "Williams",     "flag": "🇪🇸"},
    "TSU": {"name": "Yuki Tsunoda",     "short": "Tsunoda",    "num": 22, "team": "Red Bull",     "flag": "🇯🇵"},
}

PTS_MAP = {1:25, 2:18, 3:15, 4:12, 5:10, 6:8, 7:6, 8:4, 9:2, 10:1}

# ─── Mock data ────────────────────────────────────────────────────────────────
MOCK_RACES = [
    {
        "round": 3, "name": "Chinese Grand Prix", "short": "CHN",
        "location": "Shanghai", "date": "2026-03-23", "laps": 56, "status": "finished",
        "results": [
            {"pos":1,"code":"ANT","team":"Mercedes","gap":"WINNER","pts":25,"fl":False},
            {"pos":2,"code":"RUS","team":"Mercedes","gap":"+1.827s","pts":18,"fl":False},
            {"pos":3,"code":"HAM","team":"Ferrari","gap":"+3.214s","pts":15,"fl":False},
            {"pos":4,"code":"LEC","team":"Ferrari","gap":"+5.102s","pts":12,"fl":True},
            {"pos":5,"code":"NOR","team":"McLaren","gap":"+8.441s","pts":10,"fl":False},
            {"pos":6,"code":"PIA","team":"McLaren","gap":"+11.20s","pts":8,"fl":False},
            {"pos":7,"code":"VER","team":"Red Bull","gap":"+18.77s","pts":6,"fl":False},
            {"pos":8,"code":"TSU","team":"Red Bull","gap":"+23.41s","pts":4,"fl":False},
            {"pos":9,"code":"ALO","team":"Aston Martin","gap":"+31.88s","pts":2,"fl":False},
            {"pos":10,"code":"SAI","team":"Williams","gap":"+38.12s","pts":1,"fl":False},
        ]
    },
    {
        "round": 2, "name": "Australian Grand Prix", "short": "AUS",
        "location": "Melbourne", "date": "2026-03-09", "laps": 58, "status": "finished",
        "results": [
            {"pos":1,"code":"ANT","team":"Mercedes","gap":"WINNER","pts":25,"fl":False},
            {"pos":2,"code":"HAM","team":"Ferrari","gap":"+4.112s","pts":18,"fl":False},
            {"pos":3,"code":"RUS","team":"Mercedes","gap":"+6.991s","pts":15,"fl":False},
            {"pos":4,"code":"NOR","team":"McLaren","gap":"+9.234s","pts":12,"fl":False},
            {"pos":5,"code":"LEC","team":"Ferrari","gap":"+12.55s","pts":10,"fl":True},
            {"pos":6,"code":"VER","team":"Red Bull","gap":"+15.88s","pts":8,"fl":False},
            {"pos":7,"code":"PIA","team":"McLaren","gap":"+19.22s","pts":6,"fl":False},
            {"pos":8,"code":"TSU","team":"Red Bull","gap":"+25.10s","pts":4,"fl":False},
            {"pos":9,"code":"ALO","team":"Aston Martin","gap":"+34.66s","pts":2,"fl":False},
            {"pos":10,"code":"SAI","team":"Williams","gap":"+41.00s","pts":1,"fl":False},
        ]
    },
    {
        "round": 1, "name": "Bahrain Grand Prix", "short": "BHR",
        "location": "Sakhir", "date": "2026-03-02", "laps": 57, "status": "finished",
        "results": [
            {"pos":1,"code":"RUS","team":"Mercedes","gap":"WINNER","pts":25,"fl":False},
            {"pos":2,"code":"ANT","team":"Mercedes","gap":"+2.341s","pts":18,"fl":False},
            {"pos":3,"code":"LEC","team":"Ferrari","gap":"+8.712s","pts":15,"fl":False},
            {"pos":4,"code":"HAM","team":"Ferrari","gap":"+11.33s","pts":12,"fl":True},
            {"pos":5,"code":"VER","team":"Red Bull","gap":"+14.88s","pts":10,"fl":False},
            {"pos":6,"code":"NOR","team":"McLaren","gap":"+18.22s","pts":8,"fl":False},
            {"pos":7,"code":"PIA","team":"McLaren","gap":"+22.10s","pts":6,"fl":False},
            {"pos":8,"code":"TSU","team":"Red Bull","gap":"+28.55s","pts":4,"fl":False},
            {"pos":9,"code":"ALO","team":"Aston Martin","gap":"+35.44s","pts":2,"fl":False},
            {"pos":10,"code":"SAI","team":"Williams","gap":"+44.77s","pts":1,"fl":False},
        ]
    },
]

def build_championship_from_races(races):
    """Compute cumulative driver + constructor standings from race results."""
    driver_pts   = {}
    team_pts     = {}
    driver_races = {}  # code → [pts per race]

    for race in sorted(races, key=lambda r: r["round"]):
        seen_in_race = set()
        for r in race["results"]:
            code = r["code"]
            team = r["team"]
            p    = r["pts"]
            # bonus for fastest lap (if in top 10)
            if r.get("fl") and r["pos"] <= 10:
                p += 1
            driver_pts[code]   = driver_pts.get(code, 0) + p
            team_pts[team]     = team_pts.get(team, 0) + p
            if code not in driver_races:
                driver_races[code] = []
            driver_races[code].append(p)
            seen_in_race.add(code)
        # drivers not in race get 0
        for code in driver_pts:
            if code not in seen_in_race:
                if len(driver_races.get(code, [])) < race["round"]:
                    driver_races.setdefault(code, []).append(0)

    driver_list = sorted(
        [{"code": k, "pts": v,
          "team": DRIVER_INFO.get(k, {}).get("team", ""),
          "name": DRIVER_INFO.get(k, {}).get("short", k),
          "flag": DRIVER_INFO.get(k, {}).get("flag", "🏁"),
          "race_pts": driver_races.get(k, [])}
         for k, v in driver_pts.items()],
        key=lambda x: x["pts"], reverse=True
    )
    for i, d in enumerate(driver_list):
        d["pos"] = i + 1

    team_list = sorted(
        [{"team": k, "pts": v, "color": TEAM_COLORS.get(k, MUTED)}
         for k, v in team_pts.items()],
        key=lambda x: x["pts"], reverse=True
    )
    for i, t in enumerate(team_list):
        t["pos"] = i + 1

    return driver_list, team_list

# ─── FastF1 loaders ───────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_season_rounds(year: int = 2026):
    try:
        from datetime import timezone as tz
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        now = datetime.now(tz.utc)
        rows = []
        for _, row in schedule.iterrows():
            event_dt = pd.to_datetime(row["EventDate"], utc=True)
            status = "live" if abs((event_dt - now).total_seconds()) < 7200 else \
                     "finished" if event_dt < now else "upcoming"
            rows.append({
                "round":    int(row["RoundNumber"]),
                "name":     row["EventName"],
                "short":    row.get("EventName", "")[:3].upper(),
                "location": row["Location"],
                "country":  row["Country"],
                "date":     str(row["EventDate"])[:10],
                "status":   status,
            })
        completed = [r for r in rows if r["status"] in ("finished", "live")]
        return sorted(completed, key=lambda r: r["round"], reverse=True)
    except Exception:
        return []

@st.cache_data(show_spinner=False)
def _load_f1_session_cached(year: int, round_num: int):
    try:
        session = fastf1.get_session(year, round_num, "R")
        session.load(telemetry=False, laps=True, weather=False)
        loaded_at = datetime.now(timezone.utc)
        return session, None, loaded_at
    except Exception as e:
        return None, str(e), None

def load_f1_session(year=2026, round_num=None):
    if round_num is None:
        rounds = fetch_season_rounds(year)
        round_num = rounds[0]["round"] if rounds else 1
    return _load_f1_session_cached(year, round_num)

@st.cache_data(show_spinner=False)
def get_race_results_from_session(session):
    """Extract finishing order from FastF1 session laps."""
    try:
        laps = session.laps
        last = (laps.sort_values("LapNumber", ascending=False)
                .drop_duplicates(subset="Driver")
                .sort_values("Position"))
        results = []
        for i, row in enumerate(last.itertuples()):
            code = str(row.Driver)
            pos  = i + 1
            pts  = PTS_MAP.get(pos, 0)
            results.append({
                "pos":  pos,
                "code": code,
                "team": DRIVER_INFO.get(code, {}).get("team", ""),
                "gap":  "WINNER" if pos == 1 else "—",
                "pts":  pts,
                "fl":   False,
            })
        return results
    except Exception:
        return None

@st.cache_data(show_spinner=False)
def get_ergast_standings(year: int, round_num: int):
    try:
        ergast = fastf1.ergast.Ergast()
        cs = ergast.get_constructor_standings(season=year, round=round_num)
        ds = ergast.get_driver_standings(season=year, round=round_num)
        constructors = []
        for row in cs.content[0].itertuples():
            constructors.append({
                "pos":   int(row.position),
                "team":  row.constructorName,
                "pts":   int(row.points),
                "color": TEAM_COLORS.get(row.constructorName, MUTED),
            })
        drivers = []
        for row in ds.content[0].itertuples():
            code = getattr(row, "driverCode", None) or row.familyName[:3].upper()
            drivers.append({
                "pos":  int(row.position),
                "code": code,
                "name": row.familyName,
                "team": row.constructorName,
                "pts":  int(row.points),
                "flag": "🏁",
                "race_pts": [],
            })
        if drivers:
            mp = max(d["pts"] for d in drivers) or 1
            for d in drivers:
                d["pct"] = round(d["pts"] / mp * 100)
        return {"drivers": drivers, "constructors": constructors}
    except Exception:
        return None

def relative_time(dt):
    if not dt:
        return "—"
    now   = datetime.now(timezone.utc)
    delta = now - (dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt)
    s = int(delta.total_seconds())
    if s < 60:   return "just now"
    if s < 3600: return f"{s//60} min ago"
    if s < 86400:return f"{s//3600} hr{'s' if s//3600>1 else ''} ago"
    return f"{s//86400} day{'s' if s//86400>1 else ''} ago"

# ─── CSS ──────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Barlow:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Barlow+Condensed:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');

    @keyframes fade-in   {{ from{{opacity:0;transform:translateY(8px)}} to{{opacity:1;transform:none}} }}
    @keyframes bar-grow  {{ from{{width:0}} }}
    @keyframes pulse-red {{ 0%,100%{{opacity:1}} 50%{{opacity:.5}} }}
    @keyframes live-dot  {{ 0%,100%{{transform:scale(1);opacity:1}} 50%{{transform:scale(1.4);opacity:.6}} }}

    html,body,[class*="css"] {{
        background:{DARK} !important; color:{TEXT} !important;
        font-family:'Barlow',sans-serif;
    }}
    .stApp {{ background:{DARK} !important; }}

    /* ── Hide ALL chrome ── */
    #MainMenu,footer,header[data-testid="stHeader"],
    .viewerBadge_container__1QSob,[data-testid="stToolbar"],
    [data-testid="stDecoration"],[data-testid="stStatusWidget"],
    [data-testid="stDeployButton"],.stDeployButton,
    button[title="View fullscreen"],button[title="Edit"],
    [data-testid="baseButton-header"],._profileContainer_gzau3_53,
    ._link_gzau3_26,.st-emotion-cache-zq5wmm
    {{ display:none !important; }}
    .block-container {{ padding-top:.75rem !important; max-width:1400px; }}
    [data-testid="stSidebar"] {{ display:none !important; }}

    /* ── Selectbox ── */
    [data-testid="stSelectbox"] > div > div {{
        background:{CARD} !important;
        border:1px solid {BORDER2} !important;
        border-radius:8px !important;
        font-family:'Barlow Condensed',sans-serif !important;
        font-size:1rem !important;
        color:{TEXT} !important;
    }}
    [data-testid="stSelectbox"] label {{
        font-family:'Orbitron',monospace !important;
        font-size:.6rem !important;
        letter-spacing:.18em !important;
        color:{MUTED2} !important;
        text-transform:uppercase;
    }}

    /* ── Metrics ── */
    [data-testid="metric-container"] {{
        background:{CARD} !important;
        border:1px solid {BORDER} !important;
        border-radius:10px !important;
        padding:14px 16px !important;
    }}
    [data-testid="stMetricValue"] {{
        font-family:'Orbitron',monospace !important;
        font-size:1.3rem !important;
        color:{RED} !important;
    }}
    [data-testid="stMetricLabel"] {{
        font-family:'Share Tech Mono',monospace !important;
        font-size:.65rem !important;
        color:{MUTED2} !important;
        letter-spacing:.1em !important;
        text-transform:uppercase !important;
    }}

    /* ── Shared card ── */
    .fc {{ background:{CARD}; border:1px solid {BORDER}; border-radius:12px;
           padding:18px 20px; margin-bottom:12px; position:relative; overflow:hidden;
           animation: fade-in .35s ease both; }}
    .fc::before {{ content:''; position:absolute; top:0;left:0;right:0; height:2px;
                   background:linear-gradient(90deg,{RED},transparent); }}
    .fc.ferrari {{ border-left:3px solid {RED}; }}
    .fc.gold    {{ border-left:3px solid {GOLD}; }}
    .fc.silver  {{ border-left:3px solid {SILVER}; }}

    /* ── Section label ── */
    .slabel {{ font-family:'Orbitron',monospace; font-size:.6rem; font-weight:700;
               letter-spacing:.22em; color:{RED}; text-transform:uppercase;
               padding-bottom:6px; border-bottom:1px solid {BORDER2}; margin-bottom:14px; }}

    /* ── Race selector card ── */
    .race-hero {{
        background:linear-gradient(135deg, {CARD} 0%, {CARD2} 100%);
        border:1px solid {BORDER2}; border-radius:14px;
        padding:20px 24px; margin-bottom:16px;
        display:flex; align-items:center; gap:20px;
        animation: fade-in .4s ease;
    }}
    .rh-flag {{ font-size:2.8rem; line-height:1; flex-shrink:0; }}
    .rh-round {{ font-family:'Orbitron',monospace; font-size:.6rem;
                 color:{MUTED2}; letter-spacing:.2em; }}
    .rh-name  {{ font-family:'Orbitron',monospace; font-size:1.3rem;
                 font-weight:900; color:{TEXT}; margin:2px 0 4px; }}
    .rh-meta  {{ font-family:'Barlow Condensed',sans-serif; font-size:.9rem;
                 color:{MUTED2}; }}

    /* ── Status pill ── */
    .spill {{
        display:inline-flex; align-items:center; gap:6px;
        padding:4px 12px; border-radius:20px;
        font-family:'Share Tech Mono',monospace; font-size:.7rem;
        letter-spacing:.1em; font-weight:700; flex-shrink:0;
    }}
    .spill.live     {{ background:rgba(239,26,45,.15); color:{RED};
                       border:1px solid {RED}50; }}
    .spill.finished {{ background:rgba(90,106,130,.12); color:{MUTED2};
                       border:1px solid {BORDER2}; }}
    .spill .dot     {{ width:7px; height:7px; border-radius:50%;
                       background:currentColor; flex-shrink:0; }}
    .spill.live .dot {{ animation: live-dot 1.2s ease-in-out infinite; }}

    /* ── Lap bar ── */
    .lap-bar {{
        background:{CARD}; border:1px solid {BORDER}; border-radius:10px;
        padding:12px 18px; margin-bottom:14px;
        display:flex; align-items:center; gap:14px;
    }}
    .lb-lbl {{ font-family:'Share Tech Mono',monospace; font-size:.65rem;
               color:{MUTED}; white-space:nowrap; }}
    .lb-num {{ font-family:'Orbitron',monospace; font-size:1.2rem;
               font-weight:900; color:{RED}; white-space:nowrap; }}
    .lb-track {{ flex:1; height:6px; background:{BORDER2};
                 border-radius:3px; overflow:hidden; }}
    .lb-fill  {{ height:100%; border-radius:3px;
                 background:linear-gradient(90deg,{RED},#FF6060);
                 animation: bar-grow .6s ease; }}
    .lb-ended {{ font-family:'Orbitron',monospace; font-size:.7rem;
                 color:{MUTED2}; letter-spacing:.15em; white-space:nowrap; }}

    /* ── Timing rows ── */
    .trow {{
        display:flex; align-items:center; gap:0;
        padding:8px 14px; margin-bottom:3px;
        border-radius:7px; background:{SURFACE};
        border:1px solid {BORDER};
        font-family:'Barlow Condensed',sans-serif;
        transition:background .15s;
        animation: fade-in .3s ease both;
    }}
    .trow:hover {{ background:{CARD2}; }}
    .trow.is-ferrari {{
        background:linear-gradient(90deg,rgba(239,26,45,.1) 0%,{SURFACE} 55%);
        border-left:3px solid {RED};
    }}
    .trow.is-p1 {{ border-left:3px solid {GOLD}; }}

    /* ── Championship driver rows ── */
    .drow {{
        display:flex; align-items:center; gap:12px;
        padding:10px 14px; margin-bottom:4px;
        background:{SURFACE}; border:1px solid {BORDER};
        border-radius:8px; animation: fade-in .3s ease both;
    }}
    .drow.is-ferrari {{ border-left:3px solid {RED};
        background:linear-gradient(90deg,rgba(239,26,45,.08) 0%,{SURFACE} 50%); }}
    .drow .pos-num {{
        font-family:'Orbitron',monospace; font-size:1rem; font-weight:900;
        width:26px; flex-shrink:0; text-align:center;
    }}
    .drow .bar-track {{ flex:1; height:5px; background:{BORDER2};
                        border-radius:3px; overflow:hidden; margin-top:3px; }}
    .drow .bar-fill  {{ height:100%; border-radius:3px;
                        animation: bar-grow .7s ease; }}

    /* ── Constructor bar ── */
    .crow {{
        display:flex; align-items:center; gap:12px;
        padding:9px 14px; margin-bottom:4px;
        background:{SURFACE}; border:1px solid {BORDER};
        border-radius:8px;
    }}
    .crow .bar-track {{ flex:1; height:7px; background:{BORDER2};
                        border-radius:4px; overflow:hidden; }}
    .crow .bar-fill  {{ height:100%; border-radius:4px;
                        animation: bar-grow .7s ease; }}

    /* ── Ferrari hero card ── */
    .ferrari-hero {{
        background:linear-gradient(135deg, rgba(239,26,45,.12) 0%, {CARD} 60%);
        border:1px solid rgba(239,26,45,.3); border-radius:14px;
        padding:16px 20px; margin-bottom:10px; position:relative; overflow:hidden;
    }}
    .ferrari-hero::before {{ content:''; position:absolute; top:0;left:0;right:0;
                              height:2px; background:{RED}; }}
    .fh-driver {{ font-family:'Orbitron',monospace; font-size:.6rem;
                  color:{RED}; letter-spacing:.2em; margin-bottom:2px; }}
    .fh-name   {{ font-family:'Orbitron',monospace; font-size:1.1rem;
                  font-weight:900; color:{TEXT}; }}
    .fh-num    {{ font-family:'Orbitron',monospace; font-size:3rem;
                  font-weight:900; color:{RED}; opacity:.15;
                  position:absolute; right:16px; top:8px; line-height:1; }}
    .fh-stat   {{ display:flex; gap:16px; margin-top:10px; flex-wrap:wrap; }}
    .fh-stat-box {{ text-align:center; }}
    .fh-stat-val {{ font-family:'Orbitron',monospace; font-size:1.2rem;
                    font-weight:700; color:{TEXT}; }}
    .fh-stat-lbl {{ font-family:'Share Tech Mono',monospace; font-size:.6rem;
                    color:{MUTED2}; letter-spacing:.1em; }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width:4px }}
    ::-webkit-scrollbar-track {{ background:transparent }}
    ::-webkit-scrollbar-thumb {{ background:{BORDER2}; border-radius:2px }}

    /* ── Plotly bg ── */
    .js-plotly-plot .plotly {{ font-family:'Barlow',sans-serif !important; }}

    /* ── Telemetry grid ── */
    .telem-grid {{ display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:5px; margin:10px 0 10px; }}
    .t-box {{
        background:{DARK}; border:1px solid {BORDER2};
        border-radius:6px; padding:6px 8px; text-align:center;
    }}
    .t-lbl {{ font-family:'Share Tech Mono',monospace; font-size:.58rem;
              color:{MUTED}; letter-spacing:.08em; text-transform:uppercase; }}
    .t-val {{ font-family:'Orbitron',monospace; font-size:1.05rem; font-weight:700; line-height:1.2; }}
    .t-spd {{ color:#64C4FF; }}
    .t-thr {{ color:{GREEN}; }}
    .t-brk {{ color:{RED}; }}
    .t-ger {{ color:{GOLD}; }}

    /* ── Tyre row ── */
    .tyre-row {{ display:flex; align-items:center; gap:8px; }}
    .tyre-dot {{
        width:26px; height:26px; border-radius:50%;
        background:#E0E0E0; color:#111;
        display:flex; align-items:center; justify-content:center;
        font-family:'Orbitron',monospace; font-size:.65rem; font-weight:900; flex-shrink:0;
    }}
    .tyre-info {{ flex:1; }}
    .tyre-meta {{ font-family:'Share Tech Mono',monospace; font-size:.62rem;
                 color:{MUTED2}; margin-bottom:4px; }}
    .tyre-bar-track {{ background:{BORDER2}; border-radius:2px; height:4px; overflow:hidden; }}
    .tyre-bar-fill  {{ height:100%; border-radius:2px; transition:width .5s; }}
    </style>
    """, unsafe_allow_html=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
COUNTRY_FLAGS = {
    "China": "🇨🇳", "Australia": "🇦🇺", "Bahrain": "🇧🇭",
    "Saudi Arabia": "🇸🇦", "Japan": "🇯🇵", "Monaco": "🇲🇨",
    "Spain": "🇪🇸", "Canada": "🇨🇦", "Austria": "🇦🇹",
    "UK": "🇬🇧", "Hungary": "🇭🇺", "Belgium": "🇧🇪",
    "Netherlands": "🇳🇱", "Italy": "🇮🇹", "Azerbaijan": "🇦🇿",
    "Singapore": "🇸🇬", "USA": "🇺🇸", "Mexico": "🇲🇽",
    "Brazil": "🇧🇷", "Qatar": "🇶🇦", "Abu Dhabi": "🇦🇪",
}

def country_flag(country):
    return COUNTRY_FLAGS.get(country, "🏁")

def pos_color(p):
    return GOLD if p == 1 else SILVER if p == 2 else "#CD7F32" if p == 3 else MUTED2

def tyre_html(compound):
    colors = {"H": ("#E0E0E0","#111"), "M": ("#FFD700","#111"), "S": (RED,"#fff"),
              "I": ("#39a0ff","#fff"), "W": ("#1de3a0","#fff")}
    bg, fg = colors.get(compound, (MUTED, "#fff"))
    return f'<span style="background:{bg};color:{fg};border-radius:50%;display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;font-family:\'Orbitron\',monospace;font-size:.55rem;font-weight:900;flex-shrink:0;">{compound}</span>'

# ─── Chart: Championship points progression ───────────────────────────────────
# ─── Telemetry card HTML builder ─────────────────────────────────────────────
def telem_html(code, telem_data, RED, DARK, BORDER2, MUTED, MUTED2, GREEN, GOLD, ORANGE):
    t        = telem_data.get(code, {})
    spd      = t.get("spd", "—")
    thr      = t.get("thr", "—")
    brk      = t.get("brk", "—")
    ger      = t.get("ger", "—")
    comp     = t.get("compound", "H")
    lap      = t.get("tyre_lap", 0)
    mx       = t.get("tyre_max", 30)
    pct      = min(100, round(lap / mx * 100))
    bar_col  = RED if pct > 60 else ORANGE if pct > 30 else GREEN
    tyre_bg  = {"H":"#E0E0E0","M":"#FFD700","S":RED,"I":"#39a0ff","W":"#1de3a0"}.get(comp,"#888")
    tyre_fg  = "#111" if comp in ("H","M") else "#fff"
    comp_lbl = {"H":"HARD","M":"MEDIUM","S":"SOFT","I":"INTER","W":"WET"}.get(comp, comp)
    return f"""
    <div class="telem-grid">
        <div class="t-box"><div class="t-lbl">SPD</div><div class="t-val t-spd">{spd}</div></div>
        <div class="t-box"><div class="t-lbl">THR</div><div class="t-val t-thr">{thr}%</div></div>
        <div class="t-box"><div class="t-lbl">BRK</div><div class="t-val t-brk">{brk}%</div></div>
        <div class="t-box"><div class="t-lbl">GER</div><div class="t-val t-ger">{ger}</div></div>
    </div>
    <div class="tyre-row">
        <div class="tyre-dot" style="background:{tyre_bg};color:{tyre_fg};">{comp}</div>
        <div class="tyre-info">
            <div class="tyre-meta">{comp_lbl} &nbsp;·&nbsp; LAP {lap}/~{mx}</div>
            <div class="tyre-bar-track">
                <div class="tyre-bar-fill" style="width:{pct}%;background:{bar_col};"></div>
            </div>
        </div>
    </div>"""

def main():
    inject_css()

    if "tifosi" not in st.session_state:
        st.session_state["tifosi"] = True

    # Mock live telemetry — cycles on each rerun via tick
    tick = st.session_state.get("tick", 0)
    _telem = {
        "HAM": {
            "spd":  [312,318,305,320,308,315,322,298][tick % 8],
            "thr":  [94,98,88,100,92,97,99,85][tick % 8],
            "brk":  [1,0,5,0,2,0,0,8][tick % 8],
            "ger":  [8,8,7,8,8,8,8,7][tick % 8],
            "compound": "H", "tyre_lap": 18, "tyre_max": 30,
        },
        "LEC": {
            "spd":  [319,308,316,302,311,320,306,314][tick % 8],
            "thr":  [96,90,99,84,93,100,88,95][tick % 8],
            "brk":  [0,3,0,6,1,0,4,0][tick % 8],
            "ger":  [8,8,8,7,8,8,8,8][tick % 8],
            "compound": "H", "tyre_lap": 18, "tyre_max": 30,
        },
    }

    # ── Load available rounds ─────────────────────────────────────────────────
    season_rounds = []
    if FASTF1_AVAILABLE and not USE_MOCK:
        season_rounds = fetch_season_rounds(2026)
    if not season_rounds:
        season_rounds = [
            {"round": r["round"], "name": r["name"], "short": r["short"],
             "location": r["location"], "country": "China" if r["round"]==3
             else "Australia" if r["round"]==2 else "Bahrain",
             "date": r["date"], "status": r["status"]}
            for r in MOCK_RACES
        ]

    # ── Top bar: wordmark + round selector + tifosi toggle ───────────────────
    h1, h2, h3 = st.columns([2, 4, 1.2], gap="medium")
    with h1:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:6px 0;">
            <div style="width:32px;height:32px;background:{RED};
                        clip-path:polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%);
                        flex-shrink:0;"></div>
            <div>
                <div style="font-family:'Orbitron',monospace;font-size:1.1rem;
                            font-weight:900;color:{RED};letter-spacing:.05em;
                            line-height:1.1;">FERRARI</div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:.55rem;
                            color:{MUTED};letter-spacing:.2em;">MISSION CONTROL</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with h2:
        round_labels = [
            f"R{r['round']} · {r['name']}  —  {r['date']}"
            for r in season_rounds
        ]
        sel_idx = st.selectbox(
            "SELECT RACE",
            options=range(len(round_labels)),
            format_func=lambda i: round_labels[i],
            index=0,
            key="race_sel",
            label_visibility="visible",
        )

    with h3:
        last_upd = st.session_state.get("loaded_at")
        rel      = relative_time(last_upd) if last_upd else "—"
        tifosi   = st.session_state["tifosi"]
        tog_lbl  = "🔴 TIFOSI ON" if tifosi else "⚪ TIFOSI OFF"
        # Spacer matches the SELECT RACE label height so button aligns with dropdown
        st.markdown(
            f'<div style="font-family:Orbitron,monospace;font-size:.6rem;'
            f'letter-spacing:.18em;color:transparent;margin-bottom:4px;">SELECT RACE</div>',
            unsafe_allow_html=True,
        )
        if st.button(tog_lbl, key="tifosi_btn", use_container_width=True):
            st.session_state["tifosi"] = not tifosi
            st.rerun()
        st.markdown(
            f'<div style="font-family:Share Tech Mono,monospace;font-size:.58rem;'
            f'color:{MUTED};text-align:center;margin-top:4px;">◉ LIVE · {rel}</div>',
            unsafe_allow_html=True,
        )

    tifosi = st.session_state["tifosi"]
    selected = season_rounds[sel_idx]
    is_latest = sel_idx == 0

    st.markdown(f"<hr style='border-color:{BORDER};margin:8px 0 14px;'>",
                unsafe_allow_html=True)

    # ── Load session data ─────────────────────────────────────────────────────
    session_data  = None
    race_results  = None
    race_laps     = None
    total_laps_r  = selected.get("laps", 56)

    if FASTF1_AVAILABLE and not USE_MOCK:
        with st.spinner(f"Loading {selected['name']}..."):
            session_data, err, loaded_at = load_f1_session(round_num=selected["round"])
            if session_data and not err:
                if loaded_at:
                    st.session_state["loaded_at"] = loaded_at
                race_results = get_race_results_from_session(session_data)
                try:
                    total_laps_r = int(session_data.laps["LapNumber"].max())
                    if selected["status"] == "live":
                        race_laps = int(session_data.laps["LapNumber"].max())
                    else:
                        race_laps = total_laps_r
                except Exception:
                    race_laps = total_laps_r

    # Fallback to mock results
    mock_race = next((r for r in MOCK_RACES if r["round"] == selected["round"]), MOCK_RACES[0])
    if race_results is None:
        race_results = mock_race["results"]
        total_laps_r = mock_race.get("laps", 56)
        race_laps    = total_laps_r if selected["status"] != "live" else total_laps_r - 2

    # ── Get all races up to selected round (for championship) ─────────────────
    races_to_date = [r for r in MOCK_RACES if r["round"] <= selected["round"]]

    # Try Ergast for standings, else compute from mock
    live_champ = None
    if FASTF1_AVAILABLE and not USE_MOCK:
        live_champ = get_ergast_standings(2026, selected["round"])

    if live_champ and live_champ.get("drivers"):
        driver_standings  = live_champ["drivers"]
        team_standings    = live_champ["constructors"]
    else:
        driver_standings, team_standings = build_championship_from_races(races_to_date)

    # Ferrari drivers from standings
    ferrari_drivers = [d for d in driver_standings if d.get("team") == "Ferrari"]

    # ── LAYOUT: 3 columns ─────────────────────────────────────────────────────
    col_left, col_mid, col_right = st.columns([1.1, 1.3, 1.2], gap="medium")

    # ══════════════════════════════════════════════════════════════════════════
    # LEFT: Race info + status + race standings
    # ══════════════════════════════════════════════════════════════════════════
    with col_left:

        # Race hero
        flag_emoji = country_flag(selected.get("country", ""))
        status_cls = "live" if selected["status"] == "live" else "finished"
        status_txt = "LIVE" if selected["status"] == "live" else "RACE ENDED"

        st.markdown(f"""
        <div class="race-hero">
            <div class="rh-flag">{flag_emoji}</div>
            <div style="flex:1;min-width:0;">
                <div class="rh-round">ROUND {selected['round']} · 2026</div>
                <div class="rh-name">{selected['name'].upper()}</div>
                <div class="rh-meta">📍 {selected['location']} &nbsp;·&nbsp; 🗓 {selected['date']}</div>
            </div>
            <div>
                <div class="spill {status_cls}">
                    <div class="dot"></div>{status_txt}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Lap bar
        if selected["status"] == "live":
            pct = round((race_laps / total_laps_r) * 100) if total_laps_r else 0
            st.markdown(f"""
            <div class="lap-bar">
                <div class="lb-lbl">LAP</div>
                <div class="lb-num">{race_laps}</div>
                <div class="lb-track"><div class="lb-fill" style="width:{pct}%"></div></div>
                <div class="lb-lbl">/ {total_laps_r}</div>
                <div class="lb-lbl">{pct}%</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="lap-bar">
                <div class="lb-track"><div class="lb-fill" style="width:100%"></div></div>
                <div class="lb-ended">✓ COMPLETED · {total_laps_r} LAPS</div>
            </div>
            """, unsafe_allow_html=True)

        # Race standings
        st.markdown(f'<div class="slabel">🏁 Race Result</div>', unsafe_allow_html=True)

        # Column header
        st.markdown(f"""
        <div style="display:flex;font-family:'Share Tech Mono',monospace;
                    font-size:.6rem;color:{MUTED};padding:0 14px 4px;
                    letter-spacing:.07em;">
            <span style="width:26px;">POS</span>
            <span style="width:150px;">DRIVER</span>
            <span style="flex:1;">TEAM</span>
            <span style="width:48px;text-align:right;">GAP</span>
            <span style="width:30px;text-align:right;">PTS</span>
        </div>
        """, unsafe_allow_html=True)

        for row in race_results:
            is_fer  = row["team"] == "Ferrari"
            is_p1   = row["pos"] == 1
            row_cls = "is-ferrari" if is_fer else ("is-p1" if is_p1 else "")
            pc      = pos_color(row["pos"])
            nc      = RED if is_fer else TEXT
            tc      = TEAM_COLORS.get(row["team"], MUTED2)
            gap_col = GOLD if row["gap"] == "WINNER" else (GREEN if "+" not in str(row["gap"]) and row["gap"] != "—" else MUTED2)
            fl_badge = ' <span style="font-family:Share Tech Mono,monospace;font-size:.55rem;color:#A78BFA;background:rgba(167,139,250,.15);border-radius:3px;padding:0 4px;">FL</span>' if row.get("fl") else ""
            delay = row["pos"] * 0.03

            full_name = DRIVER_INFO.get(row["code"], {}).get("name", row["code"])
            st.markdown(f"""
            <div class="trow {row_cls}" style="animation-delay:{delay:.2f}s">
                <span style="width:26px;font-family:'Orbitron',monospace;
                             font-size:.8rem;font-weight:900;color:{pc};">{row["pos"]}</span>
                <div style="width:150px;flex-shrink:0;">
                    <div style="font-family:'Barlow Condensed',sans-serif;
                                font-size:.95rem;font-weight:700;color:{nc};
                                line-height:1.2;">{full_name}</div>
                </div>
                <span style="flex:1;font-size:.82rem;color:{tc};
                             font-family:'Barlow Condensed',sans-serif;">{row["team"]}{fl_badge}</span>
                <span style="width:48px;text-align:right;font-family:'Share Tech Mono',monospace;
                             font-size:.72rem;color:{gap_col};">{row["gap"]}</span>
                <span style="width:30px;text-align:right;font-family:'Orbitron',monospace;
                             font-size:.8rem;font-weight:700;color:{GREEN};">{row["pts"]}</span>
            </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # MIDDLE: Ferrari spotlight + Driver championship
    # ══════════════════════════════════════════════════════════════════════════
    with col_mid:

        # Ferrari driver cards
        st.markdown(f'<div class="slabel">🔴 Ferrari Spotlight</div>', unsafe_allow_html=True)

        ferrari_race = [r for r in race_results if r["team"] == "Ferrari"]
        for fd in ferrari_race[:2]:
            info      = DRIVER_INFO.get(fd["code"], {})
            champ_row = next((d for d in driver_standings if d["code"] == fd["code"]), {})
            champ_pos = champ_row.get("pos", "—")
            champ_pts = champ_row.get("pts", 0)
            # Pre-compute fragments — no conditionals inside f-strings
            if champ_pos != 1 and driver_standings:
                gap_val  = driver_standings[0]["pts"] - champ_pts
                gap_frag = f'<div class="fh-stat-box"><div class="fh-stat-val" style="color:{ORANGE};">−{gap_val} pts</div><div class="fh-stat-lbl">GAP LEAD</div></div>'
            else:
                gap_frag = ""
            fl_frag = '<div class="fh-stat-box"><div class="fh-stat-val" style="color:#A78BFA;">FL</div><div class="fh-stat-lbl">FASTEST</div></div>' if fd.get("fl") else ""
            pc_champ = pos_color(champ_pos) if isinstance(champ_pos, int) else MUTED2

            t_block = telem_html(fd["code"], _telem, RED, DARK, BORDER2, MUTED, MUTED2, GREEN, GOLD, ORANGE)
            st.markdown(f"""
            <div class="ferrari-hero">
                <div class="fh-num">#{info.get("num","")}</div>
                <div style="display:flex;align-items:baseline;gap:10px;">
                    <div>
                        <div class="fh-driver">{info.get("flag","")} &nbsp; P{fd["pos"]} &nbsp;·&nbsp; FERRARI #{info.get("num","")}</div>
                        <div class="fh-name">{info.get("name","")}</div>
                    </div>
                </div>
                {t_block}
                <div class="fh-stat" style="margin-top:8px;">
                    <div class="fh-stat-box">
                        <div class="fh-stat-val">{fd["pts"]}</div>
                        <div class="fh-stat-lbl">PTS TODAY</div>
                    </div>
                    <div class="fh-stat-box">
                        <div class="fh-stat-val" style="color:{pc_champ};">P{champ_pos}</div>
                        <div class="fh-stat-lbl">CHAMP POS</div>
                    </div>
                    <div class="fh-stat-box">
                        <div class="fh-stat-val">{champ_pts}</div>
                        <div class="fh-stat-lbl">TOTAL PTS</div>
                    </div>
                    {gap_frag}
                    {fl_frag}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Driver championship standings
        st.markdown(f'<div class="slabel" style="margin-top:6px;">👤 Driver Championship</div>',
                    unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex;font-family:'Share Tech Mono',monospace;
                    font-size:.58rem;color:{MUTED};padding:0 14px 4px;
                    letter-spacing:.07em;">
            <span style="width:26px;">POS</span>
            <span style="width:20px;"></span>
            <span style="flex:1;">DRIVER / TEAM</span>
            <span style="width:36px;text-align:right;">PTS</span>
        </div>
        """, unsafe_allow_html=True)

        standings_to_show = driver_standings
        if tifosi:
            ferrari_d = [d for d in driver_standings if d.get("team") == "Ferrari"]
            others_d  = [d for d in driver_standings if d.get("team") != "Ferrari"]
            standings_to_show = ferrari_d + others_d

        max_d_pts = max((d["pts"] for d in driver_standings), default=1)

        for d in standings_to_show[:10]:
            is_fer  = d.get("team") == "Ferrari"
            tc      = TEAM_COLORS.get(d.get("team",""), MUTED)
            pc      = pos_color(d["pos"])
            delay   = d["pos"] * 0.035
            bar_pct = round(d["pts"] / max_d_pts * 100)
            race_pts_this = d.get("race_pts", [])
            last_race_pts = race_pts_this[-1] if race_pts_this else 0
            lrp_html = f'<div style="font-family:Share Tech Mono,monospace;font-size:.6rem;color:{GREEN};width:28px;text-align:right;flex-shrink:0;">+{last_race_pts}</div>' if last_race_pts else '<div style="width:28px;flex-shrink:0;"></div>'

            st.markdown(f"""
            <div class="drow {'is-ferrari' if is_fer else ''}"
                 style="animation-delay:{delay:.2f}s">
                <div class="pos-num" style="color:{pc};">{d['pos']}</div>
                <div style="font-size:.9rem;width:18px;flex-shrink:0;">{d.get('flag','🏁')}</div>
                <div style="width:36px;font-family:'Barlow Condensed',sans-serif;
                            font-size:1rem;font-weight:700;
                            color:{''+RED if is_fer else TEXT};flex-shrink:0;">{d['code']}</div>
                <div style="flex:1;min-width:0;">
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:.92rem;
                                font-weight:700;color:{''+RED if is_fer else TEXT};
                                line-height:1.2;">{DRIVER_INFO.get(d["code"],{{}}).get("name", d["code"])}</div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:.7rem;
                                color:{MUTED2};line-height:1.1;">{d.get("team","")}</div>
                    <div class="bar-track" style="margin-top:3px;">
                        <div class="bar-fill" style="width:{bar_pct}%;background:{tc};"></div>
                    </div>
                </div>
                <div style="font-family:'Orbitron',monospace;font-size:.9rem;
                            font-weight:700;color:{TEXT};width:32px;
                            text-align:right;flex-shrink:0;">{d['pts']}</div>
                {lrp_html}
            </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # RIGHT: Constructor championship + Ferrari Spotlight
    # ══════════════════════════════════════════════════════════════════════════
    with col_right:

        st.markdown(f'<div class="slabel">🏗 Constructor Championship</div>',
                    unsafe_allow_html=True)

        max_t_pts = max((t["pts"] for t in team_standings), default=1)

        for t in team_standings:
            is_fer    = t["team"] == "Ferrari"
            tc        = TEAM_COLORS.get(t["team"], MUTED)
            pc        = pos_color(t["pos"])
            bar_pct   = round(t["pts"] / max_t_pts * 100)
            row_style = f"border-left:3px solid {RED};background:linear-gradient(90deg,rgba(239,26,45,.08) 0%,{SURFACE} 50%);" if is_fer else ""
            name_col  = RED if is_fer else TEXT
            # Pre-compute gap fragment — avoids stray text in f-string conditionals
            if t["pos"] > 1:
                gap_val  = team_standings[0]["pts"] - t["pts"]
                gap_html = f'<div style="font-family:Share Tech Mono,monospace;font-size:.58rem;color:{ORANGE};">−{gap_val} pts</div>'
            else:
                gap_html = ""

            st.markdown(f"""
            <div class="crow" style="{row_style}">
                <div style="font-family:'Orbitron',monospace;font-size:.9rem;
                            font-weight:900;color:{pc};width:22px;
                            text-align:center;flex-shrink:0;">{t["pos"]}</div>
                <div style="width:10px;height:10px;border-radius:50%;
                            background:{tc};flex-shrink:0;"></div>
                <div style="flex:1;min-width:0;">
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:.95rem;
                                font-weight:700;color:{name_col};">{t["team"]}</div>
                    <div class="bar-track" style="margin-top:4px;">
                        <div class="bar-fill" style="width:{bar_pct}%;background:{tc};"></div>
                    </div>
                </div>
                <div style="text-align:right;flex-shrink:0;">
                    <div style="font-family:'Orbitron',monospace;font-size:.95rem;
                                font-weight:700;color:{TEXT};">{t["pts"]}</div>
                    {gap_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Ferrari Spotlight (moved from middle col)
        st.markdown(f'<div class="slabel" style="margin-top:14px;">🔴 Ferrari Spotlight</div>',
                    unsafe_allow_html=True)

        for fd in [r for r in race_results if r["team"] == "Ferrari"][:2]:
            info      = DRIVER_INFO.get(fd["code"], {})
            champ_row = next((d for d in driver_standings if d["code"] == fd["code"]), {})
            champ_pos = champ_row.get("pos", "—")
            champ_pts = champ_row.get("pts", 0)
            if champ_pos != 1 and driver_standings:
                gap_val  = driver_standings[0]["pts"] - champ_pts
                gap_frag = f'<div class="fh-stat-box"><div class="fh-stat-val" style="color:{ORANGE};">−{gap_val} pts</div><div class="fh-stat-lbl">GAP LEAD</div></div>'
            else:
                gap_frag = ""
            fl_frag   = '<div class="fh-stat-box"><div class="fh-stat-val" style="color:#A78BFA;">FL</div><div class="fh-stat-lbl">FASTEST</div></div>' if fd.get("fl") else ""
            pc_champ  = pos_color(champ_pos) if isinstance(champ_pos, int) else MUTED2
            t_block = telem_html(fd["code"], _telem, RED, DARK, BORDER2, MUTED, MUTED2, GREEN, GOLD, ORANGE)
            st.markdown(f"""
            <div class="ferrari-hero">
                <div class="fh-num">#{info.get("num","")}</div>
                <div style="display:flex;align-items:baseline;gap:10px;">
                    <div>
                        <div class="fh-driver">{info.get("flag","")} &nbsp; P{fd["pos"]} &nbsp;·&nbsp; FERRARI #{info.get("num","")}</div>
                        <div class="fh-name">{info.get("name","")}</div>
                    </div>
                </div>
                {t_block}
                <div class="fh-stat" style="margin-top:8px;">
                    <div class="fh-stat-box">
                        <div class="fh-stat-val">{fd["pts"]}</div>
                        <div class="fh-stat-lbl">PTS TODAY</div>
                    </div>
                    <div class="fh-stat-box">
                        <div class="fh-stat-val" style="color:{pc_champ};">P{champ_pos}</div>
                        <div class="fh-stat-lbl">CHAMP POS</div>
                    </div>
                    <div class="fh-stat-box">
                        <div class="fh-stat-val">{champ_pts}</div>
                        <div class="fh-stat-lbl">TOTAL PTS</div>
                    </div>
                    {gap_frag}
                    {fl_frag}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center;padding:20px 0 8px;font-family:'Share Tech Mono',
                monospace;font-size:.58rem;color:{MUTED};letter-spacing:.15em;
                border-top:1px solid {BORDER};margin-top:10px;">
        FERRARI MISSION CONTROL &nbsp;·&nbsp;
        2026 FIA FORMULA ONE WORLD CHAMPIONSHIP &nbsp;·&nbsp;
        {'🔴 TIFOSI MODE' if tifosi else 'STANDARD VIEW'}
    </div>
    """, unsafe_allow_html=True)

    # Tick telemetry sim
    st.session_state["tick"] = st.session_state.get("tick", 0) + 1

if __name__ == "__main__":
    main()
