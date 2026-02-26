import os
import re
import datetime
from faster_whisper import WhisperModel
from dictionary import replacement_dict 

def run_atis_system():
    audio_file = "atis_recorded.wav"
    if not os.path.exists(audio_file):
        return

    # 1. Transcription
    model = WhisperModel("medium.en", device="cpu", compute_type="int8")
    prompt = "Tallinn Airport ATIS, Information, Runway 08, QNH 1021, Hectopascals, CAVOK, NOSIG, touchdown, midpoint, stop-end, frost, wet, bird activity, knots, degrees."
    segments, _ = model.transcribe(audio_file, beam_size=5, initial_prompt=prompt)
    raw_text = " ".join([s.text for s in segments]).upper()

    # 2. Nettoyage agressif (On vire les virgules et points pour faciliter l'extraction)
    clean_text = raw_text.replace(",", " ").replace(".", " ")
    for wrong, right in replacement_dict.items():
        clean_text = re.sub(rf'\b{wrong}\b', right, clean_text)
    
    clean_text = " ".join(clean_text.split())

    # 3. Extraction (Regex assouplies)
    def find(pattern, src):
        res = re.findall(pattern, src)
        return res[-1] if res else "---"

    # \s* permet de gérer l'absence ou la présence d'espaces
    info = find(r"INFORMATION\s+([A-Z])", clean_text)
    rwy  = find(r"RUNWAY\s+(\d{2})", clean_text)
    qnh  = find(r"(?:QNH|HPA|HECTOPASCALS)\s+(\d{4})", clean_text)
    
    # Vent : Gestion plus flexible du format "190 DEGREES 20 KNOTS"
    w_match = re.search(r"(\d{3})\s+DEGREES\s+(\d+)\s+KNOTS", clean_text)
    if not w_match: # Fallback au cas où
        w_match = re.search(r"(\d{3})\s*°?\s*(\d+)\s*KT", clean_text)
    
    wind = f"{w_match.group(1)}° / {w_match.group(2)} KT" if w_match else "---"

    zulu = datetime.datetime.utcnow().strftime("%H:%M")

    # 4. Génération HTML (Design conservé)
    html_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {{ --bg: #0a0a0c; --card: #16161a; --accent: #ffffff; --dim: #828282; }}
        body {{ background: var(--bg); color: var(--accent); font-family: system-ui, sans-serif; margin: 0; padding: 15px; display: flex; justify-content: center; }}
        .container {{ width: 100%; max-width: 450px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
        .zulu {{ background: #fff; color: #000; padding: 3px 10px; font-weight: 900; border-radius: 4px; font-size: 0.9rem; }}
        .info-box {{ background: var(--card); border: 1px solid #333; border-radius: 12px; padding: 25px; text-align: center; margin-bottom: 15px; }}
        .info-letter {{ font-size: 5rem; font-weight: 900; line-height: 1; display: block; color: #00ff41; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
        .tile {{ background: var(--card); border: 1px solid #2a2a2a; border-radius: 12px; padding: 15px; }}
        .label {{ color: var(--dim); font-size: 0.7rem; text-transform: uppercase; margin-bottom: 5px; font-weight: bold; }}
        .val {{ font-size: 1.4rem; font-weight: bold; }}
        .raw {{ margin-top: 30px; font-size: 0.7rem; color: #444; text-transform: uppercase; line-height: 1.4; border-top: 1px solid #222; padding-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="font-weight: 800; letter-spacing: 1px;">EETN TALLINN</div>
            <div class="zulu">{ZULU}Z</div>
        </div>
        <div class="info-box">
            <span class="label">Information</span>
            <span class="info-letter">{INFO}</span>
        </div>
        <div class="grid">
            <div class="tile"><div class="label">Runway</div><div class="val">{RWY}</div></div>
            <div class="tile"><div class="label">QNH</div><div class="val">{QNH}</div></div>
            <div class="tile"><div class="label">Wind</div><div class="val">{WIND}</div></div>
            <div class="tile"><div class="label">Visibility</div><div class="val">CAVOK</div></div>
        </div>
        <div class="raw"><strong>Transcription:</strong><br>{RAW}</div>
    </div>
</body>
</html>
"""
    final_html = html_template.format(
        ZULU=zulu, INFO=info, RWY=rwy, QNH=qnh, WIND=wind, RAW=clean_text
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    run_atis_system()
