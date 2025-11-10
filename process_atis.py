#!/usr/bin/env python3
# process_atis.py
# Parses raw ATIS text and generates structured HTML and JSON.
# If a parameter is missing, it is set to "NaN".

import re
import sys
import json

def parse_atis(raw_text):
    """Extract structured ATIS data from raw text using flexible regex patterns."""
    
    # Clean text: replace commas and hyphens with spaces, lowercase for easier matching
    text = re.sub(r'[,/-]', ' ', raw_text).lower()

    def match(pattern):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else "NaN"

    # ATIS letter
    atis_letter = match(r'information\s*[a-z]*\s*([A-Z])').upper()

    # ATIS time (4 digits)
    atis_time = match(r'time\s*(\d{4})')

    # Wind
    wind_match = re.search(r'wind.*?(\d{1,3})\s*degrees.*?(\d{1,2})\s*knots', text)
    if wind_match:
        wind_dir, wind_speed = wind_match.groups()
        wind = f"{wind_dir}° / {wind_speed} kt"
    else:
        wind = "NaN"

    # Visibility
    visibility = match(r'visibility.*?(\d+\s*(?:km|kilometers|m|meters))')

    # Runway in use
    runway = match(r'runway\s*(\d{1,2}[lrc]?)')

    # Runway condition
    rwy_cond = "NaN"

    # Clouds
    clouds_match = re.search(r'(overcast|few|scattered|broken)', text)
    clouds = clouds_match.group(1).upper() if clouds_match else "NaN"

    # Bird activity
    bird_activity = "in the vicinity of the airport" if "bird" in text else "NaN"

    # Temperature / Dew point
    temp_match = re.search(r'temperature\s*(\d+)', text)
    dew_match = re.search(r'dew point\s*(\d+)', text)
    if temp_match and dew_match:
        temp_dew = f"{temp_match.group(1)}°C / {dew_match.group(1)}°C"
    else:
        temp_dew = "NaN"

    # QNH
    qnh_match = re.search(r'qnh\s*([\d\s]+)', text)
    if qnh_match:
        qnh = qnh_match.group(1).replace(" ", "").replace("-", "")
    else:
        qnh = "NaN"

    # Transition level
    tl_match = re.search(r'transition level\s*(\d{1,3})', text)
    tl = tl_match.group(1) if tl_match else "NaN"

    # Trend
    trend_match = re.search(r'trend\s*(.*?)(?:\.|$)', text)
    trend = trend_match.group(1).capitalize() if trend_match else "NaN"

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
    """Render the structured ATIS data into HTML format."""
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
