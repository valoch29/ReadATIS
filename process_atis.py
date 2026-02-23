import os
from faster_whisper import WhisperModel

model = WhisperModel("medium.en", device="cpu", compute_type="int8")

def transcribe():
    prompt = "Tallinn Airport ATIS, Information Uniform, Runway 08, QNH 1007, Hectopascals, NOSIG."
    segments, _ = model.transcribe("atis_recorded.wav", beam_size=5, initial_prompt=prompt)
    
    full_text = " ".join([s.text for s in segments])
    
    # --- LOGIQUE DE NETTOYAGE DES RÉPÉTITIONS ---
    # On cherche le début officiel du message
    start_marker = "This is Tallinn Airport"
    if start_marker in full_text:
        # On coupe tout ce qu'il y a avant le premier "This is Tallinn Airport"
        clean_text = start_marker + full_text.split(start_marker)[1]
        
        # On cherche la fin du message "Information [Letter] out"
        if " out" in clean_text:
            # On ne garde que jusqu'au premier "out"
            clean_text = clean_text.split(" out")[0] + " out."
    else:
        clean_text = full_text # Au cas où le marqueur est mal entendu

    # Corrections finales
    clean_text = clean_text.replace("touchstone", "touchdown")
    clean_text = clean_text.replace("niner", "9")
    
    with open("atis_transcribed.txt", "w") as f:
        f.write(clean_text)

if __name__ == "__main__":
    if os.path.exists("atis_recorded.wav"):
        transcribe()
