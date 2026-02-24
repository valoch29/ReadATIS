import datetime
import os
import re

atis_text = "WAITING FOR DATA..."
info, qnh, rwy, wind, temp_dew = "-", "----", "--", "--- / --KT", "-- / --"

if os.path.exists("atis_transcribed.txt"):
    with open("atis_transcribed.txt", "r", encoding="utf-8") as f:
        # On simplifie le texte : MAJUSCULES et suppression des bruits
        raw = f.read().upper().replace("-", " ").replace(",", " ")
        # On s'assure que les chiffres sont bien séparés du texte
        atis_text = re.sub(r'(\d)([A-Z])', r'\1 \2', raw)
        atis_text = re.sub(r'([A-Z])(\d)', r'\1 \2', atis_text)

    # --- LOGIQUE D'EXTRACTION PAR PROXIMITÉ ---

    # 1. INFO : Ce qui suit le mot "INFORMATION"
    m_info = re.search(r"INFORMATION\s+([A-Z])", atis_text)
    if m_info: info = m_info.group(1)

    # 2. RUNWAY : Les 2 chiffres après "RUNWAY" ou "RUNWAY 0"
    m_rwy = re.search(r"RUNWAY\s*(?:0)?(\d{2})", atis_text)
    if m_rwy: rwy = m_rwy.group(1)

    # 3. QNH : Les 4 chiffres après "QNH" (on ignore les espaces/points entre les chiffres)
    # On cherche "QNH" puis on capture tout ce qui ressemble à 4 chiffres dans les 15 caractères suivants
    m_qnh_context = re.search(r"QNH\s*(.{1,15})", atis_text)
    if m_qnh_context:
        digits = re.sub(r'\D', '', m_qnh_context.group(1))
        if len(digits) >= 4: qnh = digits[:4]

    # 4. VENT : On cherche "DEGREES" et on prend ce qu'il y a avant et après
    # Exemple : "050 DEGREES 7 KNOTS"
    m_wind = re.search(r"(\d{3})\s*DEGREES\s*(\d+)", atis_text)
    if m_wind:
        wind = f"{m_wind.group(1)}° / {m_wind.group(2).zfill(2)}KT"

    # 5. TEMP/DEW : Proximité avec "TEMPERATURE" et "DEWPOINT"
    m_temp = re.search(r"TEMPERATURE\s*(.*?)\s*(\d+)", atis_text)
    m_dew = re.search(r"DEWPOINT\s*(.*?)\s*(\d+)", atis_text)
    
    t_val, d_val = "--", "--"
    if m_temp:
        prefix = "-" if "MINUS" in m_temp.group(1) else ""
        t_val = prefix + m_temp.group(2)
    if m_dew:
        prefix = "-" if "MINUS" in m_dew.group(1) else ""
        d_val = prefix + m_dew.group(2)
    temp_dew = f"{t_val}° / {d_val}°"

# --- MISE EN PAGE ---
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
        .met-box {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 5px; background: #000; padding: 12px; border: 1px solid #1a1a1a; text-align: center; }}
        .raw-text {{ font-size: 0.75rem; color: #666; line-height: 1.4; padding: 10px; border-top: 1px solid #222; margin-top: 10px; }}
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
            <div><span style="color:#444; font-size:0.6rem;">WIND</span><br><span style="font-size:1.1rem; font-weight:bold; color:#eee;">{wind}</span></div>
            <div><span style="color:#444; font-size:0.6rem;">TEMP / DEW</span><br><span style="font-size:1.1rem; font-weight:bold; color:#eee;">{temp_dew}</span></div>
        </div>
    </div>
    <div class="section">
        <div class="sec-title">RAW TRANSCRIPTION</div>
        <div class="raw-text">{atis_text}</div>
    </div>
    <div style="font-size: 0.6rem; color: #222; margin-top: 10px; letter-spacing: 2px;">DATALINK ATIS MONITOR</div>
</body>
</html>
'''
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
