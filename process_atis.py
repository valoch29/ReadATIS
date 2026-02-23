import os
from faster_whisper import WhisperModel

# Modèle Medium pour la fidélité (Qualité identique à ma transcription)
model = WhisperModel("medium.en", device="cpu", compute_type="int8")

def transcribe():
    prompt = "Tallinn Airport ATIS, Information, Runway, QNH, Hectopascals, Temperature, Dewpoint, NOSIG."
    segments, _ = model.transcribe("atis_recorded.wav", beam_size=5, initial_prompt=prompt)
    
    text = " ".join([s.text for s in segments])
    
    # Nettoyage des erreurs courantes
    text = text.replace("hecto pascals", "hectopascals").replace("Q and H", "QNH")
    
    with open("atis_transcribed.txt", "w") as f:
        f.write(text)

if __name__ == "__main__":
    if os.path.exists("atis_recorded.wav"):
        transcribe()
