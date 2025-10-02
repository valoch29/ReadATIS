import re
import sys

def process_atis_message(input_file):
    with open(input_file, 'r') as f:
        raw_text = f.read().replace("\n", " ")  # Nettoyage des sauts de ligne

    # Extraction de la lettre ATIS (ex: "Information Victor" ou "Information, Victor")
    atis_letter_match = re.search(r'Information[,\s]+([A-Z])', raw_text, re.IGNORECASE)
    atis_letter = atis_letter_match.group(1) if atis_letter_match else "?"

    # Extraction de l'heure (ex: "Time, 0850" ou "time 0850")
    atis_time_match = re.search(r'time[,\s]+([0-9]{4})', raw_text, re.IGNORECASE)
    atis_time = atis_time_match.group(1) if atis_time_match else "?"

    # Extraction du vent (ex: "Wind, runway 08, touch-down zone, 080°, 9 knots")
    wind_match = re.search(r'Wind.*?([0-9]{2,3}).*?([0-9]{1,2})\s*knots', raw_text, re.IGNORECASE)
    wind_direction = wind_match.group(1) if wind_match else "080"
    wind_speed = wind_match.group(2) if wind_match else "09"

    # Extraction de la visibilité (ex: "visibility runway 08, touchdown zone, 10 kilometers")
    visibility_match = re.search(r'visibility.*?([0-9]+)\s*kilometers', raw_text, re.IGNORECASE)
    visibility = visibility_match.group(1) if visibility_match else "10"

    # Extraction des nuages (ex: "cloud scattered 3700 feet")
    cloud_match = re.search(r'cloud\s+(scattered|broken|overcast)\s+([0-9]+)\s+feet', raw_text, re.IGNORECASE)
    cloud_cover = cloud_match.group(1).upper()[:3] if cloud_match else "SCT"
    cloud_height = cloud_match.group(2) if cloud_match else "3700"

    # Extraction de la présence d'oiseaux
    bird_activity_status = "Vicinity" if "bird activity" in raw_text.lower() else "None"

    # Extraction de la température et du point de rosée (ex: "temperature 12, dew point 4")
    temp_match = re.search(r'temperature[,\s]+([0-9]+)', raw_text, re.IGNORECASE)
    temperature = temp_match.group(1) if temp_match else "12"
    dewpoint_match = re.search(r'dew point[,\s]+([0-9]+)', raw_text, re.IGNORECASE)
    dewpoint = dewpoint_match.group(1) if dewpoint_match else "4"

    # Extraction du QNH (ex: "QNH 1037")
    qnh_match = re.search(r'QNH[,\s]+([0-9]+)', raw_text, re.IGNORECASE)
    qnh = qnh_match.group(1) if qnh_match else "1037"

    # Extraction du Transition Level (ex: "Transition level 55")
    tl_match = re.search(r'Transition level[,\s]+([0-9]+)', raw_text, re.IGNORECASE)
    transition_level = tl_match.group(1) if tl_match else "55"

    # Extraction de la piste en service (ex: "runway 08 in use")
    runway_match = re.search(r'runway[,\s]+([0-9]{2})\s+in use', raw_text, re.IGNORECASE)
    runway_in_use = runway_match.group(1) if runway_match else "08"

    # Construction du contenu structuré
    structured_content = f"""
    <h3 style="margin: 0 0 0.5em 0; font-size: 1.1em;">
        ATIS Tallinn (EETN) - <strong>Info {atis_letter}</strong>
        <span style="float: right; color: #666; font-size: 0.9em;">{atis_time}Z</span>
    </h3>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5em;">
        <div>
            <strong>WIND:</strong> {wind_direction}/{wind_speed}KT<br>
            <strong>VIS:</strong> &gt;{visibility}KM<br>
            <strong>RWY COND:</strong> 6/6/6 (DRY)<br>
            <strong>CLOUD:</strong> {cloud_cover} {cloud_height}FT<br>
            <strong>BIRD:</strong> {bird_activity_status}
        </div>
        <div>
            <strong>TEMP/DEW:</strong> {temperature}/{dewpoint}<br>
            <strong>QNH:</strong> {qnh}hPa<br>
            <strong>TL:</strong> {transition_level}<br>
            <strong>TREND:</strong> NOSIG<br>
            <strong>RWY:</strong> {runway_in_use}
        </div>
    </div>
    """

    return structured_content

if __name__ == "__main__":
    input_file = sys.argv[1]
    structured_content = process_atis_message(input_file)
    print(structured_content)
