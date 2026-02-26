import os
import re
import datetime
from faster_whisper import WhisperModel
# On importe la fonction ou le dictionnaire depuis ton fichier à part
from dictionary import corrections 

def run_atis_system():
    audio_file = "atis_recorded.wav"
    if not os.path.exists(audio_file):
        print("Fichier audio manquant.")
        return

    # 1. Transcription
    model = WhisperModel("medium.en", device="cpu", compute_type="int8")
    prompt = "Tallinn Airport ATIS, Information, Runway 08, QNH 1021, Hectopascals, CAVOK, NOSIG, touchdown, midpoint, stop-end, frost, wet, bird activity, knots, degrees."
    segments, _ = model.transcribe(audio_file, beam_size=5, initial_prompt=prompt)
    raw_text = " ".join([s.text for s in segments]).upper()

    # 2. Application du dictionnaire externe
    clean_text = raw_text
    for wrong, right in corrections.items():
        clean_text = re.sub(rf'\b{wrong}\b', right, clean_text)
    clean_text = " ".join(clean_text.split())

    # 3. Extraction des données
    def find(pattern, src):
        res = re.findall(pattern, src)
        return res[-1] if res else "---"

    info = find(r"INFORMATION\s+([A-Z])", clean_text)
    rwy  = find(r"RUNWAY\s+(\d{2})", clean_text)
    qnh  = find(r"(?:QNH|HECTOPASCALS)\s+(\d{4})", clean_text)
    
    # Vent
    w_match = re.search(r"(\d{3})\s+DEGREES\s+(\d+)\s+KNOTS", clean_text)
    wind = f"{w_match.group(1)} / {w_match.group(2)} KT" if w_match else "---"

    zulu = datetime.datetime.utcnow().strftime("%H:%M")

    # 4. Génération HTML (Template propre)
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ background: #000; color: #fff; font-family: monospace; padding: 20px; }}
        .box {{ border: 2px solid #fff; padding: 20px; max-width: 400px; margin: auto; }}
        .big {{ font-size: 5rem; text-align: center; margin: 15px 0; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
        .item {{ background: #111; padding: 10px; border: 1px solid #333; }}
    </style>
</head>
<body>
    <div class="box">
        <div style="display:flex; justify-content:space-between"><b>EETN TALLINN</b> <span>{ZULU}Z</span></div>
        <div class="big">{INFO}</div>
        <div class="grid">
            <div class="item">RWY: {RWY}</div>
            <div class="item">QNH: {QNH}</div>
            <div class="item">WIND: {WIND}</div>
            <div class="item">VIS: CAVOK</div>
        </div>
        <div style="margin-top:20px; font-size:0.7rem; color:#444;">{RAW}</div>
    </div>
</body>
</html>
"""
    # Remplissage du template
    final_html = html_template.format(
        ZULU=zulu, INFO=info, RWY=rwy, QNH=qnh, WIND=wind, RAW=clean_text
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    print("Page index.html générée avec succès.")

if __name__ == "__main__":
    run_atis_system()
