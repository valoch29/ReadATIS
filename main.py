import os
import re
from faster_whisper import WhisperModel
from dictionary import replacement_dict 

def run_atis_system():
    audio_file = "atis_recorded.wav"
    if not os.path.exists(audio_file): return

    model = WhisperModel("medium.en", device="cpu", compute_type="int8")
    prompt = "Tallinn Airport ATIS, Information Delta, Runway 26, QNH 1010, RCC 5/5/5, LVP ACTIVE, visibility 700m, RVR 1100m, vertical visibility 100ft."
    segments, _ = model.transcribe(audio_file, beam_size=5, initial_prompt=prompt)
    text = " ".join([s.text for s in segments]).upper()

    # Nettoyage
    for wrong, right in replacement_dict.items():
        text = re.sub(rf'\b{wrong}\b', right, text)

    # Extraction
    def find(pattern, src):
        res = re.findall(pattern, src)
        return res[-1] if res else "---"

    # 1. Indicateur LVP
    lvp_active = "LVP ACTIVE" in text
    lvp_tag = '<span class="lvp-alert">⚠️ LVP ACTIVE</span>' if lvp_active else ""

    # 2. Visibilité vs CAVOK
    vis_match = re.search(r"TOUCHDOWN ZONE\s+(\d+)\s+METERS", text)
    vis_display = f"{vis_match.group(1)}m" if vis_match else ("CAVOK" if "CAVOK" in text else "---")

    # 3. RVR (Runway Visual Range)
    rvr_match = re.search(r"VISUAL RANGE.*?TOUCHDOWN ZONE\s+(\d+)", text)
    rvr_display = f"RVR {rvr_match.group(1)}m" if rvr_match else ""

    # 4. Heure (Correction espace)
    atis_time = find(r"TIME\s+(\d{4})", text)
    display_time = f"{atis_time[:2]}:{atis_time[2:]}" if atis_time != "---" else "---"

    # 5. Temp/Dewp
    temp = find(r"TEMPERATURE\s+(\d+)", text)
    dewp = find(r"DEWPOINT\s+(\d+)", text)
    
    # Génération HTML
    html_template = """
    <style>
        .lvp-alert {{ color: #ff4444; border: 1px solid #ff4444; padding: 2px 8px; border-radius: 5px; font-size: 0.7rem; animation: blink 2s infinite; }}
        @keyframes blink {{ 0% {{opacity: 1;}} 50% {{opacity: 0.3;}} 100% {{opacity: 1;}} }}
    </style>
    <div class="header">
        <span>EETN TALLINN</span>
        {LVP_TAG}
        <span style="color:#fff">{ZULU}Z</span>
    </div>
    <div class="tile"><div class="label">Visibility</div><div class="val">{VIS} <small style="font-size:0.6rem; color:#777;">{RVR}</small></div></div>
    """

    final_html = html_template.format(
        LVP_TAG=lvp_tag,
        ZULU=display_time,
        INFO=find(r"INFORMATION\s+([A-Z])", text),
        RWY=find(r"RUNWAY\s+(\d{2})", text),
        QNH=f"{find(r'QNH\s+(\d{4})', text)} hPa",
        WIND=f"{find(r'TOUCHDOWN ZONE\s+(\d{3})', text)}°/{find(r'KNOTS', text)}KT",
        VIS=vis_display,
        RVR=rvr_display,
        TEMP_DEWP=f"{temp}° / {dewp}°",
        RCC="5/5/5",
        CONTAM="WET / WET / WET",
        RAW=text
    )
    # ... (sauvegarde du fichier)
