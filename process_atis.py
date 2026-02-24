import os
from faster_whisper import WhisperModel

model = WhisperModel("medium.en", device="cpu", compute_type="int8")

def transcribe():
    prompt = "Tallinn Airport ATIS, Information, Runway, QNH, Hectopascals, CAVOK, NOSIG, touchdown, midpoint, stop-end."
    segments, _ = model.transcribe("atis_recorded.wav", beam_size=5, initial_prompt=prompt)
    
    text = " ".join([s.text for s in segments])
    
    corrections = {
        "business, Tallinn Airport": "Tallinn Airport",
        "business Tallinn Airport": "Tallinn Airport",
        "CAVCAVOK": "CAVOK",
        "CAV OK": "CAVOK",
        "Meat point": "Midpoint",
        "meat point": "midpoint",
        "Hectopascal": "Hectopascals",
        "niner": "9",
        "NOS, ": "", 
        "0, 8, 5, 3": "0853",
        "1, 1, 2, 0": "1120"
    }
    
    for search, replace in corrections.items():
        text = text.replace(search, replace)

    if "Tallinn Airport" in text:
        parts = text.split("Tallinn Airport")
        if len(parts) > 1:
            text = "Tallinn Airport" + parts[1].split("out")[0] + " out"

    with open("atis_transcribed.txt", "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    if os.path.exists("atis_recorded.wav"):
        transcribe()
