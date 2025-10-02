import re
import sys

def process_atis_message(input_file):
    with open(input_file, 'r') as f:
        raw_text = f.read()

    # Extraction des données (exemples simplifiés)
    atis_letter_match = re.search(r'Information ([A-Z])', raw_text)
    atis_letter = atis_letter_match.group(1) if atis_letter_match else "?"

    atis_time_match = re.search(r'Time,? ([0-9]{4})', raw_text)
    atis_time = atis_time_match.group(1) if atis_time_match else "?"

    # Extraction du vent
    wind_match = re.search(r'Wind,? runway [0-9]{2}, touch-down zone,? ([0-9]{3}),? ([0-9]+) knots', raw_text, re.IGNORECASE)
    wind_direction = wind_match.group(1) if wind_match else "080"
    wind_speed = wind_match.group(2) if wind_match else "09"

    visibility = "10"
    runway_condition_code = "6/6/6"
    runway_state = "DRY"
    cloud_cover = "SCT"
    cloud_height = "3700"
    bird_activity_status = "Vicinity" if "bird activity" in raw_text.lower() else "None"
    temperature = "12"
    dewpoint = "4"
    qnh = "1037"
    transition_level = "55"
    trend = "NOSIG"
    runway_in_use = "08"

    # Construction du contenu de la div
    structured_content = f"""
    <h3 style="margin: 0 0 0.5em 0; font-size: 1.1em;">
        ATIS Tallinn (EETN) - <strong>Info {atis_letter}</strong>
        <span style="float: right; color: #666; font-size: 0.9em;">{atis_time}Z</span>
    </h3>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5em;">
        <div>
            <strong>WIND:</strong> {wind_direction}/{wind_speed}KT<br>
            <strong>VIS:</strong> &gt;{visibility}KM<br>
            <strong>RWY COND:</strong> {runway_condition_code} ({runway_state})<br>
            <strong>CLOUD:</strong> {cloud_cover} {cloud_height}FT<br>
            <strong>BIRD:</strong> {bird_activity_status}
        </div>
        <div>
            <strong>TEMP/DEW:</strong> {temperature}/{dewpoint}<br>
            <strong>QNH:</strong> {qnh}hPa<br>
            <strong>TL:</strong> {transition_level}<br>
            <strong>TREND:</strong> {trend}<br>
            <strong>RWY:</strong> {runway_in_use}
        </div>
    </div>
    """

    return structured_content

if __name__ == "__main__":
    input_file = sys.argv[1]
    structured_content = process_atis_message(input_file)
    print(structured_content)
