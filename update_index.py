import datetime
import os
import re

atis_text = "WAITING FOR DATA..."
info, qnh, rwy, wind, temp_dew = "-", "----", "--", "--- / --KT", "-- / --"

if os.path.exists("atis_transcribed.txt"):
    with open("atis_transcribed.txt", "r", encoding="utf-8") as f:
        # 1. On récupère le texte et on force les espaces entre chiffres et lettres
        raw = f.read().upper()
        atis_text = re.sub(r'(\d)([A-Z])', r'\1 \2', raw)
        atis_text = re.sub(r'([A-Z])(\d)', r'\1 \2', atis_text)

    # 2. Nettoyage spécifique pour les badges (on enlève tirets/virgules)
    search_text = re.sub(r'(\d)[-,\s]+(?=\d)', r'\1', atis_text)

    # 3. Extraction Badges (Regex plus souple)
    def get_match(pattern, text):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).upper() if m else None

    info = get_match(r"INFORMATION\s+([A-Z]+)", search_text) or "-"
    qnh = get_match(r"QNH\s*(\d{4})", search_text) or "----"
    rwy = get_match(r"RUNWAY\s*(\d{2})", search_text) or "--"
    
    # 4. Extraction Vent (cherche "XXX DEGREES X KNOTS" ou juste "XXX/XX")
    w_m = re.search(r"(\d{3})\s*(?:DEGREES)?\s*(\d+)\s*KNOTS", search_text)
    if w_m:
        wind = f"{w_m.group(1)}° / {w_m.group(2).zfill(2)}KT"
    
    # 5. Extraction Temp/Dew (plus robuste aux mots collés)
    t_m = re.search(r"TEMPERATURE\s*(?:MINUS\s*)?(\d+)", search_text)
    d_m = re.search(r"DEWPOINT\s*(?:MINUS\s*)?(\d+)", search_text)
    if t_m and d_m:
        t_val = t_m.group(1)
        d_val = d_m.group(1)
        # Vérifie si "MINUS" est présent avant le chiffre
        t_prefix = "-" if "MINUS" in atis_text.split("TEMPERATURE")[1].split("DEWPOINT")[0] else ""
        d_prefix = "-" if "MINUS" in atis_text.split("DEWPOINT")[1] else ""
        temp_dew = f"{t_prefix}{t_val}° / {d_prefix}{d_val}°"

# 6. Découpage et Tri
sentences = [s.strip() for s in atis_text.replace('.', ',').split(',') if len(s.strip()) > 5]
unique_sentences = []
for s in sentences:
    if s not in unique_sentences: unique_sentences.append(s)

rwy_data = [s for s in unique_sentences if any(x in s for x in ["CONDITION", "TOUCHDOWN", "MIDPOINT", "WET", "STOP-END", "IN USE"])]
met_data = [s for s in unique_sentences if any(x in s for x in ["WIND", "CAVOK", "TEMPERATURE", "NOSIG", "DEWPOINT", "DEGREES"])]

now = datetime.datetime.now().strftime("%H:%M")

html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EETN ATIS PRO</title>
    <style>
        :root {{ --blue: #00aaff; --bg: #080808; --card: #121212; --border: #222; }}
        body {{ font-family: 'Courier New', Courier, monospace; background: var(--bg); color: #ccc; margin: 0; padding: 15px; display: flex; flex-direction: column; align-items: center; text-transform: uppercase; }}
        .header {{ width: 100%; max-width: 600px; border-bottom: 2px solid var(--border); padding-bottom: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; width: 100%; max-width: 600px; margin-bottom: 15px; }}
        .card {{ background: var(--card); padding: 15px 5px; border-radius: 4px; text-align: center; border: 1px solid var(--border); }}
        .label {{ font-size: 0.7rem; color: #555; margin-bottom: 5px; font-weight: bold; }}
        .value {{ font-size: 1.6rem; font-weight: bold; color: var(--blue); }}
        .section {{ width: 100%; max-width: 600px; background: var(--card); border: 1px solid var(--border); padding: 15px; margin-bottom: 15px; box-sizing: border-box; }}
        .sec-title {{ color: var(--blue); font-size: 0.8rem; margin-bottom: 12px; border-bottom: 1px solid #222; padding-bottom: 5px; font-weight: bold; }}
        .met-box {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px; background: #000; padding: 10px; border: 1px solid #1a1a1a; }}
        .item {{ font-size: 0.85rem; line-height: 1.4; color: #999; margin-bottom: 8px; border-left: 3px solid #222; padding-left: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <div style="font-weight: bold;">TALLINN/EETN ATIS</div>
        <div style="color: #444; font-size: 0.8rem;">{now} UTC</div>
    </div>
    <div class="grid">
        <div class="card"><div class="label">INFO</div><div class="value">{info}</div></div>
        <div class="card"><div class="label">RWY</div><div class="value">{rwy}</div></div>
        <div class="card"><div class="label">QNH</div><div class="value">{qnh}</div></div>
    </div>
    <div class="section">
        <div class="sec-title">METEOROLOGICAL DATA</div>
        <div class="met-box">
            <div><span style="color:#444; font-size:0.6rem;">WIND</span><br>{wind}</div>
            <div><span style="color:#444; font-size:0.6rem;">T / D</span><br>{temp_dew}</div>
        </div>
        {"".join([f'<div class="item">{s}</div>' for s in met_data if "DEGREES" not in s])}
    </div>
    <div class="section">
        <div class="sec-title">RUNWAY STATUS</div>
        {"".join([f'<div class="item">{s}</div>' for s in rwy_data])}
    </div>
    <div style="font-size: 0.6rem; color: #222; margin-top: 10px;">DATALINK ATIS MONITOR</div>
</body>
</html>
'''
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
