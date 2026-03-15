# 🏎️ Scuderia Ferrari Mission Control
### High-Fidelity F1 Telemetry Dashboard · 2026 Chinese Grand Prix

---

## Quick Start

```bash
# 1. Clone / copy files to your project directory
# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
streamlit run app.py
```

The dashboard **launches immediately in Mock Data mode** — no internet or
FastF1 cache required. Once the 2026 Chinese GP data is available in the
FastF1 API, it will automatically switch to live data.

---

## Architecture

```
ferrari_dashboard/
├── app.py            # Main Streamlit application (single-file, modular)
├── requirements.txt  # Python dependencies
├── README.md
└── f1_cache/         # FastF1 cache (auto-created on first run)
```

### Key Modules inside `app.py`

| Function | Description |
|---|---|
| `inject_css()` | All theming: Orbitron/Rajdhani fonts, Ferrari Red palette, Tifosi glow |
| `generate_mock_telemetry()` | Shanghai-ish speed profile with per-driver offsets |
| `generate_mock_timing()` | Timing tower with Tifosi-pin logic |
| `load_f1_session()` | FastF1 session loader (cached, graceful fallback) |
| `render_battle_trace()` | Plotly Speed vs Distance overlay (HAM vs ANT) |
| `render_pedal_trace()` | Plotly dual throttle/brake subplots |
| `render_constructor_chart()` | 2026 constructor standings horizontal bar |
| `render_sidebar()` | Ferrari Hub with live telemetry cards + Tyre Life |
| `main()` | Page assembly: top bar → timing tower → charts → standings |

---

## Features

### Sidebar — Scuderia Hub
- **Driver Cards**: HAM (#44) and LEC (#16) with live-simulated telemetry
- **Metrics**: Speed (km/h), Throttle %, Brake %, Gear
- **Tyre Life bar**: Colour-coded (green → orange → red) for Hard compound stint
- **Session conditions**: Track temp, air temp, wind

### Top Bar
- **Lap Slider**: Scrub through Lap 1–56, defaults to Lap 51
- **Race progress bar**: Animated fill with lap percentage

### Module A — Timing Tower
- Full 10-driver grid with positions, intervals, points gains, tyre compounds
- Ferrari rows highlighted with red left border + gradient background
- **Tifosi Pin**: Pins HAM & LEC to top of tower when Tifosi Mode is active
- Championship delta panel: shows Ferrari's gap reduction to Mercedes

### Module B — Battle Trace (Plotly)
- Speed vs Distance overlay: HAM (Ferrari Red) vs ANT (Silver dashed)
- Delta shading between traces
- Corner markers for Shanghai (T1, T2, T6, T11, T13, T16)
- Throttle/Brake pedal subplots on second tab
- `add_distance()` alignment (real data) or interpolated mock (same effect)

### Module C — Championship
- Constructor standings horizontal bar chart with team colours
- Driver standings with progress bars, Tifosi pin toggle
- Gap evolution chart across all 56 laps

### Tifosi Mode (sidebar toggle)
- Pins Ferrari to top of timing tower and driver standings
- Activates pulsing red glow on the sidebar border
- Scanline sweep animation across the viewport
- Status indicator in header turns red

---

## Data Flow

```
FastF1 available?
    YES → load_f1_session(2026, 'Shanghai', 'R')
         → get_real_telemetry(session, 'HAM')
         → get_real_telemetry(session, 'ANT')
    NO  → generate_mock_telemetry('HAM', seed=44)
         → generate_mock_telemetry('ANT', seed=12)
         → (all other mock generators)
```

---

## Theming

| Variable | Value | Use |
|---|---|---|
| `FERRARI_RED` | `#EF1A2D` | Primary accent, Ferrari rows, Tifosi glow |
| `CARBON_GREY` | `#343F47` | Secondary surfaces |
| `DARK_BG` | `#0A0A0A` | Page background |
| `CARD_BG` | `#181C23` | Card / panel backgrounds |
| `GOLD` | `#FFD700` | P1 position, current lap marker |
| `GREEN_DELTA` | `#39FF14` | Points gain, throttle trace |

Fonts: **Orbitron** (headers/numbers) · **Rajdhani** (body) · **Share Tech Mono** (telemetry labels)

---

## Extending

- **Add more drivers**: Extend `DRIVER_INFO` dict and `generate_mock_telemetry()`
- **Real pit stop data**: Use `session.laps.pick_driver(code)` + stint logic
- **Sector times**: Add `session.laps[['Sector1Time','Sector2Time','Sector3Time']]`
- **Weather overlay**: `session.weather_data` for track/air temperature traces
