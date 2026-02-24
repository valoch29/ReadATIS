import datetime
import os
import re

atis_text = "Waiting for data..."
info, qnh, rwy, wind, temp_dew = "-", "----", "--", "--- / --KT", "-- / --"

if os.path.exists("atis_transcribed.txt"):
    with open("atis_transcribed.txt", "r", encoding="utf-8") as f:
        atis_text = f.read()
    
    # Nettoyage profond pour la recherche : on enlève les tirets et virgules dans les chiffres
    search_text = re.sub(r'(\d)[-,\s]+(?=\d)', r'\1', atis_text)

    # Extraction des données
    def get_match(pattern, text):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).upper() if m else None

    info = get_match(r"Information\s+([a-zA-Z]+)", search_text) or "-"
    qnh = get_match(r"QNH\s*(\d{4})", search_text) or "----"
    rwy = get_match(r"Runway\s*(\d{2})", search_text) or "--"
    
    # Vent et Temp
    w_m = re.search(r"(\d{3})\s*degrees\s*(\d+)\s*knots", search_text, re.IGNORECASE)
    if w_m: wind = f"{w_m.group(1)} / {w_m.group(2).zfill(2)}KT"
    
    t_m = re.search(r"temperature\s*(?:minus\s*)?(\d+)", search_text, re.IGNORECASE)
    d_m = re.search(r"dewpoint\s*(?:minus\s*)?(\d+)", search_text, re.IGNORECASE)
    if t_m and d_m:
        t = f"-{t_m.group(1)}" if "minus" in atis_text.lower().split("temperature")[1] else t_m.group(1)
        d = f"-{d_m.group(1)}" if "minus" in atis_text.lower().split("dewpoint")[1] else d_m.group(1)
        temp_dew = f"{t} / {d}"

# Séparation par catégories
lines = [s.strip().upper() for s in atis_text.split('.') if len(s.strip()) > 5]
rwy_lines = [l for l in lines if any(x in l for x in ["RUNWAY", "CONDITION", "WET", "CODE"])]
met_lines = [l for l in lines if any(x in l for x in ["WIND", "CAVOK", "TEMPERATURE", "NOSIG", "DEWPOINT"])]
misc_lines = [l for l in lines if l not in rwy_lines and l not in met_lines]

def format_section(title, content):
    if not content: return ""
    items = "".join([f'<div class="item">{item}.</div>' for item in content])
    return f'<div class="section"><div class="sec-title">{title}</div>{items}</div>'

now = datetime.datetime.now().strftime("%H:%M")

html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EETN ATIS</title>
    <style>
        :root {{ --blue: #007aff; --bg: #000; --card: #111; --text: #eee; }}
        body {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; background: var(--bg); color: var(--text); margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }}
        .header {{ width: 100%; max-width: 600px; border-bottom: 1px solid #222; padding-bottom: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; width: 100%; max-width: 600px; margin-bottom: 20px; }}
        .card {{ background: var(--card); padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #222; }}
        .label {{ font-size: 0.7rem; color: #666; font-weight: bold; margin-bottom: 5px; }}
        .value {{ font-size: 1.6rem; font-weight: bold; color: var(--blue); }}
        .container {{ width: 100%; max-width: 600px; }}
        .section {{ margin-bottom: 25px; }}
        .sec-title {{ font-size: 0.8rem; color: #444; border-bottom: 1px solid #222; padding-bottom: 5px; margin-bottom: 10px; font-weight: bold; }}
        .item {{ font-size: 0.95rem; line-height: 1.6; color: #bbb; margin-bottom: 5px; }}
        .footer {{ margin-top: 30px; font-size: 0.7rem; color: #333; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="font-weight:bold; letter-spacing:1px;">EETN / TALLINN ATIS</div>
        <div style="font-size:0.8rem; color:#666;">{now} UTC</div>
    </div>
    <div class="grid">
        <div class="card"><div class="label">INFO</div><div class="value">{info}</div></div>
        <div class="card"><div class="label">RWY</div><div class="value">{rwy}</div></div>
        <div class="card"><div class="label">QNH</div><div class="value">{qnh}</div></div>
    </div>
    <div class="container">
        <div class="section">
            <div class="sec-title">METEOROLOGICAL DATA</div>
            <div class="item">WIND: {wind}</div>
            <div class="item">TEMP/DEW: {temp_dew}</div>
            {"".join([f'<div class="item">{l}.</div>' for l in met_lines])}
        </div>
        {format_section("RUNWAY STATUS", rwy_lines)}
        {format_section("OTHER INFORMATION", misc_lines)}
    </div>
    <div class="footer">TERMINAL INFORMATION SERVICE • AUTOMATED DATA</div>
</body>
</html>
'''
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
