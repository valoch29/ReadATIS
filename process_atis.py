import os
from faster_whisper import WhisperModel

# Modèle Medium pour la fidélité
model = WhisperModel("medium.en", device="cpu", compute_type="int8")

def transcribe():
    # Prompt enrichi avec CAVOK pour aider l'IA
    prompt = "Tallinn Airport ATIS, Information, Runway, QNH, Hectopascals, CAVOK, NOSIG, touchdown."
    segments, _ = model.transcribe("atis_recorded.wav", beam_size=5, initial_prompt=prompt)
    
    full_text = " ".join([s.text for s in segments])
    
    # --- LOGIQUE DE NETTOYAGE ---
    start_marker = "This is Tallinn Airport"
    if start_marker in full_text:
        clean_text = start_marker + full_text.split(start_marker)[1]
        if " out" in clean_text:
            clean_text = clean_text.split(" out")[0] + " out."
    else:
        clean_text = full_text

    # --- DICTIONNAIRE DE CORRECTIONS TECHNIQUES ---
    corrections = {
        "cable K": "CAVOK",
        "cable k": "CAVOK",
        "Cable K": "CAVOK",
        "touchstone": "touchdown",
        "niner": "9",
        "hecto pascals": "hectopascals",
        "Q and H": "QNH"
    }
    
    for search, replace in corrections.items():
        clean_text = clean_text.replace(search, replace)
    
    with open("atis_transcribed.txt", "w") as f:
        f.write(clean_text)

if __name__ == "__main__":
    if os.path.exists("atis_recorded.wav"):
        transcribe()
