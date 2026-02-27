import os
import re
from faster_whisper import WhisperModel
from dictionary import replacement_dict 

def run_atis_system():
    audio_file = "atis_recorded.wav"
    if not os.path.exists(audio_file): return

    # 1. Transcription et Nettoyage
    model = WhisperModel("medium.en", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_file, beam_size=5)
    text = " ".join([s.text for s in segments]).upper()

    for wrong, right in replacement_dict.items():
        text = re.sub(rf'\b{wrong}\b', right, text)

    # 2. Fonction d'extraction sécurisée
    def find(pattern, src):
        res = re.findall(pattern, src)
        return res[-1] if res else "---"

    # 3. EXTRACTION PRÉALABLE (Zéro backslash dans les f-strings)
    info_val = find(r"INFORMATION\s+([A-Z])", text)
    rwy_val = find(r"RUNWAY\s+(\d{2})", text)
    qnh_val = find(r"QNH\s+(\d{4})", text)
    
    # Temps (Zulu)
    time_raw = find(r"TIME\s+(\d{4})", text)
    zulu_val = f"{time_raw[:2]}:{time_raw[2:]}" if time_raw != "---" else "---"

    # Vent (TDZ)
    w_dir = find(r"ZONE\s+(\d{3})", text)
    w_spd = find(r"(\d+)\s+KNOTS", text)
    wind_display = f"{w_dir}°/{w_spd}KT" if w_dir != "---" else "---"

    # Visibilité
    vis_raw = find(r"ZONE\s+(\d+)\s*M", text)
    vis_display = f"{vis_raw}m" if vis_raw != "---" else ("CAVOK" if "CAVOK" in text else "---")
    
    # RVR (Correction de la ligne 40 : on sort le find de la f-string)
    rvr_raw = find(r'RANGE.*?ZONE\s+(\d+)', text)
    rvr_val = f"RVR {rvr_raw}m" if "RANGE" in text and rvr_raw != "---" else ""

    # Temp/Dewp
    t_val = find(r"TEMPERATURE\s+(\d+)", text)
    d_val = find(r"DEWPOINT\s+(\d+)", text)
    temp_dewp_display = f"{t_val}° / {d_val}°"
    
    # RCC et Contaminants
    rcc_val = "5/5/5" if "TOUCHDOWN 5" in text else "---"
    contam_val = "WET / WET / WET" if "WET" in text else "---"

    # LVP Status
    lvp_html = '<span class="lvp-alert">⚠️ LVP ACTIVE</span>' if "LVP ACTIVE" in text else ""

    # 4. Dictionnaire de données pour le template
    data = {
        "INFO": info_val,
        "ZULU": zulu_val,
        "RWY": rwy_val,
        "QNH": qnh_val,
        "WIND": wind_display,
        "VIS": vis_display,
        "RVR": rvr_val,
        "TEMP_DEWP": temp_dewp_display,
        "RCC": rcc_val,
        "CONTAM": contam_val,
        "LVP_TAG": lvp_html,
        "RAW_TEXT": text
    }

    # 5. Injection dans le template
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()

for key, value in data.items():
            # Construction manuelle de la balise {{KEY}}
            placeholder = "{{" + key + "}}"
            # Remplacement forcé
            html_content = html_content.replace(placeholder, str(value))

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)

if __name__ == "__main__":
    run_atis_system()
