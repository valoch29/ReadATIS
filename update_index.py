import datetime
import os
import re

atis_text = "Chargement..."
info_letter = "-"
qnh = "----"
runway = "--"

if os.path.exists("atis_transcribed.txt"):
    with open("atis_transcribed.txt", "r", encoding="utf-8") as f:
        atis_text = f.read()
    
    letter_match = re.search(r"Information,?\s+([a-zA-Z]+)", atis_text, re.IGNORECASE)
    if letter_match: info_letter = letter_match.group(1).upper()

    qnh_match = re.search(r"QNH,?\s*(\d{4})", atis_text, re.IGNORECASE)
    if qnh_match: qnh = qnh_match.group(1)

    rwy_match = re.search(r"Runway\s*(\d{2})", atis_text, re.IGNORECASE)
    if rwy_match: runway = rwy_match.group(1)

now = datetime.datetime.now().strftime("%H:%M")
sentences = [s.strip() for s in atis_text.split('.') if len(s.strip()) > 5]
html_lines = "".join([f'<div class="line">✈️ {s}.</div>' for s in sentences])

html = f'''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EETN ATIS</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #000; color: #fff; margin: 0; padding: 15px; display: flex; flex-direction: column; align-items: center; }}
        .header {{ width: 100%; max-width: 500px; text-align: center; border-bottom: 1px solid #222; padding: 10px 0; margin-bottom: 15px; color:#888; font-weight:bold; letter-spacing:2px; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; width: 100%; max-width: 500px; margin-bottom: 20px; }}
        .card {{ background: #111; padding: 15px 5px; border-radius: 12px; text-align: center; border: 1px solid #333; }}
        .label {{ font-size: 0.7rem; color: #007bff; font-weight: bold; margin-bottom: 5px; }}
        .val {{ font-size: 1.6rem; font-weight: bold; }}
        .content {{ width: 100%; max-width: 500px; }}
        .line {{ background: #161616; margin-bottom: 8px; padding: 12px; border-radius: 8px; font-size: 1rem; line-height: 1.4; border-left: 4px solid #007bff; text-transform: uppercase; }}
        .footer {{ margin-top: 20px; font-size: 0.8rem; color: #444; }}
    </style>
</head>
<body>
    <div class="header">TALLINN EETN ATIS</div>
    <div class="grid">
        <div class="card"><div class="label">INFO</div><div class="val">{info_letter}</div></div>
        <div class="card"><div class="label">RWY</div><div class="val">{runway}</div></div>
        <div class="card"><div class="label">QNH</div><div class="val">{qnh}</div></div>
    </div>
    <div class="content">{html_lines}</div>
    <div class="footer">MAJ : {now} UTC</div>
</body>
</html>
'''
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
