#!/usr/bin/env python3
# process_atis.py — décode un message ATIS texte en JSON + HTML sans IA

import re
import sys
import json
from bs4 import BeautifulSoup

def parse_atis(text):
    """Analyse heuristique du texte ATIS pour extraire les champs principaux."""
    t = text.lower()

    data = {
        "atis_letter": "NaN",
        "atis_time": "NaN",
        "wind": "NaN",
        "visibility": "NaN",
        "runway": "NaN",
        "rwy_cond": "NaN",
        "clouds": "NaN",
        "bird": "NaN",
        "temp_dew": "NaN",
        "qnh": "NaN",
        "tl": "NaN",
        "trend": "NaN"
    }

    # Lettre d'information (Information Alpha, Bravo, Charlie…)
    m = re.search(r"information\s+([a-z])", t)
    if m:
        data["atis_letter"] = m.group(1).upper()

    # Heure (ex: time 1320 ou report time 0855)
    m = re.search(r"(?:time|report time)\s*(\d{3,4})", t)
    if m:
        data["atis_time"] = m.group(1)

    # Vent
    m = re.search(r"wind.*?(\d{3})\D*(\d{1,2})\s*knots", t)
    if m:
        data["wind"] = f"{m.group(1)}°/{m.group(2)} kt"

    # Visibilité
    m = re.search(r"visibility.*?(\d{1,2})\s*kilometer", t)
    if m:
        data["visibility"] = f"{m.group(1)} km"

    # Piste
    m = re.search(r"runway\s*(\d{2})", t)
    if m:
        data["runway"] = m.group(1)

    # Condition de piste
    m = re.search(r"condition.*?(\d).*?midpoint.*?(\d).*?(?:stop|top).*?(\d)", t)
    if m:
        data["rwy_cond"] = f"TDZ {m.group(1)}/MID {m.group(2)}/END {m.group(3)}"
    elif "wet" in t:
        data["rwy_cond"] = "Wet"

    # Nuages
    clouds = []
    for layer in re.findall(r"(few|scattered|overcast|broken)\D*(\d{2,4})", t):
        clouds.append(f"{layer[0].capitalize()} {layer[1]} ft")
    if clouds:
        data["clouds"] = ", ".join(clouds)

    # Bird activity
    if "bird" in t:
        data["bird"] = "Yes"

    # Température / dew point
    m = re.search(r"temperature[^0-9]*(\d+).*?(\d+)", t)
    if m:
        data["temp_dew"] = f"{m.group(1)} / {m.group(2)} °C"

    # QNH
    m = re.search(r"qnh[^0-9]*(\d{3,4})", t)
    if m:
        data["qnh"] = m.group(1)
    elif "hectopascal" in t:
        m = re.search(r"(\d{3,4})\s*hectopascal", t)
        if m:
            data["qnh"] = m.group(1)

    # Transition level
    m = re.search(r"transition level\s*(\d+)", t)
    if m:
        data["tl"] = m.group(1)

    # Trend
    m = re.search(r"trend[^a-z]*([a-z\s]+)", t)
    if m:
        data["trend"] = m.group(1).strip().capitalize()

    return data


def render_html(data):
    """Transforme le JSON ATIS en bloc HTML simple."""
    return f"""<div id="atis-message">
    <div class="atis-header">
        Information {data.get('atis_letter','NaN')} — <span>{data.get('atis_time','NaN')}Z</span>
    </div>

    <div class="atis-info">
        <div><strong>Wind:</strong> {data.get('wind','NaN')}</div>
        <div><strong>Visibility:</strong> {data.get('visibility','NaN')}</div>
        <div><strong>Runway in use:</strong> {data.get('runway','NaN')}</div>
        <div><strong>Runway condition:</strong> {data.get('rwy_cond','NaN')}</div>
        <div><strong>Cloud:</strong> {data.get('clouds','NaN')}</div>
        <div><strong>Bird activity:</strong> {data.get('bird','NaN')}</div>
        <div><strong>Temperature / Dew point:</strong> {data.get('temp_dew','NaN')}</div>
        <div><strong>QNH:</strong> {data.get('qnh','NaN')} hPa</div>
        <div><strong>Transition level:</strong> {data.get('tl','NaN')}</div>
        <div><strong>Trend:</strong> {data.get('trend','NaN')}</div>
    </div>
</div>
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: process_atis.py <atis_raw_text_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    data = parse_atis(raw_text)

    # Export JSON
    with open("atis.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Export HTML
    with open("atis_structured.html", "w", encoding="utf-8") as f:
        f.write(render_html(data))

    print("✅ ATIS traité avec succès")
    print(json.dumps(data, indent=2))
