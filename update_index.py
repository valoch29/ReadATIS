import datetime
import os
import re

atis_text = "WAITING FOR DATA..."
info, qnh, rwy, wind, temp_dew = "-", "----", "--", "--- / --KT", "-- / --"

if os.path.exists("atis_transcribed.txt"):
    with open("atis_transcribed.txt", "r", encoding="utf-8") as f:
        atis_text = f.read().upper() # Tout en majuscules pour le look Pro
    
    # Nettoyage pour les badges
    search_text = re.sub(r'(\d)[-,\s]+(?=\d)', r'\1', atis_text)

    # Extraction
    def get_match(pattern, text):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).upper() if m else None

    info = get_match(r"INFORMATION\s+([A-Z]+)", search_text) or "-"
    qnh = get_match(r"QNH\s*(\d{4})", search_text) or "----"
    rwy = get_match(r"RUNWAY\s*(\d{2})", search_text) or "--"
    
    # Vent et Temp
    w_m = re.search(r"(\d{3})\s*DEGREES\s*(\d+)\s*KNOTS", search_text)
    if w_m: wind = f"{w_m.group(1)} / {w_m.group(2).zfill(2)}KT"
    
    t_m = re.search(r"TEMPERATURE\s*(?:MINUS\s*)?(\d+)", search_text)
    d_m = re.search(r"DEWPOINT\s*(?:MINUS\s*)?(\d+)", search_text)
    if t_m and d_m:
        t = f"-{t_m.group(1)}" if "MINUS" in atis_text.split("TEMPERATURE")[1] else t_m.group(1)
        d = f"-{d_m.group(1)}" if "MINUS" in atis_text.split("DEWPOINT")[1] else d_m.group(1)
        temp_dew = f"{t} / {d}"

# Tri par blocs logiques
sentences = [s.strip() for s in atis_text.split(',') if len(s.strip()) > 5]
rwy_data = [s for s in sentences if any(x in s for x in ["RUNWAY", "CONDITION", "WET", "CODE", "TOUCHDOWN"])]
met_data = [s for s in sentences if any(x in s for x in ["WIND", "CAVOK", "TEMPERATURE", "NOSIG", "DEWPOINT", "VISIBILITY"])]

now = datetime.datetime.now().strftime("%H:%M")

html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EETN ATIS PRO</title>
    <style>
        :root {{ --blue: #00aaff; --bg: #080808; --card: #151515; --border: #252525; }}
        body {{ font-family: 'Courier New', Courier, monospace; background: var(--bg); color: #ddd; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; text-transform: uppercase; }}
        .header {{ width: 100%; max-width: 650px; border-bottom: 2px solid var(--border); padding-bottom: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; width: 100%; max-width: 650px; margin-bottom: 20px; }}
        .card {{ background: var(--card); padding: 15px; border-radius: 4px; text-align: center; border: 1px solid var(--border); }}
        .label {{ font-size: 0.75rem; color: #777; margin-bottom: 5px; }}
        .value {{ font-size: 1.8rem; font-weight: bold; color: var(--blue); }}
        .container {{ width: 100%; max-width: 650px; }}
        .section {{ background: var(--card); border: 1px solid var(--border); padding: 15px; margin-bottom: 15px; border-radius: 4px; }}
        .sec-title {{ color: var(--blue); font-size: 0.8rem; margin-bottom: 10px; border-bottom: 1px solid var(--border); padding-bottom: 5px; }}
        .item {{ font-size: 0.9rem; line-height: 1.5; color: #aaa; margin-bottom: 8px; border-left: 2px solid #333; padding-left: 10px; }}
        .footer {{ margin-top: 30px; font-size: 0.7rem; color: #444; letter-spacing: 1px; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="font-size: 1.2rem; font-weight: bold;">TALLINN / EETN ATIS</div>
        <div style="color: #666;">{now} UTC</div>
    </div>

    <div class="grid">
        <div class="card"><div class="label">INFO</div><div class="value">{info}</div></div>
        <div class="card"><div class="label">RWY</div><div class="value">{rwy}</div></div>
        <div class="card"><div class="label">QNH</div><div class="value">{qnh}</div></div>
    </div>

    <div class="container">
        <div class="section">
            <div class="sec-title">METEOROLOGICAL DATA</div>
            <div style="display:flex; justify-content:space-around; margin-bottom:15px; background:#000; padding:10px;">
                <div><span style="color:#555; font-size:0.7rem;">WIND:</span> {wind}</div>
                <div><span style="color:#555; font-size:0.7rem;">T/D:</span> {temp_dew}</div>
            </div>
            {"".join([f'<div class="item">{s}</div>' for s in met_data if "WIND" not in s])}
        </div>

        <div class="section">
            <div class="sec-title">RUNWAY STATUS & FACILITIES</div>
            {"".join([f'<div class="item">{s}</div>' for s in rwy_data])}
        </div>
    </div>

    <div class="footer">DATALINK ATIS SOURCE • TALLINN ESTONIA</div>
</body>
</html>
'''
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
