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

# Découpage propre par phrases pour présentation successive
sentences = re.split(r'\.|\bout\b', atis_text, flags=re.IGNORECASE)
clean_sentences = [s.strip().upper() for s in sentences if len(s) > 8]

html_lines = "".join([f'<div class="info-line"><span class="bullet"></span> {s}</div>' for s in clean_sentences])

html = f'''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EETN ATIS Dashboard</title>
    <style>
        :root {{
            --bg-color: #121212;
            --card-bg: #1e1e1e;
            --text-white: #ffffff;
            --text-dim: #b0b0b0;
            --accent-blue: #3498db;
        }}
        body {{ 
            font-family: 'Inter', -apple-system, sans-serif; 
            background: var(--bg-color); 
            color: var(--text-dim); 
            margin: 0; padding: 15px;
            display: flex; flex-direction: column; align-items: center;
        }}
        .header {{ width: 100%; max-width: 600px; margin: 20px 0; text-align: center; }}
        .header h1 {{ font-size: 1rem; color: var(--accent-blue); letter-spacing: 3px; margin: 0; font-weight: 700; }}
        
        .dashboard {{ 
            display: grid; 
            grid-template-columns: repeat(3, 1fr); 
            gap: 12px; width: 100%; max-width: 600px; margin-bottom: 25px; 
        }}
        .stat-card {{ 
            background: var(--card-bg); padding: 20px 10px; 
            border-radius: 10px; border: 1px solid #2a2a2a; text-align: center;
        }}
        .stat-label {{ font-size: 0.7rem; color: var(--text-dim); text-transform: uppercase; margin-bottom: 8px; font-weight: 600; letter-spacing: 1px; }}
        .stat-value {{ font-size: 1.8rem; font-weight: 800; color: var(--text-white); }}

        .container {{ width: 100%; max-width: 600px; display: flex; flex-direction: column; gap: 8px; }}
        .info-line {{ 
            background: var(--card-bg); padding: 14px 18px; 
            border-radius: 6px; font-size: 0.95rem; line-height: 1.4;
            color: var(--text-dim); border-left: 3px solid #333;
        }}
        .footer {{ margin-top: 30px; font-size: 0.75rem; color: #555; width: 100%; max-width: 600px; text-align: center; }}

        /* RESPONSIVE DESIGN */
        @media (max-width: 480px) {{
            .dashboard {{ grid-template-columns: 1fr; }}
            .stat-card {{ padding: 12px; display: flex; justify-content: space-between; align-items: center; padding: 15px 25px; }}
            .stat-label {{ margin-bottom: 0; }}
            .stat-value {{ font-size: 1.4rem; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>TALLINN / EETN ATIS</h1>
    </div>

    <div class="dashboard">
        <div class="stat-card">
            <div class="stat-label">Information</div>
            <div class="stat-value">{info_letter}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Runway</div>
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

    <div class="footer">
        Dernière mise à jour : {now} UTC<br>
        AI Transcription Service
    </div>
</body>
</html>
'''
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
