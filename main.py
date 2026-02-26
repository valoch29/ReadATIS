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

    # 2. Nettoyage de base et application du dictionnaire
    text = raw_text.replace(",", " ").replace(".", " ")
    for wrong, right in replacement_dict.items():
        text = re.sub(rf'\b{wrong}\b', right, text)
    text = " ".join(text.split())

    # 3. Extraction des données
    def find(pattern, src):
        res = re.findall(pattern, src)
        return res[-1] if res else "---"

    info = find(r"INFORMATION\s+([A-Z])", text)
    rwy  = find(r"RUNWAY\s+(\d{2})", text)
    qnh  = find(r"(?:QNH|HPA|HECTOPASCALS)\s+(\d{4})", text)
    
    # Heure de l'ATIS (ex: TIME 1052)
    atis_time = find(r"TIME\s+(\d{4})", text)
    if atis_time != "---":
        atis_time = f"{atis_time[:2]}:{atis_time[2:]}"

    # Vent
    w_match = re.search(r"(\d{3})\s+DEGREES\s+(\d+)\s+KNOTS", text)
    wind = f"{w_match.group(1)}° / {w_match.group(2)} KT" if w_match else "---"

    # 4. Découpe : Une seule itération de "THIS IS TALLINN" jusqu'à la fin de la boucle
    # On cherche l'amorce du message
    start_trigger = "THIS IS TALLINN"
    start_idx = text.find(start_trigger)
    
    if start_idx != -1:
        # On prend tout à partir du premier "THIS IS TALLINN"
        iteration = text[start_idx:]
        # On cherche si le message recommence plus loin pour couper la répétition
        # On cherche la 2ème occurrence de "THIS IS TALLINN" (au moins 50 caractères plus loin)
        next_iter = iteration.find(start_trigger, 50)
        if next_iter != -1:
            clean_display_text = iteration[:next_iter].strip()
        else:
            clean_display_text = iteration.strip()
    else:
        # Fallback si l'amorce n'est pas trouvée : on garde le texte tel quel
        clean_display_text = text

    # 5. Génération HTML (Design Monochrome)
    html_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {{ --bg: #000000; --card: #111111; --border: #333333; --text: #ffffff; --dim: #666666; }}
        body {{ background: var(--bg); color: var(--text); font-family: 'Inter', -apple-system, sans-serif; margin: 0; padding: 20px; display: flex; justify-content: center; }}
        .container {{ width: 100%; max-width: 450px; }}
        .header {{ display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }}
        .zulu {{ font-size: 1.2rem; font-weight: 700; letter-spacing: 1px; }}
        .info-box {{ background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 30px; text-align: center; margin-bottom: 15px; }}
        .info-letter {{ font-size: 7rem; font-weight: 900; line-height: 1; display: block; color: var(--text); }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1px; background: var(--border); border: 1px solid var(--border); border-radius: 4px; overflow: hidden; }}
        .tile {{ background: var(--card); padding: 20px; }}
        .label {{ color: var(--dim); font-size: 0.65rem; text-transform: uppercase; margin-bottom: 8px; font-weight: 800; letter-spacing: 1.5px; }}
        .val {{ font-size: 1.3rem; font-weight: 700; }}
        .raw {{ margin-top: 40px; font-size: 0.85rem; color: var(--text); line-height: 1.6; text-align: justify; border-left: 2px solid var(--border); padding-left: 15px; }}
        .raw strong {{ color: var(--dim); display: block; font-size: 0.7rem; letter-spacing: 2px; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="font-weight: 900; font-size: 0.9rem; letter-spacing: 2px;">EETN TALLINN</div>
            <div class="zulu">{ZULU}Z</div>
        </div>
        <div class="info-box">
            <div class="label" style="margin-bottom: 0;">Information</div>
            <span class="info-letter">{INFO}</span>
        </div>
        <div class="grid">
            <div class="tile"><div class="label">Runway</div><div class="val">{RWY}</div></div>
            <div class="tile"><div class="label">QNH</div><div class="val">{QNH}</div></div>
            <div class="tile"><div class="label">Wind</div><div class="val">{WIND}</div></div>
            <div class="tile"><div class="label">Visibility</div><div class="val">CAVOK</div></div>
        </div>
        <div class="raw">
            <strong>TRANSCRIPTION</strong>
            {RAW}
        </div>
    </div>
</body>
</html>
"""
    final_html = html_template.format(
        ZULU=atis_time if atis_time != "---" else datetime.datetime.utcnow().strftime("%H:%M"),
        INFO=info[0] if info != "---" else "---",
        RWY=rwy,
        QNH=qnh,
        WIND=wind,
        RAW=clean_display_text
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    run_atis_system()
