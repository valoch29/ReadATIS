import os
from faster_whisper import WhisperModel

model = WhisperModel("medium.en", device="cpu", compute_type="int8")

def transcribe():
    prompt = "Tallinn Airport ATIS, Information, Runway, QNH, Hectopascals, CAVOK, NOSIG, touchdown, midpoint, stop-end."
    segments, _ = model.transcribe("atis_recorded.wav", beam_size=5, initial_prompt=prompt)
    
    text = " ".join([s.text for s in segments])
    
    corrections = {
        "business travelling airport": "This is Tallinn Airport",
        "meat point": "midpoint",
        "pack down": "touchdown",
        "top end": "stop-end",
        "OK": "CAVOK",
        "West Phoenix Hill": "vicinity of the",
        "niner": "9",
        "  ": " "
    }
    
    for search, replace in corrections.items():
        text = text.replace(search, replace)

    # On essaye de ne garder qu'un seul message propre
    if "This is Tallinn Airport" in text:
        text = "This is Tallinn Airport" + text.split("This is Tallinn Airport")[1].split("out")[0] + " out"

    with open("atis_transcribed.txt", "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    if os.path.exists("atis_recorded.wav"):
        transcribe()
