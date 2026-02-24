import os
import re
from faster_whisper import WhisperModel

# Chargement du modèle
model = WhisperModel("medium.en", device="cpu", compute_type="int8")

def transcribe():
    # Prompt pour guider l'IA vers le vocabulaire aéronautique
    prompt = "Tallinn Airport ATIS, Information Yankee, Runway 08, QNH 1013, Hectopascals, CAVOK, NOSIG, touchdown, midpoint, stop-end, vicinity of the airport."
    segments, _ = model.transcribe("atis_recorded.wav", beam_size=5, initial_prompt=prompt)
    
    text = " ".join([s.text for s in segments])
    
    # --- NETTOYAGE ---
    corrections = {
        "West Hennessy Airport": "vicinity of the airport",
        "West Phoenix Hill": "vicinity of the airport",
        "CAVCAVOK": "CAVOK",
        "CAV OK": "CAVOK",
        "Hectopascal": "Hectopascals",
        "condition report, sorry, Matt": "condition report time",
        "climb": "time",
        "Meat point": "Midpoint",
        "meat point": "midpoint"
    }
    
    for search, replace in corrections.items():
        text = text.replace(search, replace)

    # Correction des chiffres espacés : "1, 0, 1, 3" -> "1013"
    text = re.sub(r'(\d),\s*', r'\1', text) 

    # On ne garde qu'une seule itération du message
    if "Tallinn Airport" in text:
        parts = text.split("Tallinn Airport")
        text = "Tallinn Airport " + parts[1].split("out")[0].strip() + " out."
    elif "Information" in text:
        parts = text.split("Information")
        text = "Information " + parts[1].split("out")[0].strip() + " out."

    with open("atis_transcribed.txt", "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    if os.path.exists("atis_recorded.wav"):
        transcribe()
