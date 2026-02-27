import os
import re
from faster_whisper import WhisperModel
from dictionary import replacement_dict 

def run_atis_system():
    audio_file = "atis_recorded.wav"
    if not os.path.exists(audio_file): return

    model = WhisperModel("medium.en", device="cpu", compute_type="int8")
    prompt = "Tallinn Airport ATIS, Information Victor, Runway 26, QNH 1010, RCC 5/5/5, LVP ACTIVE, visibility 2500m, temperature 3, dewpoint 3."
    segments, _ = model.transcribe(audio_file, beam_size=5, initial_prompt=prompt)
    text = " ".join([s.text for s in segments]).upper()

    # Nettoyage
    for wrong, right in replacement_dict.items():
        text = re.sub(rf'\b{wrong}\b', right, text)

    # Fonction d'extraction
    def find(pattern, src):
        res = re.findall(pattern, src)
        return res[-1] if res else "---"

    # 1. Variables de base
    info = find(r"INFORMATION\s+([A-Z])", text)
    rwy = find(r"RUNWAY\s+(\d{2})", text)
    qnh = find(r"QNH\s+(\d{4})", text)
    
    # 2. Heure (Correction pour 1450)
    atis_time = find(r"TIME\s+(\d{4})", text)
    zulu = f"{atis_time[:2]}:{atis_time[2:]}" if atis_time != "---" else "---"

    # 3. LVP Status
    lvp_tag = '<span class="lvp-alert">⚠️ LVP ACTIVE</span>' if "LVP ACTIVE" in text else ""
    
    # 4. Vent (Supporte le symbole ° et les KNOTS)
    w_match = re.search(r"TOUCHDOWN ZONE\s+(\d{3})[°\s]+(\d+)\s+KNOTS", text)
    wind = f"{w_match.group(1)}°/{w_match.group(2)}KT" if w_match else "---"

    # 5. Visibilité (Capture 2500M)
    vis_match = re.search(r"TOUCHDOWN ZONE\s+(\d+)\s*M", text)
    vis = f"{vis_match.group(1)}m" if vis_match else ("CAVOK" if "CAVOK" in text else "---")
    
    # 6. Température et Point de Rosée (Maintenant que FREE=3)
    temp_val = find(r"TEMPERATURE\s+(\d+)", text)
    dewp_val = find(r"DEWPOINT\s+(\d+)", text)
    temp_dewp = f"{temp_val}° / {dewp_val}°"

    # --- Génération HTML (Inchangée pour garder ton thème) ---
    # [Utilise ici ton bloc html_output avec les variables : info, rwy, qnh, zulu, lvp_tag, wind, vis, temp_dewp]
    # ...
