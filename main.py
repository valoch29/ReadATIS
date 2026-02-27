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

    # 2. Extraction (comme précédemment)
    def find(pattern, src):
        res = re.findall(pattern, src)
        return res[-1] if res else "---"

    atis_time = find(r"TIME\s+(\d{4})", text)
    temp_val = find(r"TEMPERATURE\s+(\d+)", text)
    dewp_val = find(r"DEWPOINT\s+(\d+)", text)
    
    # 3. Préparation du dictionnaire de données
    data = {
        "INFO": find(r"INFORMATION\s+([A-Z])", text),
        "ZULU": f"{atis_time[:2]}:{atis_time[2:]}" if atis_time != "---" else "---",
        "RWY": find(r"RUNWAY\s+(\d{2})", text),
        "QNH": find(r"QNH\s+(\d{4})", text),
        "WIND": f"{find(r'ZONE\s+(\d{3})', text)}°/{find(r'(\d+)\s+KNOTS', text)}KT",
        "VIS": f"{find(r'ZONE\s+(\d+)\s*M', text)}m",
        "RVR": f"RVR {find(r'RANGE.*?ZONE\s+(\d+)', text)}m" if "RANGE" in text else "",
        "TEMP_DEWP": f"{temp_val}° / {dewp_val}°",
        "LVP_TAG": '<span class="lvp-alert">⚠️ LVP ACTIVE</span>' if "LVP ACTIVE" in text else "",
        "RAW_TEXT": text
    }

    # 4. Chargement du template et Remplacement
    with open("template.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    for key, value in data.items():
        html_content = html_content.replace(f"{{{{{key}}}}}", str(value))

    # 5. Sauvegarde
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    run_atis_system()
