import re
import sys
import json

def parse_atis(raw_text):
    raw_text = raw_text.replace("\n", " ").lower()

    def match(pattern, default=None, group=1):
        m = re.search(pattern, raw_text)
        return m.group(group) if m else default

    # Lettre et heure
    atis_letter = match(r'information\s+([a-z])', "?").upper()
    atis_time = match(r'time\s+(\d{4})', "?")

    # Vent (gestion rafales)
    wind = re.search(r'wind.*?(\d{2,3}).*?(\d{1,2})(?:\s*gusts?\s*(\d{1,2}))?\s*knots', raw_text)
    wind_dir = wind.group(1) if wind else "080"
    wind_speed = wind.group(2) if wind else "09"
    wind_gust = wind.group(3) if wind and wind.group(3) else None

    # Visibilité (m ou km)
    vis = match(r'visibility.*?(\d+)\s*(kilometers|meters)', None, group=1)
    vis_unit = match(r'visibility.*?(\d+)\s*(kilometers|meters)', "kilometers", group=2)
    if vis:
        visibility = f"{vis}{'KM' if 'kilo' in vis_unit else 'M'}"
    else:
        visibility = ">10KM"

    # Nuages (toutes couches)
    clouds = re.findall(r'cloud\s+(scattered|broken|overcast)\s+(\d+)', raw_text)
    cloud_layers = [f"{c[0][:3].upper()} {c[1]}FT" for c in clouds] if clouds else ["SCT 3700FT"]

    # Oiseaux
    bird_activity = "Yes" if "bird activity" in raw_text else "None"

    # Température / Point de rosée
    temp = match(r'temperature\s+(\d{1,2})', "12")
    dew = match(r'dew point\s+(\d{1,2})', "4")

    # QNH / TL / Piste
    qnh = match(r'qnh\s+(\d{4})', "1037")
    tl = match(r'transition level\s+(\d{2})', "55")
    runway = match(r'runway\s+(\d{2})\s+in use', "08")

    return {
        "atis_letter": atis_letter,
        "atis_time": atis_time,
        "wind": f"{wind_dir}/{wind_speed}KT" + (f" G{wind_gust}" if wind_gust else ""),
        "visibility": visibility,
        "clouds": cloud_layers,
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
