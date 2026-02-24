import datetime
import os
import re

# Valeurs par défaut
atis_text = "WAITING FOR DATA..."
info, qnh, rwy, wind, temp_dew, vis, rcc, contamination = "-", "----", "--", "--- / --KT", "-- / --", "---", "-/-/-", "UNKNOWN"

if os.path.exists("atis_transcribed.txt"):
    with open("atis_transcribed.txt", "r", encoding="utf-8") as f:
        raw = f.read().upper()
        # Nettoyage : on force les espaces entre chiffres et lettres
        atis_text = re.sub(r'(\d)([A-Z])', r'\1 \2', raw)
        atis_text = re.sub(r'([A-Z])(\d)', r'\1 \2', atis_text)
        clean_text = atis_text.replace("-", " ").replace(",", " ").replace(".", " ")

    # --- LOGIQUE D'EXTRACTION PAR ANCRES ---

    def extract_after(anchor, text, length=10, is_digit=True):
        match = re.search(f"{anchor}\s*(.{{1,{length}}})", text)
        if match:
            val = match.group(1)
            if is_digit:
                digits = re.sub(r'\D', '', val)
                return digits if digits else None
            return val.strip().split()[0]
        return None

    # 1. INFO, RUNWAY & QNH
    info = extract_after("INFORMATION", clean_text, is_digit=False) or "-"
    rwy = extract_after("RUNWAY", clean_text, length=5) or "--"
    if len(rwy) > 2: rwy = rwy[:2]
    
    qnh = extract_after("QNH", clean_text, length=15) or "----"
    if len(qnh) > 4: qnh = qnh[:4]

    # 2. VISIBILITÉ
    if "CAVOK" in clean_text:
        vis = "CAVOK"
    else:
        v_m = re.search(r"VISIBILITY\s*(\d+)", clean_text)
        vis = v_m.group(1) + "M" if v_m else "---"

    # 3. VENT
    w_m = re.search(r"(\d{3})\s*DEGREES\s*(\d+)", clean_text)
    if w_m:
        wind = f"{w_m.group(1)}° / {w_m.group(2).zfill(2)}KT"

    # 4. TEMP / DEW
    t_c = re.search(r"TEMPERATURE\s*(.*?)\s*(\d+)", clean_text)
    d_c = re.search(r"DEWPOINT\s*(.*?)\s*(\d+)", clean_text)
    t_v = ("-" if t_c and "MINUS" in t_c.group(1) else "") + (t_c.group(2) if t_c else "--")
    d_v = ("-" if d_c and "MINUS" in d_c.group(1) else "") + (d_c.group(2) if d_c else "--")
    temp_dew = f"{t_v}° / {d_v}°"

    # 5. RCC (Runway Condition Code) - COLLECTE ROBUSTE
    # On regarde ce qu'il y a après "CONDITION" ou "CODE"
    rwy_context = ""
    if "CONDITION" in clean_text:
        rwy_context = clean_text.split("CONDITION")[1]
    
    # On cherche tous les chiffres isolés de 0 à 6 dans cette zone
    rcc_matches = re.findall(r'\b([0-6])\b', rwy_context)
    if len(rcc_matches) >= 3:
        rcc = f"{rcc_matches[0]}/{rcc_matches[1]}/{rcc_matches[2]}"
    elif len(rcc_matches) > 0:
        rcc = f"{rcc_matches[0]}/{rcc_matches[0]}/{rcc_matches[0]}"

    # 6. CONTAMINATION
    contaminants = []
    for word in ["WET", "DRY", "WATER", "ICE", "SNOW", "SLUSH"]:
        if word in clean_text:
            contaminants.append(word)
    if contaminants:
        while len(contaminants) < 3:
            contaminants.append(contaminants[0])
        contamination = f"{contaminants[0]}/{contaminants[1]}/{contaminants[2]}"

# --- GÉNÉRATION HTML ---
now = datetime.datetime.now().strftime("%H:%M")

html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EETN ATIS MONITOR</title>
    <style>
        :root {{ --border: #333; --bg: #000; --card: #111; --text-main: #FFF; --text-dim: #666; }}
        body {{ font-family: 'Courier New', Courier, monospace; background: var(--bg); color: var(--text-main); margin: 0; padding: 10px; display: flex; flex-direction: column; align-items: center; text-transform: uppercase; }}
        .header {{ width: 100%; max-width: 600px; border-bottom: 1px solid var(--border); padding: 10px 0; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; width: 100%; max-width: 600px; margin-bottom: 10px; }}
        .card {{ background: var(--card); padding: 12px 5px; border-radius: 2px; text-align: center; border: 1px solid var(--border); }}
        .label {{ font-size: 0.65rem; color: var(--text-dim); margin-bottom: 4px; font-weight: bold; }}
        .value {{ font-size: 1.5rem; font-weight: bold; color: var(--text-main); }}
        .section {{ width: 100%; max-width: 600px; background: var(--card); border: 1px solid var(--border); padding: 15px; margin-bottom: 10px; box-sizing: border-box; }}
        .sec-title {{ color: var(--text-main); font-size: 0.75rem; margin-bottom: 10px; border-bottom: 1px solid var(--border); padding-bottom: 5px; font-weight: bold; }}
        .met-box {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; background: #000; padding: 10px; border: 1px solid var(--border); text-align: center; margin-bottom: 10px; }}
        .rcc-box {{ display: flex; justify-content: space-between; align-items: center; background: #000; padding: 10px; border: 1px solid var(--border); }}
        .raw-text {{ font-size: 0.7rem; color: var(--text-dim); line-height: 1.3; text-align: justify; margin-top:10px; }}
        .footer {{ font-size: 0.55rem; color: #222; margin-top: 5px; letter-spacing: 2px; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="font-weight: bold;">TALLINN/EETN ATIS</div>
        <div style="color: var(--text-dim); font-size: 0.75rem;">{now} UTC</div>
    </div>
    <div class="grid">
        <div class="card"><div class="label">INFO</div><div class="value">{info}</div></div>
        <div class="card"><div class="label">RWY</div><div class="value">{rwy}</div></div>
        <div class="card"><div class="label">QNH</div><div class="value">{qnh}</div></div>
    </div>
    <div class="section">
        <div class="sec-title">METEOROLOGICAL DATA</div>
        <div class="met-box">
            <div><span style="color:var(--text-dim); font-size:0.55rem;">WIND</span><br><span style="font-size:0.9rem;">{wind}</span></div>
            <div><span style="color:var(--text-dim); font-size:0.55rem;">VIS</span><br><span style="font-size:0.9rem;">{vis}</span></div>
            <div><span style="color:var(--text-dim); font-size:0.55rem;">T/D</span><br><span style="font-size:0.9rem;">{temp_dew}</span></div>
        </div>
    </div>
    <div class="section">
        <div class="sec-title">RUNWAY CONDITION</div>
        <div class="rcc-box">
            <div><span style="color:var(--text-dim); font-size:0.6rem; font-weight:bold;">RCC:</span> <span style="font-size:1.1rem;">{rcc}</span></div>
            <div><span style="color:var(--text-dim); font-size:0.6rem; font-weight:bold;">STATE:</span> <span style="font-size:0.8rem;">{contamination}</span></div>
        </div>
    </div>
    <div class="section">
        <div class="sec-title">RAW TEXT ANALYZED</div>
        <div class="raw-text">{atis_text}</div>
    </div>
    <div class="footer">EETN DIGITAL ATIS MONITOR</div>
</body>
</html>
'''
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
