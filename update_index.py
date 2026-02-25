import datetime
import os
import re

# Valeurs par défaut
info, qnh, rwy, wind, temp_dew, vis, rcc, contamination = "-", "----", "--", "--- / --KT", "-- / --", "---", "-/-/-", "UNKNOWN"

if os.path.exists("atis_transcribed.txt"):
    with open("atis_transcribed.txt", "r", encoding="utf-8") as f:
        clean_text = f.read().upper()

    # --- EXTRACTION ---
    # Info, QNH, Runway
    m_i = re.search(r"INFORMATION\s+([A-Z])", clean_text)
    if m_i: info = m_i.group(1)
    
    m_q = re.search(r"QNH\s*(\d{4})", clean_text)
    if m_q: qnh = m_q.group(1)
    
    m_r = re.search(r"RUNWAY\s*(\d{2})", clean_text)
    if m_r: rwy = m_r.group(1)

    # Vent (XXX DEGREES XX KNOTS)
    m_w = re.search(r"(\d{3})\s*DEGREES\s*(\d+)\s*KNOTS", clean_text)
    if m_w: wind = f"{m_w.group(1)}° / {m_w.group(2).zfill(2)}KT"

    # Visibilité
    vis = "CAVOK" if "CAVOK" in clean_text else "---"

    # Temp / Dewpoint
    def get_t(anchor, text):
        parts = text.split(anchor)
        if len(parts) > 1:
            m = re.search(r"(MINUS\s+)?(\d+)", parts[1])
            if m: return ("-" if m.group(1) else "") + m.group(2)
        return "--"
    temp_dew = f"{get_t('TEMPERATURE', clean_text)}° / {get_t('DEWPOINT', clean_text)}°"

    # RCC (Piste)
    r1 = re.search(r"TOUCHDOWN\s*.*?(\d)", clean_text)
    r2 = re.search(r"MIDPOINT\s*.*?(\d)", clean_text)
    r3 = re.search(r"STOP END\s*.*?(\d)", clean_text)
    if r1: rcc = f"{r1.group(1)}/{r2.group(1) if r2 else r1.group(1)}/{r3.group(1) if r3 else r1.group(1)}"

    # Contamination
    states = [s for s in ["WET", "DRY", "WATER", "ICE", "SNOW", "SLUSH", "FROST"] if s in clean_text]
    if states: contamination = "/".join((states * 3)[:3])

now = datetime.datetime.now().strftime("%H:%M")

# --- HTML (Design Gris/Blanc) ---
html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EETN ATIS</title>
    <style>
        :root {{ --bg: #121212; --card: #1a1a1a; --text: #ffffff; --dim: #777; }}
        body {{ font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 15px; display: flex; flex-direction: column; align-items: center; text-transform: uppercase; }}
        .container {{ width: 100%; max-width: 480px; }}
        .header {{ display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--dim); margin: 15px 0; font-weight: bold; letter-spacing: 1px; }}
        .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 15px; }}
        .card {{ background: var(--card); padding: 18px 5px; border-radius: 10px; text-align: center; border: 1px solid #222; }}
        .label {{ font-size: 0.6rem; color: var(--dim); margin-bottom: 5px; display: block; }}
        .value {{ font-size: 1.6rem; font-weight: 800; }}
        .sec {{ background: var(--card); border-radius: 10px; padding: 5px 20px; margin-bottom: 10px; border: 1px solid #222; }}
        .row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #252525; }}
        .row:last-child {{ border: none; }}
        .row span:first-child {{ color: var(--dim); font-size: 0.75rem; font-weight: bold; }}
        .raw {{ font-size: 0.65rem; color: #333; margin-top: 25px; text-transform: none; text-align: justify; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><span>TALLINN EETN ATIS</span><span>{now} UTC</span></div>
        <div class="grid">
            <div class="card"><span class="label">INFO</span><span class="value">{info}</span></div>
            <div class="card"><span class="label">RWY</span><span class="value">{rwy}</span></div>
            <div class="card"><span class="label">QNH</span><span class="value">{qnh}</span></div>
        </div>
        <div class="sec">
            <div class="row"><span>WIND</span><span>{wind}</span></div>
            <div class="row"><span>VISIBILITY</span><span>{vis}</span></div>
            <div class="row"><span>TEMP / DEW</span><span>{temp_dew}</span></div>
        </div>
        <div class="sec">
            <div class="row"><span>RWY CONDITION</span><span>{rcc}</span></div>
            <div class="row"><span>SURFACE</span><span>{contamination}</span></div>
        </div>
        <div class="raw">ANALYZED: {clean_text}</div>
    </div>
</body>
</html>
'''
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
