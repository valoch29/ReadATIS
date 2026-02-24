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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EETN ATIS MONITOR</title>
    <style>
        :root {{ --bg: #121212; --card: #1e1e1e; --white: #ffffff; --accent: #b0b0b0; --dim: #555; }}
        body {{ 
            font-family: 'Inter', -apple-system, sans-serif; 
            background: var(--bg); color: var(--accent); 
            margin: 0; padding: 20px; 
            display: flex; flex-direction: column; align-items: center;
            text-transform: uppercase;
        }}
        .container {{ width: 100%; max-width: 500px; }}
        .header {{ 
            display: flex; justify-content: space-between; 
            margin-bottom: 20px; font-size: 0.75rem; color: var(--dim); letter-spacing: 1px;
        }}
        
        /* Dashboard Principal */
        .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 15px; }}
        .card {{ background: var(--card); padding: 20px 10px; border-radius: 8px; text-align: center; }}
        .label {{ font-size: 0.65rem; color: var(--accent); margin-bottom: 8px; display: block; }}
        .value {{ font-size: 1.6rem; font-weight: 800; color: var(--white); }}

        /* Sections Détails */
        .section {{ background: var(--card); border-radius: 8px; padding: 15px; margin-bottom: 10px; }}
        .row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #2a2a2a; }}
        .row:last-child {{ border: none; }}
        .row span {{ font-size: 0.9rem; }}
        .row .val {{ color: var(--white); font-weight: bold; }}

        .raw {{ font-size: 0.7rem; color: #444; line-height: 1.4; margin-top: 20px; text-align: justify; text-transform: none; }}

        /* Mobile */
        @media (max-width: 400px) {{
            .value {{ font-size: 1.3rem; }}
            .row span {{ font-size: 0.8rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span>TALLINN EETN ATIS</span>
            <span>{now} UTC</span>
        </div>

        <div class="grid">
            <div class="card"><span class="label">INFO</span><span class="value">{info}</span></div>
            <div class="card"><span class="label">RWY</span><span class="value">{rwy}</span></div>
            <div class="card"><span class="label">QNH</span><span class="value">{qnh}</span></div>
        </div>

        <div class="section">
            <div class="row"><span>WIND</span><span class="val">{wind}</span></div>
            <div class="row"><span>VISIBILITY</span><span class="val">{vis}</span></div>
            <div class="row"><span>TEMP / DEW</span><span class="val">{temp_dew}</span></div>
        </div>

        <div class="section">
            <div class="row"><span>RUNWAY COND (RCC)</span><span class="val">{rcc}</span></div>
            <div class="row"><span>CONTAMINATION</span><span class="val">{contamination}</span></div>
        </div>

        <div class="raw">
            RAW ANALYZED: {atis_text}
        </div>
    </div>
</body>
</html>
'''
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
