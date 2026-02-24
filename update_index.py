import datetime
import os
import re

atis_text = "WAITING FOR DATA..."
info, qnh, rwy, wind, temp_dew, vis, trans = "-", "----", "--", "--- / --KT", "-- / --", "---", "---"

if os.path.exists("atis_transcribed.txt"):
    with open("atis_transcribed.txt", "r", encoding="utf-8") as f:
        raw = f.read().upper()
        # On nettoie les caractères parasites pour l'analyse
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

    # 1. INFO & RUNWAY
    info = extract_after("INFORMATION", clean_text, is_digit=False) or "-"
    rwy = extract_after("RUNWAY", clean_text, length=5) or "--"
    if len(rwy) > 2: rwy = rwy[:2]

    # 2. QNH (Ancre QNH)
    qnh = extract_after("QNH", clean_text, length=15) or "----"
    if len(qnh) > 4: qnh = qnh[:4]

    # 3. VISIBILITÉ (Ancre CAVOK ou VISIBILITY)
    if "CAVOK" in clean_text:
        vis = "CAVOK"
    else:
        v_match = re.search(r"VISIBILITY\s*(\d+)", clean_text)
        vis = v_match.group(1) + "M" if v_match else "---"

    # 4. VENT (Ancre DEGREES)
    w_match = re.search(r"(\d{3})\s*DEGREES\s*(\d+)", clean_text)
    if w_match:
        wind = f"{w_match.group(1)}° / {w_match.group(2).zfill(2)}KT"

    # 5. TEMP / DEW (Ancres dédiées)
    t_context = re.search(r"TEMPERATURE\s*(.*?)\s*(\d+)", clean_text)
    d_context = re.search(r"DEWPOINT\s*(.*?)\s*(\d+)", clean_text)
    t_val = ("-" if t_context and "MINUS" in t_context.group(1) else "") + (t_context.group(2) if t_context else "--")
    d_val = ("-" if d_context and "MINUS" in d_context.group(1) else "") + (d_context.group(2) if d_context else "--")
    temp_dew = f"{t_val}° / {d_val}°"

    # 6. NIVEAU DE TRANSITION (Ancre TRANSITION)
    trans_match = re.search(r"TRANSITION LEVEL\s*(\d+)", clean_text)
    trans = "FL" + trans_match.group(1) if trans_match else "---"

now = datetime.datetime.now().strftime("%H:%M")

html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EETN ATIS PRO</title>
    <style>
        :root {{ --blue: #00aaff; --bg: #050505; --card: #111; --border: #222; }}
        body {{ font-family: 'Courier New', Courier, monospace; background: var(--bg); color: #ccc; margin: 0; padding: 10px; display: flex; flex-direction: column; align-items: center; text-transform: uppercase; }}
        .header {{ width: 100%; max-width: 600px; border-bottom: 2px solid var(--border); padding: 10px 0; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; width: 100%; max-width: 600px; margin-bottom: 10px; }}
        .card {{ background: var(--card); padding: 12px 5px; border-radius: 4px; text-align: center; border: 1px solid var(--border); }}
        .label {{ font-size: 0.65rem; color: #555; margin-bottom: 4px; font-weight: bold; }}
        .value {{ font-size: 1.5rem; font-weight: bold; color: var(--blue); }}
        .section {{ width: 100%; max-width: 600px; background: var(--card); border: 1px solid var(--border); padding: 15px; margin-bottom: 10px; box-sizing: border-box; }}
        .sec-title {{ color: var(--blue); font-size: 0.75rem; margin-bottom: 10px; border-bottom: 1px solid #222; padding-bottom: 5px; font-weight: bold; }}
        .met-box {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; background: #000; padding: 10px; border: 1px solid #1a1a1a; text-align: center; margin-bottom: 10px; }}
        .raw-text {{ font-size: 0.7rem; color: #444; line-height: 1.3; text-align: justify; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="font-weight: bold;">TALLINN/EETN ATIS</div>
        <div style="color: #444; font-size: 0.75rem;">{now} UTC</div>
    </div>
    <div class="grid">
        <div class="card"><div class="label">INFO</div><div class="value">{info}</div></div>
        <div class="card"><div class="label">RWY</div><div class="value">{rwy}</div></div>
        <div class="card"><div class="label">QNH</div><div class="value">{qnh}</div></div>
    </div>
    <div class="section">
        <div class="sec-title">METEOROLOGICAL DATA</div>
        <div class="met-box">
            <div><span style="color:#444; font-size:0.55rem;">WIND</span><br><span style="color:#eee; font-size:0.9rem;">{wind}</span></div>
            <div><span style="color:#444; font-size:0.55rem;">VIS</span><br><span style="color:#eee; font-size:0.9rem;">{vis}</span></div>
            <div><span style="color:#444; font-size:0.55rem;">T/D</span><br><span style="color:#eee; font-size:0.9rem;">{temp_dew}</span></div>
        </div>
        <div style="font-size: 0.8rem; color: #888;">TRANSITION LEVEL: <span style="color:var(--blue)">{trans}</span></div>
    </div>
    <div class="section">
        <div class="sec-title">RAW DATA ANALYZED</div>
        <div class="raw-text">{atis_text}</div>
    </div>
    <div style="font-size: 0.55rem; color: #222; margin-top: 5px; letter-spacing: 2px;">EETN DIGITAL ATIS MONITOR</div>
</body>
</html>
'''
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
