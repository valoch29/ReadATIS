import os
import re
from faster_whisper import WhisperModel
from dictionary import replacement_dict 

def run_atis_system():
    audio_file = "atis_recorded.wav"
    if not os.path.exists(audio_file): return

    # 1. Transcription avec prompt guidé pour les LVP
    model = WhisperModel("medium.en", device="cpu", compute_type="int8")
    prompt = "Tallinn Airport ATIS, Information, Runway 26, QNH 1013, RCC 5/5/5, wet, touchdown, midpoint, stop-end, visibility 1500m, overcast 200 feet."
    segments, _ = model.transcribe(audio_file, beam_size=5, initial_prompt=prompt)
    raw_text = " ".join([s.text for s in segments]).upper()

    # 2. Nettoyage
    text = raw_text.replace(",", " ").replace(".", " ")
    for wrong, right in replacement_dict.items():
        text = re.sub(rf'\b{wrong}\b', right, text)
    text = " ".join(text.split())

    # 3. Extraction des données
    def find(pattern, src):
        res = re.findall(pattern, src)
        return res[-1] if res else "---"

    info = find(r"INFORMATION\s+([A-Z])", text)
    rwy  = find(r"RUNWAY\s+(\d{2})", text)
    qnh_val = find(r"(?:QNH|HPA)\s+(\d{4})", text)
    
    atis_time = find(r"TIME\s+(\d{4})", text)
    display_time = f"{atis_time[:2]}:{atis_time[2:]}" if atis_time != "---" else "---"

    # RCC (Touchdown / Midpoint / Stop End)
    rcc_match = re.search(r"TOUCHDOWN\s+(\d)\s+MIDPOINT\s+(\d)\s+STOP\s+END\s+(\d)", text)
    rcc = f"{rcc_match.group(1)}/{rcc_match.group(2)}/{rcc_match.group(3)}" if rcc_match else "---"

    # Contaminants
    def get_contam(part, src):
        match = re.search(rf"{part}\s+\d+\s*(?:PERCENT|%)\s+(\w+)", src)
        return match.group(1) if match else "---"
    contam_str = f"{get_contam('TOUCHDOWN', text)} / {get_contam('MIDPOINT', text)} / {get_contam('STOP END', text)}"

    # Temp/Dewp
    def get_temp(type_name, src):
        match = re.search(rf"{type_name}\s+(MINUS\s+)?(\d+)", src)
        if match:
            val = match.group(2)
            return f"-{val}" if match.group(1) else val
        return "---"
    temp_dewp_display = f"{get_temp('TEMPERATURE', text)}° / {get_temp('DEWPOINT', text)}°"

    # VENT : Correction pour accepter le symbole ° et les rafales
    w_match = re.search(r"TOUCHDOWN ZONE\s+(\d{3})(?:\s+DEGREES|°)?\s+(\d+)\s+KNOTS(?:\s+MAXIMUM\s+(\d+))?", text)
    if w_match:
        wind = f"{w_match.group(1)}°/{w_match.group(2)}KT"
        if w_match.group(3): wind += f" G{w_match.group(3)}KT"
    else:
        wind = "---"

    # VISIBILITÉ : Extraction en mètres (indispensable pour les LVP)
    vis_match = re.search(r"VISIBILITY.*?TOUCHDOWN ZONE\s+(\d+)", text)
    vis_display = f"{vis_match.group(1)}m" if vis_match else ("CAVOK" if "CAVOK" in text else "---")

    # 4. Génération HTML (Pensez à utiliser {VIS} dans votre template pour la visibilité)
    final_html = html_template.format(
        ZULU=display_time,
        INFO=info[0] if info != "---" else "---",
        RWY=rwy,
        QNH=f"{qnh_val} hPa" if qnh_val != "---" else "---",
        WIND=wind,
        VIS=vis_display,
        TEMP_DEWP=temp_dewp_display,
        RCC=rcc,
        CONTAM=contam_str,
        RAW=text
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
