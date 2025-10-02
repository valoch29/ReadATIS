import re
import sys

def process_atis_message(input_file):
    with open(input_file, 'r') as f:
        raw_text = f.read().replace("\n", " ").lower()  # Convertir en minuscules pour faciliter la recherche

    # Extraction de la lettre ATIS (ex: "information yankee")
    atis_letter_match = re.search(r'information\s+([a-z])', raw_text)
    atis_letter = atis_letter_match.group(1).upper() if atis_letter_match else "?"

    # Extraction de l'heure (ex: "time 1020")
    atis_time_match = re.search(r'time\s+(\d{4})', raw_text)
    atis_time = atis_time_match.group(1) if atis_time_match else "?"

    # Extraction du vent (ex: "wind runway 08 touchdown zone 090 degrees 13 knots")
    wind_match = re.search(r'wind.*?(\d{2,3}).*?(\d{1,2})\s*knots', raw_text)
    wind_direction = wind_match.group(1) if wind_match else "080"
    wind_speed = wind_match.group(2) if wind_match else "09"

    # Extraction de la visibilité (ex: "visibility runway 08 touchdown zone 10 kilometers")
    visibility_match = re.search(r'visibility.*?(\d{1,2})\s*kilometers', raw_text)
    visibility = visibility_match.group(1) if visibility_match else "10"

    # Extraction des nuages (ex: "cloud scattered 3100 feet")
    cloud_match = re.search(r'cloud\s+(scattered|broken|overcast)\s+(\d+)', raw_text)
    cloud_cover = cloud_match.group(1).upper()[:3] if cloud_match else "SCT"
    cloud_height = cloud_match.group(2) if cloud_match else "3700"

    # Extraction de la présence d'oiseaux
    bird_activity_status = "Vicinity" if "bird activity" in raw_text else "None"

    # Extraction de la température et du point de rosée (ex: "temperature 11, dew point 4")
    temp_match = re.search(r'temperature\s+(\d{1,2})', raw_text)
    temperature = temp_match.group(1) if temp_match else "12"
    dewpoint_match = re.search(r'dew point\s+(\d{1,2})', raw_text)
    dewpoint = dewpoint_match.group(1) if dewpoint_match else "4"

    # Extraction du QNH (ex: "QNH 1034 hectopascal")
    qnh_match = re.search(r'qnh\s+(\d{4})', raw_text)
    qnh = qnh_match.group(1) if qnh_match else "1037"

    # Extraction du Transition Level (ex: "transition level 55")
    tl_match = re.search(r'transition level\s+(\d{2})', raw_text)
    transition_level = tl_match.group(1) if tl_match else "55"

    # Extraction de la piste en service (ex: "runway 08 in use")
    runway_match = re.search(r'runway\s+(\d{2})\s+in use', raw_text)
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
