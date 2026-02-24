import datetime
import os
import re

info, qnh, rwy, wind, temp_dew, vis, rcc, contamination = "-", "----", "--", "--- / --KT", "-- / --", "---", "-/-/-", "UNKNOWN"

if os.path.exists("atis_transcribed.txt"):
    with open("atis_transcribed.txt", "r", encoding="utf-8") as f:
        raw = f.read().upper()
        
        # --- DICTIONNAIRE DE CORRECTION PHONÉTIQUE (Anticipation) ---
        corrections = {
            "WEST": "WET", "WASTE": "WET", "WAIT": "WET",
            "GULF": "GOLF", "GOLD": "GOLF",
            "CABLE K": "CAVOK", "CABO K": "CAVOK", "COVER K": "CAVOK",
            "HECTOPASCALSS": "HECTOPASCALS", "HP": "HECTOPASCALS",
            "NO SEEK": "NOSIG", "NO SEAT": "NOSIG", "NO SICK": "NOSIG",
            "DUE POINT": "DEWPOINT", "DO POINT": "DEWPOINT",
            "TOP END": "STOP END", "STEP END": "STOP END",
            "TOUCHSTONE": "TOUCHDOWN", "TOUCH DOWN": "TOUCHDOWN",
            "MID POINT": "MIDPOINT", "MEET POINT": "MIDPOINT"
        }
        for wrong, right in corrections.items():
            raw = raw.replace(wrong, right)
            
        # Nettoyage des chiffres collés et caractères
        atis_text = re.sub(r'(\d)([A-Z])', r'\1 \2', raw)
        atis_text = re.sub(r'([A-Z])(\d)', r'\1 \2', atis_text)
        clean_text = atis_text.replace("-", " ").replace(",", " ").replace(".", " ")

    # --- FONCTIONS D'EXTRACTION RÉSILIENNES ---

    def extract_after(anchors, text, length=20, is_digit=True):
        """Cherche plusieurs variantes d'une ancre et extrait la valeur suivante."""
        for anchor in anchors:
            match = re.search(f"{anchor}\s*(.{{1,{length}}})", text)
            if match:
                val = match.group(1)
                if is_digit:
                    digits = re.sub(r'\D', '', val)
                    return digits if digits else None
                return val.strip().split()[0]
        return None

    # 1. BADGES (multi-ancres pour parer aux oublis)
    info = extract_after(["INFORMATION", "INFO"], clean_text, is_digit=False) or "-"
    rwy = extract_after(["RUNWAY", "RWY"], clean_text, length=5) or "--"
    if len(rwy) > 2: rwy = rwy[:2]
    
    qnh = extract_after(["QNH", "ALTIMETER"], clean_text, length=15) or "----"
    if len(qnh) > 4: qnh = qnh[:4]

    # 2. VISIBILITÉ
    if any(x in clean_text for x in ["CAVOK", "CAV OK"]):
        vis = "CAVOK"
    else:
        v_m = re.search(r"(?:VISIBILITY|VIS)\s*(\d+)", clean_text)
        vis = v_m.group(1) + "M" if v_m else "---"

    # 3. VENT (Cherche XXX DEGREES ou XXX AT XX)
    w_m = re.search(r"(\d{3})\s*(?:DEGREES|AT)\s*(\d+)", clean_text)
    if w_m:
        wind = f"{w_m.group(1)}° / {w_m.group(2).zfill(2)}KT"

    # 4. TEMP / DEWPOINT
    def get_temp(anchor, text):
        part = text.split(anchor)
        if len(part) > 1:
            val_match = re.search(r"(MINUS\s+)?(\d+)", part[1])
            if val_match:
                prefix = "-" if val_match.group(1) else ""
                return prefix + val_match.group(2)
        return "--"

    t_val = get_temp("TEMPERATURE", clean_text)
    d_val = get_temp("DEWPOINT", clean_text)
    temp_dew = f"{t_val}° / {d_val}°"

    # 5. RCC (Logique par segment isolés)
    def find_rcc(segment_name, text):
        match = re.search(f"{segment_name}\s*.*?(\d)", text)
        return match.group(1) if match else None

    r1 = find_rcc("TOUCHDOWN", clean_text)
    r2 = find_rcc("MIDPOINT", clean_text)
    r3 = find_rcc("STOP END", clean_text)
    
    if r1 and r2 and r3:
        rcc = f"{r1}/{r2}/{r3}"
    elif r1: rcc = f"{r1}/{r1}/{r1}" # Fallback si un seul chiffre trouvé

    # 6. CONTAMINATION
    states = []
    for s in ["WET", "DRY", "WATER", "ICE", "SNOW", "SLUSH"]:
        if s in clean_text: states.append(s)
    if states:
        while len(states) < 3: states.append(states[0])
        contamination = f"{states[0]}/{states[1]}/{states[2]}"

now = datetime.datetime.now().strftime("%H:%M")

html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EETN ATIS MONITOR</title>
    <style>
        :root {{ --border: #222; --bg: #000; --text: #EEE; --dim: #555; }}
        body {{ font-family: 'Courier New', monospace; background: var(--bg); color: var(--text); margin: 0; padding: 15px; display: flex; flex-direction: column; align-items: center; text-transform: uppercase; }}
        .header {{ width: 100%; max-width: 600px; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; width: 100%; max-width: 600px; margin-bottom: 10px; }}
        .card {{ background: #0A0A0A; padding: 15px 5px; text-align: center; border: 1px solid var(--border); }}
        .label {{ font-size: 0.65rem; color: var(--dim); margin-bottom: 5px; font-weight: bold; }}
        .value {{ font-size: 1.6rem; font-weight: bold; }}
        .section {{ width: 100%; max-width: 600px; background: #0A0A0A; border: 1px solid var(--border); padding: 15px; margin-bottom: 10px; box-sizing: border-box; }}
        .sec-title {{ font-size: 0.75rem; color: var(--dim); margin-bottom: 10px; border-bottom: 1px solid var(--border); padding-bottom: 5px; }}
        .met-box {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; text-align: center; background: #000; padding: 12px; border: 1px solid var(--border); }}
        .rcc-box {{ display: flex; justify-content: space-between; padding: 10px; background: #000; border: 1px solid var(--border); }}
        .raw {{ font-size: 0.65rem; color: #333; line-height: 1.3; text-align: justify; margin-top: 5px; font-style: italic; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="font-weight: bold;">EETN DIGITAL MONITOR</div>
        <div style="color: var(--dim); font-size: 0.7rem;">{now} UTC</div>
    </div>
    <div class="grid">
        <div class="card"><div class="label">INFO</div><div class="value">{info}</div></div>
        <div class="card"><div class="label">RWY</div><div class="value">{rwy}</div></div>
        <div class="card"><div class="label">QNH</div><div class="value">{qnh}</div></div>
    </div>
    <div class="section">
        <div class="sec-title">METEOROLOGICAL DATA</div>
        <div class="met-box">
            <div><span class="label">WIND</span><br>{wind}</div>
            <div><span class="label">VIS</span><br>{vis}</div>
            <div><span class="label">T/D</span><br>{temp_dew}</div>
        </div>
    </div>
    <div class="section">
        <div class="sec-title">RUNWAY CONDITION</div>
        <div class="rcc-box">
            <div><span class="label">RCC:</span> {rcc}</div>
            <div><span class="label">STATE:</span> {contamination}</div>
        </div>
    </div>
    <div class="section" style="border:none; background:transparent;">
        <div class="sec-title">RAW ANALYZED</div>
        <div class="raw">{atis_text}</div>
    </div>
</body>
</html>
'''
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
