import datetime
import os
import re

atis_text = "En attente de données..."
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

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

# Découpage du texte en lignes pour une présentation successive
sentences = atis_text.split('.')
clean_sentences = [s.strip() for s in sentences if len(s) > 5]

html_lines = "".join([f'<div class="info-line">✈️ {s}</div>' for s in clean_sentences])

html = f'''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EETN ATIS Dashboard</title>
    <style>
        body {{ font-family: 'Consolas', monospace; background: #050505; color: #00ff00; padding: 20px; display: flex; flex-direction: column; align-items: center; }}
        .header {{ text-align: center; border: 2px solid #00ff00; padding: 10px 40px; margin-bottom: 30px; border-radius: 5px; box-shadow: 0 0 15px rgba(0,255,0,0.2); }}
        .dashboard {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: #111; padding: 15px; border: 1px solid #00ff00; text-align: center; min-width: 120px; }}
        .stat-label {{ font-size: 0.8rem; color: #00ff00; text-transform: uppercase; margin-bottom: 5px; opacity: 0.7; }}
        .stat-value {{ font-size: 2.2rem; font-weight: bold; color: #00ff00; }}
        .container {{ width: 100%; max-width: 800px; }}
        .info-line {{ background: rgba(0,255,0,0.05); border-left: 3px solid #00ff00; margin-bottom: 8px; padding: 12px; font-size: 1.1rem; text-transform: uppercase; }}
        .time {{ color: #006600; font-size: 0.8rem; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1 style="margin:0; font-size: 1.5rem;">EETN ATIS TALLINN</h1>
    </div>

    <div class="dashboard">
        <div class="stat-card">
            <div class="stat-label">INFO</div>
            <div class="stat-value">{info_letter}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">RWY</div>
            <div class="stat-value">{runway}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">QNH</div>
            <div class="stat-value">{qnh}</div>
        </div>
    </div>

    <div class="container">
        {html_lines}
    </div>

    <div class="time">LAST UPDATE: {now} UTC | NO AUDIO RECORDING AVAILABLE</div>
</body>
</html>
'''
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
