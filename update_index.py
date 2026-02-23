import datetime
import os
import re

atis_text = "En attente de données..."
info_letter = "-"

if os.path.exists("atis_transcribed.txt"):
    with open("atis_transcribed.txt", "r") as f:
        atis_text = f.read()
    
    # Extraction de la lettre d'information (ex: Information Uniform)
    match = re.search(r"Information\s+([a-zA-Z]+)", atis_text, re.IGNORECASE)
    if match:
        info_letter = match.group(1).upper()

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

html = f'''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EETN ATIS - Live AI</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0f0f0f; color: #e0e0e0; padding: 20px; display: flex; flex-direction: column; align-items: center; }}
        .header {{ margin-bottom: 20px; text-align: center; }}
        .badge {{ 
            background: #007bff; color: white; padding: 10px 25px; border-radius: 50px; 
            font-size: 2.5rem; font-weight: bold; margin-bottom: 15px; display: inline-block;
            box-shadow: 0 0 20px rgba(0,123,255,0.4);
        }}
        .box {{ 
            background: #1a1a1a; padding: 30px; border-radius: 15px; border-top: 4px solid #007bff; 
            max-width: 700px; line-height: 1.8; font-size: 1.2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        .airport {{ font-size: 1.8rem; color: #fff; margin-bottom: 5px; font-weight: bold; }}
        .time {{ color: #666; font-size: 0.85rem; margin-top: 25px; border-top: 1px solid #333; padding-top: 15px; text-align: center; }}
        .label {{ color: #007bff; font-size: 0.9rem; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="airport">TALLINN AIRPORT (EETN)</div>
        <div class="label">Current Information</div>
        <div class="badge">{info_letter}</div>
    </div>

    <div class="box">
        <span class="label">AI Transcription (Whisper Medium)</span>
        <p>{atis_text}</p>
        <div class="time">Dernière mise à jour : {now} UTC</div>
    </div>
</body>
</html>
'''

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
