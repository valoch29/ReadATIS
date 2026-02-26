import os
import re
import datetime
from faster_whisper import WhisperModel
from dictionary import replacement_dict 

def run_atis_system():
    audio_file = "atis_recorded.wav"
    if not os.path.exists(audio_file):
        return

    # 1. Transcription
    model = WhisperModel("medium.en", device="cpu", compute_type="int8")
    # Prompt optimisé pour capter les formats RCC et contaminants
    prompt = "Tallinn Airport ATIS, Information, Runway 26, QNH 1013, RCC 5/5/5, wet, frost, dry, touchdown, midpoint, stop-end."
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
    qnh_val = find(r"(?:QNH|HPA|HECTOPASCALS)\s+(\d{4})", text)
    qnh_display = f"{qnh_val} hPa" if qnh_val != "---" else "---"
    
    atis_time = find(r"TIME\s+(\d{4})", text)
    display_time = f"{atis_time[:2]}:{atis_time[2:]}" if atis_time != "---" else "---"

    # Extraction du RCC (Cherche un chiffre après chaque mot-clé de zone)
    rcc_match = re.search(r"TOUCHDOWN\s+(\d)\s+MIDPOINT\s+(\d)\s+STOP\s+END\s+(\d)", text)
    if rcc_match:
        rcc = f"{rcc_match.group(1)}/{rcc_match.group(2)}/{rcc_match.group(3)}"
    else:
        rcc = "---"

    # Contaminants (TDZ/MID/END)
    def get_contam(part, src):
        # Cherche le mot (WET, DRY, etc.) après le pourcentage
        match = re.search(rf"{part}\s+\d+\s*(?:PERCENT|%)\s+(\w+)", src)
        return match.group(1) if match else "---"
    
    contam_str = f"{get_contam('TOUCHDOWN', text)} / {get_contam('MIDPOINT', text)} / {get_contam('STOP END', text)}"

    # Temp & Dewpoint (Fusionnés)
    def get_temp(type_name, src):
        match = re.search(rf"{type_name}\s+(MINUS\s+)?(\d+)", src)
        if match:
            val = match.group(2)
            return f"-{val}" if match.group(1) else val
        return "---"
    
    temp = get_temp("TEMPERATURE", text)
    dewp = get_temp("DEWPOINT", text)
    temp_dewp_display = f"{temp}° / {dewp}°"

    # Vent
    w_match = re.search(r"TOUCHDOWN ZONE\s+(\d{3})\s+DEGREES\s+(\d+)\s+KNOTS", text)
    if not w_match:
        w_match = re.search(r"(\d{3})\s+DEGREES\s+(\d+)\s+KNOTS", text)
    wind = f"{w_match.group(1)}°/{w_match.group(2)}KT" if w_match else "---"

    # 4. Découpe Chirurgicale
    start_trigger = "THIS IS TALLINN"
    start_idx = text.find(start_trigger)
    if start_idx != -1:
        iteration = text[start_idx:]
        next_iter = iteration.find(start_trigger, 60)
        if next_iter == -1: 
            next_iter = iteration.find("INFORMATION", 60)
        clean_display_text = iteration[:next_iter].strip() if next_iter != -1 else iteration.strip()
    else:
        clean_display_text = text

    # 5. Génération HTML
    html_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {{ --bg: #000; --card: #0d0d0d; --border: #222; --text: #fff; --dim: #777; --subtext: #bbb; }}
        body {{ background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; margin: 0; padding: 25px; display: flex; justify-content: center; }}
        .container {{ width: 100%; max-width: 420px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; letter-spacing: 2px; font-weight: 800; font-size: 0.8rem; color: var(--dim); }}
        .info-section {{ text-align: center; margin-bottom: 25px; background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 15px; }}
        .info-letter {{ font-size: 6rem; font-weight: 900; line-height: 1; margin: 0; }}
        .info-label {{ text-transform: uppercase; font-size: 0.7rem; letter-spacing: 4px; color: var(--dim); margin-bottom: 5px; display: block; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
        .tile {{ background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 18px; }}
        .full-width {{ grid-column: span 2; }}
        .label {{ color: var(--dim); font-size: 0.6rem; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; margin-bottom: 8px; }}
        .val {{ font-size: 1.2rem; font-weight: 700; }}
        .raw {{ margin-top: 40px; font-size: 0.8rem; color: var(--subtext); line-height: 1.6; text-align: justify; border-top: 1px solid #222; padding-top: 20px; text-transform: uppercase; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span>EETN TALLINN</span>
            <span style="color:#fff">{ZULU}Z</span>
        </div>
        <div class="info-section">
            <span class="info-label">Information</span>
            <div class="info-letter">{INFO}</div>
        </div>
        <div class="grid">
            <div class="tile"><div class="label">Runway</div><div class="val">{RWY}</div></div>
            <div class="tile"><div class="label">QNH</div><div class="val">{QNH}</div></div>
            <div class="tile"><div class="label">Wind (TDZ)</div><div class="val">{WIND}</div></div>
            <div class="tile"><div class="label">Visibility</div><div class="val">CAVOK</div></div>
            <div class="tile"><div class="label">Temp / Dewp</div><div class="val">{TEMP_DEWP}</div></div>
            <div class="tile"><div class="label">RCC (TDZ/MID/END)</div><div class="val">{RCC}</div></div>
            <div class="tile full-width"><div class="label">Contaminants (TDZ/MID/END)</div><div class="val">{CONTAM}</div></div>
        </div>
        <div class="raw">{RAW}</div>
    </div>
</body>
</html>
"""
    final_html = html_template.format(
        ZULU=display_time,
        INFO=info[0] if info != "---" else "---",
        RWY=rwy,
        QNH=qnh_display,
        WIND=wind,
        TEMP_DEWP=temp_dewp_display,
        RCC=rcc,
        CONTAM=contam_str,
        RAW=clean_display_text
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    run_atis_system()
