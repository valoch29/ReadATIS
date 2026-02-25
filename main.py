import os
import sys
import re

# Installation forcée si absent (Sécurité GitHub Actions)
try:
    from faster_whisper import WhisperModel
except ImportError:
    os.system('pip install faster-whisper')
    from faster_whisper import WhisperModel

# Chargement sécurisé du dictionnaire
replacement_dict = {}
if os.path.exists("dictionary.py"):
    try:
        with open("dictionary.py", "r", encoding="utf-8") as f:
            local_vars = {}
            exec(f.read(), {}, local_vars)
            replacement_dict = local_vars.get('replacement_dict', {})
    except Exception:
        pass

def run_atis_system():
    audio_file = "atis_recorded.wav"
    if not os.path.exists(audio_file):
        print("Audio introuvable.")
        return

    try:
        # Initialisation du modèle (Optimisé CPU pour GitHub)
        model = WhisperModel("small", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_file, beam_size=5)
        raw_text = " ".join([s.text for s in segments]).upper().strip()
        
        # 1. Application du dictionnaire
        clean_text = raw_text
        for word, replacement in sorted(replacement_dict.items(), key=lambda x: len(x[0]), reverse=True):
            clean_text = clean_text.replace(word.upper(), replacement)

        # 2. Nettoyage : On ne garde qu'une seule itération du message
        # On cherche à couper dès que le message recommence (souvent par "THIS IS TALLINN")
        if "THIS IS TALLINN" in clean_text:
            parts = clean_text.split("THIS IS TALLINN")
            # On prend la dernière partie complète (souvent la mieux enregistrée)
            processed_text = "THIS IS TALLINN" + parts[-1]
            # Si le mot "OUT" est présent à la fin du message, on coupe tout ce qui suit
            if "OUT" in processed_text:
                processed_text = processed_text.split("OUT")[0] + "OUT."
        else:
            processed_text = clean_text

        # 3. Extraction des paramètres (Regex)
        info = re.search(r"INFORMATION\s+([A-Z])", processed_text)
        rwy = re.search(r"RUNWAY\s+(\d+)", processed_text)
        qnh = re.search(r"QNH\s+(\d+)", processed_text)
        wind = re.search(r"(\d+)\s+DEGREES\s+(\d+)\s+KNOTS", processed_text)
        temp_match = re.search(r"TEMPERATURE\s+(?:MINUS\s+)?(\d+)\s+DEWPOINT\s+(?:MINUS\s+)?(\d+)", processed_text)
        cond = re.search(r"TOUCHDOWN\s*,\s*(\d)\s+MIDPOINT\s*,\s*(\d)\s+STOP END\s*,\s*(\d)", processed_text)

        # Formatage des valeurs
        val_info = info.group(1) if info else "-"
        val_r