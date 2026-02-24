import os
from faster_whisper import WhisperModel

model = WhisperModel("medium.en", device="cpu", compute_type="int8")

def transcribe():
    prompt = "Tallinn Airport ATIS, Information India, Runway 08, QNH 1009, Hectopascals, CAVOK, NOSIG, bird activity in the vicinity of the airport."
    segments, _ = model.transcribe("atis_recorded.wav", beam_size=5, initial_prompt=prompt)
    
    full_text = " ".join([s.text for s in segments])
    
    # --- LOGIQUE DE NETTOYAGE DES DOUBLONS ---
    # Le message ATIS commence souvent par "This is Tallinn Airport" ou "Tallinn Airport"
    # On cherche à ne garder qu'une seule itération.
    start_marker = "Tallinn Airport"
    if start_marker in full_text:
        # On prend à partir du premier marqueur
        parts = full_text.split(start_marker)
        # On ne garde que le contenu entre le 1er et le 2e "Tallinn Airport" (s'il existe)
        if len(parts) > 2:
            clean_text = start_marker + parts[1]
        else:
            clean_text = full_text
    else:
        clean_text = full_text

    # --- DICTIONNAIRE DE CORRECTIONS ---
    corrections = {
        "West Phoenix Hill": "the vicinity of the",
        "West Phoenix Hill Airport": "the vicinity of the airport",
        "vicinity of airport": "vicinity of the airport",
        "touchstone": "touchdown",
        "cable K": "CAVOK",
        "niner": "9",
        "hecto pascals": "hectopascals",
        "Q and H": "QNH"
    }
    
    for search, replace in corrections.items():
        clean_text = clean_text.replace(search, replace)
    
    # Nettoyage final des espaces doubles
    clean_text = " ".join(clean_text.split())
    
    with open("atis_transcribed.txt", "w", encoding="utf-8") as f:
        f.write(clean_text)

if __name__ == "__main__":
    if os.path.exists("atis_recorded.wav"):
        transcribe()