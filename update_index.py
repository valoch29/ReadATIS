import datetime
import os
import re

atis_text = "En attente de mise à jour..."
info_letter, qnh, runway, wind, temp_dew = "-", "----", "--", "---° / --KT", "--° / --°"

if os.path.exists("atis_transcribed.txt"):
    with open("atis_transcribed.txt", "r", encoding="utf-8") as f:
        atis_text = f.read()
    
    # Nettoyage temporaire pour faciliter la recherche Regex
    clean = atis_text.replace(",", "")

    # 1. Extraction Lettre
    m = re.search(r"Information\s+([a-zA-Z]+)", clean, re.IGNORECASE)
    if m: info_letter = m.group(1).upper()

    # 2. Extraction QNH
    m = re.search(r"QNH\s*(\d{4})", clean, re.IGNORECASE)
    if m: qnh = m.group(1)

    # 3. Extraction Piste
    m = re.search(r"Runway\s*(\d{2})", clean, re.IGNORECASE)
    if m: runway = m.group(1)

    # 4. Extraction Vent
    m = re.search(r"(\d{3})\s*degrees\s*(\d+)\s*knots", clean, re.IGNORECASE)
    if m: wind = f"{m.group(1)}° / {m.group(2).zfill(2)}KT"

    # 5. Extraction Température / Dewpoint
    t_match = re.search(r"temperature\s*(?:minus\s*)?(\d+)", clean, re.IGNORECASE)
    d_match = re.search(r"dewpoint\s*(?:minus\s*)?(\d+)", clean, re.IGNORECASE)
    if t_match and d_match:
        t_val = f"-{t_match.group(1)}" if "minus" in atis_text.lower().split("temperature")[1] else t_match.group(1)
        d_val = f"-{d_match.group(1)}" if "minus" in atis_text.lower().split("dewpoint")[1] else d_match.group(1)
        temp_dew = f"{t_val}° / {d_val}°"

now = datetime.datetime.now().strftime("%H:%M")
sentences = [s.strip() for s in atis_text.split('.') if len(s.strip()) > 5]
html_lines = "".join([f'<div class="line"><span>•</span> {s}.</div>' for s in sentences])

html = f'''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EETN ATIS</title>
    <style>
        :root {{ --neon: #00d4ff; --bg: #050505; --card: #121212; }}
        body {{ font-family: 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: #eee; margin: 0; padding: 15px; display: flex; flex-direction: column; align-items: center; }}
        .header {{ width: 100%; max-width: 600px; display: flex; justify-content: space-between; margin: 10px 0 20px 0; border-left: 4px solid var(--neon); padding-left: 15px; }}
        .airport-id {{ font-size: 1.4rem; font-weight: 800; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; width: 100%; max-width: 600px; margin-bottom: 10px; }}
        .card {{ background: var(--card); padding: 20px 10px; border-radius: 12px; text-align: center; border: 1px solid #222; }}
        .label {{ font-size: 0.65rem; color: var(--neon); font-weight: 700; text-transform: uppercase; margin-bottom: 8px; }}
        .value {{ font-size: 1.8rem; font-weight: 700; font-family: monospace; }}
        .sec-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; width: 100%; max-width: 600px; margin-bottom: 20px; }}
        .small-card {{ background: var(--card); padding: 15px; border-radius: 12px; border: 1px solid #222; display: flex; justify-content: space-between; align-items: center; font-weight: bold; font-size: 0.9rem; }}
        .content {{ width: 100%; max-width: 600px; background: #0a0a0a; border-radius: 16px; border: 1px solid #1a1a1a; }}
        .line {{ padding: 15px; font-size: 0.95rem; line-height: 1.5; color: #bbb; border-bottom: 1px solid #1a1a1a; text-transform: uppercase; }}
        .line span {{ color: var(--neon); margin-right: 10px; }}
        .footer {{ margin-top: 20px; font-size: 0.7rem; color: #444; }}
    </style>
</head>
<body>
    <div class="header"><div class="airport-id">TALLINN <span style="color:var(--neon)">EETN</span></div><div style="font-size:0.8rem;color:#666;">{now} UTC</div></div>
    <div class="grid">
        <div class="card"><div class="label">INFORMATION</div><div class="value">{info_letter}</div></div>
        <div class="card"><div class="label">RUNWAY</div><div class="value">{runway}</div></div>
        <div class="card"><div class="label">QNH</div><div class="value">{qnh}</div></div>
    </div>
    <div class="sec-grid">
        <div class="small-card"><span class="label">WIND</span>{wind}</div>
        <div class="small-card"><span class="label">TEMP/DEW</span>{temp_dew}</div>
    </div>
    <div class="content">{html_lines}</div>
    <div class="footer">EETN ATIS MONITOR • AUTO-UPDATED</div>
</body>
</html>
'''
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
