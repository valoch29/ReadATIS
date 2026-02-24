import os
from faster_whisper import WhisperModel

model = WhisperModel("medium.en", device="cpu", compute_type="int8")

def transcribe():
    prompt = "Tallinn Airport ATIS, Information Uniform, Runway 08, QNH 1012, Hectopascals, CAVOK, NOSIG, touchdown, midpoint, stop-end."
    segments, _ = model.transcribe("atis_recorded.wav", beam_size=5, initial_prompt=prompt)
    
    full_text = " ".join([s.text for s in segments])
    
    # Corrections des erreurs phonétiques de l'IA
    corrections = {{
        "business travelling airport": "This is Tallinn Airport",
        "meat point": "midpoint",
        "pack down": "touchdown",
        "top end": "stop-end",
        "OK": "CAVOK",
        "Cable K": "CAVOK",
        "West Phoenix Hill": "vicinity of the",
        "niner": "9"
    }}
    
    clean_text = full_text
    for search, replace in corrections.items():
        clean_text = clean_text.replace(search, replace)

    # On ne garde que la première itération du message pour éviter les répétitions
    if "This is Tallinn Airport" in clean_text:
        parts = clean_text.split("This is Tallinn Airport")
        if len(parts) > 1:
            clean_text = "This is Tallinn Airport" + parts[1].split("out.")[0] + "out."

    with open("atis_transcribed.txt", "w", encoding="utf-8") as f:
        f.write(clean_text)

if __name__ == "__main__":
    if os.path.exists("atis_recorded.wav"):
        transcribe()
