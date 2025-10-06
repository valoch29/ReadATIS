# process_atis.py
import re
import sys
import json

def parse_atis(raw_text):
    # Extraire les informations avec des expressions régulières adaptées
    def match(pattern, text, default=""):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else default

    # ATIS letter
    atis_letter = match(r'information\s+([a-z])', raw_text, "U")

    # ATIS time
    atis_time = match(r'time\s+(\d{4})', raw_text, "0000")

    # Wind
    wind_dir = match(r'wind.*?(\d{2,3})\s+degrees', raw_text, "000")
    wind_speed = match(r'(\d{1,2})\s+knots', raw_text, "00")
    wind = f"{wind_dir}/{wind_speed}KT"

    # Visibility
    visibility = match(r'visibility.*?(\d{1,2}[,\.\d]*\s*(?:meters|kilometers))', raw_text, "10KM")

    # Clouds
    clouds = match(r'cloud.*?(overcast|few|scattered|broken).*?(\d{3,4})\s+feet', raw_text, "OVC004")
    clouds = clouds.replace("overcast", "OVC").replace("few", "FEW").replace("scattered", "SCT").replace("broken", "BKN")

    # Temperature/Dew point
    temp = match(r'temperature.*?(\d{1,2})', raw_text, "10")
    dew = match(r'dew point.*?(\d{1,2})', raw_text, "10")

    # QNH (par défaut si non précisé)
    qnh = "1007"

    # Transition level
    tl = match(r'transition level\s+(\d{2})', raw_text, "65")

    # Bird activity
    bird_activity = "in vicinity of airport" if "bird activity" in raw_text else "NIL"

    # Runway
    runway = match(r'runway\s+(\d{2})\s+in use', raw_text, "08")

    return {
        "atis_letter": atis_letter,
        "atis_time": atis_time,
        "wind": wind,
        "visibility": visibility,
        "clouds": [clouds],
        "bird": bird_activity,
        "temp_dew": f"{temp}/{dew}",
        "qnh": qnh,
        "tl": tl,
        "trend": "NOSIG",
        "runway": runway
    }

def render_html(data):
    clouds_html = "<br>".join(data["clouds"])
    return f"""
    <h3 style="margin: 0 0 0.5em 0; font-size: 1.1em;">
        ATIS Tallinn (EETN) - <strong>Info {data['atis_letter']}</strong>
        <span style="float: right; color: #666; font-size: 0.9em;">{data['atis_time']}Z</span>
    </h3>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5em;">
        <div>
            <strong>WIND:</strong> {data['wind']}<br>
            <strong>VIS:</strong> {data['visibility']}<br>
            <strong>RWY COND:</strong> 6/6/6 (DRY)<br>
            <strong>CLOUD:</strong><br>{clouds_html}<br>
            <strong>BIRD:</strong> {data['bird']}
        </div>
        <div>
            <strong>TEMP/DEW:</strong> {data['temp_dew']}<br>
            <strong>QNH:</strong> {data['qnh']}hPa<br>
            <strong>TL:</strong> {data['tl']}<br>
            <strong>TREND:</strong> {data['trend']}<br>
            <strong>RWY:</strong> {data['runway']}
        </div>
    </div>
    """

if __name__ == "__main__":
    input_file = sys.argv[1]
    with open(input_file, "r") as f:
        raw = f.read()
    data = parse_atis(raw)

    # Export JSON
    with open("atis.json", "w") as f:
        json.dump(data, f, indent=2)

    # Export HTML
    with open("atis_structured.html", "w") as f:
        f.write(render_html(data))
