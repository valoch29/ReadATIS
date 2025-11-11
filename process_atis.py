#!/usr/bin/env python3
# process_atis.py
# Décodage ATIS + validation METAR, sans IA

import os
import sys
import json
from bs4 import BeautifulSoup
import re
import requests

METAR_API_TOKEN = os.environ.get("METAR_API_TOKEN")  # clé API pour avwx.rest ou autre

def fetch_metar():
    """Récupère le dernier METAR pour Tallinn (EETN)."""
    if not METAR_API_TOKEN:
        print("⚠️ METAR_API_TOKEN non défini, validation METAR désactivée.")
        return {}
    try:
        url = f"https://avwx.rest/api/metar/EETN?options=info&format=json&token={METAR_API_TOKEN}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "wind_dir": int(data.get("wind_direction", {}).get("value", 0)),
                "wind_speed": int(data.get("wind_speed", {}).get("value", 0)),
                "altimeter": int(data.get("altimeter", {}).get("value", 0)),
                "visibility": int(data.get("visibility", {}).get("value", 0)),
                "temperature": float(data.get("temperature", {}).get("value", 0)),
                "dewpoint": float(data.get("dewpoint", {}).get("value", 0))
            }
    except Exception as e:
        print(f"⚠️ Erreur récupération METAR: {e}")
    return {}

def parse_atis_text(raw_text):
    """Extrait les informations ATIS depuis la transcription brute."""

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

    # 1️⃣ ATIS letter
    match_letter = re.search(r"[iI]nformation\s+([A-Z])", raw_text)
    if match_letter:
        data["atis_letter"] = match_letter.group(1)

    # 2️⃣ ATIS time
    match_time = re.search(r"[tT]ime\s+(\d{3,4})", raw_text)
    if match_time:
        data["atis_time"] = match_time.group(1)

    # 3️⃣ Wind
    match_wind = re.search(r"[wW]ind.*?(\d{1,3})\s*degrees[,/ ]+(\d+)\s*knots", raw_text)
    if match_wind:
        data["wind"] = f"{match_wind.group(1)}°/{match_wind.group(2)} kt"

    # 4️⃣ Visibility
    match_vis = re.search(r"[vV]isibility.*?(\d+)\s*kilometers?", raw_text)
    if match_vis:
        data["visibility"] = f"{match_vis.group(1)} km"

    # 5️⃣ Runway
    match_rwy = re.search(r"[rR]unway\s+(\d+)", raw_text)
    if match_rwy:
        data["runway"] = match_rwy.group(1)

    # 6️⃣ Runway condition
    match_rwy_cond = re.search(r"[tT]ouchdown.*?(\d+)[^\d]+midpoint.*?(\d+)[^\d]+stop end.*?(\d+)", raw_text, re.IGNORECASE)
    if match_rwy_cond:
        data["rwy_cond"] = f"TDZ {match_rwy_cond.group(1)}/MID {match_rwy_cond.group(2)}/END {match_rwy_cond.group(3)}"

    # 7️⃣ Clouds
    cloud_matches = re.findall(r"(overcast|scatter|few|broken)[ ,]*(\d+)[ ]*feet", raw_text, re.IGNORECASE)
    if cloud_matches:
        clouds_list = [f"{m[0].capitalize()} {m[1]} ft" for m in cloud_matches]
        data["clouds"] = ", ".join(clouds_list)

    # 8️⃣ Bird activity
    if "bird" in raw_text.lower():
        data["bird"] = "Yes"

    # 9️⃣ Temperature / Dew point
    match_temp = re.search(r"[tT]emperature[, ]+(\d+)[ ,/]+dew point[, ]+(\d+\.?\d*)", raw_text)
    if match_temp:
        data["temp_dew"] = f"{match_temp.group(1)} / {match_temp.group(2)} °C"

    # 10️⃣ QNH
    match_qnh = re.search(r"[qQ][nN][hH][ ,]?(\d{4})", raw_text)
    if match_qnh:
        data["qnh"] = match_qnh.group(1)

    # 11️⃣ Transition level
    match_tl = re.search(r"[tT]ransition level\s+(\d+)", raw_text)
    if match_tl:
        data["tl"] = match_tl.group(1)

    # 12️⃣ Trend
    match_trend = re.search(r"[tT]rend[, ]+(.*?)(?:\.|$)", raw_text)
    if match_trend:
        data["trend"] = match_trend.group(1).strip()

    return data

def validate_with_metar(atis_data, metar_data):
    """Compare certaines valeurs avec le METAR et remplace par NaN si incohérent."""

    # Vent
    if "wind" in atis_data and metar_data:
        try:
            dir_deg, speed = map(int, atis_data["wind"].replace("°","").replace(" kt","").split("/"))
            if abs(dir_deg - metar_data["wind_dir"]) > 20 or abs(speed - metar_data["wind_speed"]) > 10:
                atis_data["wind"] = "NaN"
        except:
            pass

    # QNH
    if "qnh" in atis_data and metar_data:
        try:
            if abs(int(atis_data["qnh"]) - metar_data["altimeter"]) > 5:
                atis_data["qnh"] = "NaN"
        except:
            pass

    # Visibilité
    if "visibility" in atis_data and metar_data:
        try:
            if abs(int(atis_data["visibility"].replace(" km","")) - metar_data["visibility"]) > 2:
                atis_data["visibility"] = "NaN"
        except:
            pass

    # Température / Dew point
    if "temp_dew" in atis_data and metar_data:
        try:
            at, dp = map(float, atis_data["temp_dew"].replace(" °C","").split("/"))
            if abs(at - metar_data["temperature"]) > 3 or abs(dp - metar_data["dewpoint"]) > 3:
                atis_data["temp_dew"] = "NaN / NaN °C"
        except:
            pass

    return atis_data

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
        raw = f.read()

    data = parse_atis_text(raw)

    # Récupérer METAR et valider
    metar = fetch_metar()
    data = validate_with_metar(data, metar)

    # Export JSON
    with open("atis.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Export HTML
    with open("atis_structured.html", "w", encoding="utf-8") as f:
        f.write(render_html(data))

    print("✅ ATIS traité avec succès")
    print(json.dumps(data, indent=2))
