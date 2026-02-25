import os
import re
from faster_whisper import WhisperModel

model = WhisperModel("medium.en", device="cpu", compute_type="int8")

def transcribe():
    prompt = "Tallinn Airport ATIS, Information, Runway 08, QNH 1021, Hectopascals, CAVOK, NOSIG, touchdown, midpoint, stop-end, frost, wet, bird activity, knots, degrees."
    segments, _ = model.transcribe("atis_recorded.wav", beam_size=5, initial_prompt=prompt)
    raw_text = " ".join([s.text for s in segments]).upper()

    # --- LE DICTIONNAIRE ULTIME DE CORRECTIONS ---
    corrections = {
        # Chiffres et Phonétique Aéro
        "NINER": "9", "ZE-RO": "0", "WUN": "1", "TOO": "2", "TREE": "3", 
        "FOW-ER": "4", "FIFE": "5", "SIX": "6", "SEV-EN": "7", "AIT": "8",
        "ZERO": "0", "ONE": "1", "TWO": "2", "THREE": "3", "FOUR": "4", 
        "FIVE": "5", "SEVEN": "7", "EIGHT": "8", "NINE": "9",
        
        # Météo & Vent
        "THRUST": "FROST", "TRUST": "FROST", "FORST": "FROST", "FROSTED": "FROST", "FRONT": "FROST",
        "NOS": "KNOTS", "NOTS": "KNOTS", "NOT": "KNOTS", "KNOT": "KNOTS",
        "CABLE K": "CAVOK", "CABO K": "CAVOK", "COVER K": "CAVOK", "KO": "CAVOK", "CAV OK": "CAVOK",
        "DEGREES": "DEGREES", "DEGREE": "DEGREES",
        "DUE POINT": "DEWPOINT", "DO POINT": "DEWPOINT", "DEW POINT": "DEWPOINT",
        "NO SEEK": "NOSIG", "NO SICK": "NOSIG", "NO SEAT": "NOSIG", "NO SIGN": "NOSIG",
        
        # Piste & État (RCC)
        "PACK DOWN": "TOUCHDOWN", "TOUCH STONE": "TOUCHDOWN", "TOUCH DOWN": "TOUCHDOWN", "TOUCHDOWNED": "TOUCHDOWN",
        "MEAT POINT": "MIDPOINT", "MID POINT": "MIDPOINT", "MADE POINT": "MIDPOINT", "MID-POINT": "MIDPOINT",
        "TOP END": "STOP END", "STEP END": "STOP END", "STOP-END": "STOP END", "STOPEND": "STOP END",
        "WEST": "WET", "WASTE": "WET", "WEIGHT": "WET", "WAIT": "WET",
        
        # Lieux & Général
        "BUSINESS TRAVELLING": "THIS IS TALLINN", "BUSINESS TRAVELING": "THIS IS TALLINN",
        "PHOENIX HILL": "VICINITY OF THE", "PHOENIX": "VICINITY",
        "HECTOPASCALSS": "HECTOPASCALS", "HECTO PASCALS": "HECTOPASCALS", "HP": "HECTOPASCALS",
        "INFORMATION": "INFORMATION", "INFO": "INFORMATION"
    }

    clean_text = raw_text
    for wrong, right in corrections.items():
        # Utilisation de regex pour ne remplacer que les mots entiers (évite de casser "80" en "AIT0")
        clean_text = re.sub(rf'\b{wrong}\b', right, clean_text)

    # Nettoyage final : suppression des espaces multiples
    clean_text = " ".join(clean_text.split())

    with open("atis_transcribed.txt", "w", encoding="utf-8") as f:
        f.write(clean_text)

if __name__ == "__main__":
    if os.path.exists("atis_recorded.wav"):
        transcribe()
