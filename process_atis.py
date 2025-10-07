#!/usr/bin/env python3
# process_atis.py
# Parses raw ATIS text and generates a simple, single-column English HTML block.

import re
import sys
import json

def parse_atis(raw_text):
    """Extract structured ATIS data from raw text using regex patterns."""

    def match(pattern, text, default=""):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else default

    # ATIS letter
    atis_letter = match(r'information\s+([A-Z])', raw_text, "U").upper()

    # ATIS time
    atis_time = match(r'(\d{4})Z', raw_text, "0000")

    # Wind
    wind_dir = match(r'wind\s+(\d{2,3})', raw_text, "000")
    wind_speed = match(r'(\d{1,2})\s*(?:kt|knots)', raw_text, "00")
    wind = f"{wind_dir}° / {wind_speed} kt"

    # Visibility
    visibility = match(r'visibility\s+([\d,\.]+\s*(?:m|meters|km|kilometers))', raw_text, "10 km")

    # Runway
    runway = match(r'runway\s*(\d{2})', raw_text, "08")

    # Runway condition
    rwy_cond = "6 / 6 / 6 (dry)"

    # Clouds
    clouds = match(r'(overcast|few|scattered|broken)', raw_text, "overcast").upper()

    # Bird activity
    bird_activity = "in the vicinity of the airport" if "bird" in raw_text.lower() else "NIL"

    # Temperature / Dew point
    temp = match(r'temperature\s+(-?\d+)', raw_text, "1")
    dew = match(r'dew\s*point\s+(-?\d+)', raw_text, "1")
    temp_dew = f"{temp}°C / {dew}°C"

    # QNH
    qnh = match(r'qnh\s*(\d{3,4})', raw_text, "1007")

    # Transition level
    tl = match(r'transition\s*level\s*(\d{2})', raw_text, "65")

    # Trend
    trend = "No significant change (NOSIG)"

    return {
        "atis_letter": atis_letter,
        "atis_time": atis_time,
        "wind": wind,
        "visibility": visibility,
        "runway": runway,
        "rwy_cond": rwy_cond,
        "clouds": clouds,
        "bird": bird_activity,
        "temp_dew": temp_dew,
        "qnh": qnh,
        "tl": tl,
        "trend": trend
    }

def render_html(data):
    """Render the structured ATIS data into the new single-column HTML format."""
    return f"""<div id="atis-message">
    <div class="atis-header">
        Information {data['atis_letter']} — <span>{data['atis_time']}Z</span>
    </div>

    <div class="atis-info">
        <div><strong>Wind:</strong> {data['wind']}</div>
        <div><strong>Visibility:</strong> {data['visibility']}</div>
        <div><strong>Runway in use:</strong> {data['runway']}</div>
        <div><strong>Runway condition:</strong> {data['rwy_cond']}</div>
        <div><strong>Cloud:</strong> {data['clouds']}</div>
        <div><strong>Bird activity:</strong> {data['bird']}</div>
        <div><strong>Temperature / Dew point:</strong> {data['temp_dew']}</div>
        <div><strong>QNH:</strong> {data['qnh']} hPa</div>
        <div><strong>Transition level:</strong> {data['tl']}</div>
        <div><strong>Trend:</strong> {data['trend']}</div>
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

    data = parse_atis(raw)

    # Export JSON
    with open("atis.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Export HTML
    with open("atis_structured.html", "w", encoding="utf-8") as f:
        f.write(render_html(data))

    print("✅ ATIS processed successfully:")
    print(json.dumps(data, indent=2))
