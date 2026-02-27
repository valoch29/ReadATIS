import os
import re
from faster_whisper import WhisperModel
from dictionary import replacement_dict 

def run_atis_system():
    audio_file = "atis_recorded.wav"
    if not os.path.exists(audio_file): return

    # 1. Transcription
    model = WhisperModel("medium.en", device="cpu", compute_type="int8")
    prompt = "Tallinn Airport ATIS, Information Delta, Runway 26, QNH 1010, RCC 5/5/5, LVP ACTIVE, visibility 700m, RVR 1100m."
    segments, _ = model.transcribe(audio_file, beam_size=5, initial_prompt=prompt)
    text = " ".join([s.text for s in segments]).upper()

    # 2. Nettoyage
    for wrong, right in replacement_dict.items():
        text = re.sub(rf'\b{wrong}\b', right, text)

    # 3. Fonction d'extraction sécurisée
    def find(pattern, src):
        res = re.findall(pattern, src)
        return res[-1] if res else "---"

    # 4. Préparation des variables (SANS BACKSLASH pour éviter l'erreur)
    info = find(r"INFORMATION\s+([A-Z])", text)
    rwy = find(r"RUNWAY\s+(\d{2})", text)
    qnh = find(r"QNH\s+(\d{4})", text)
    
    atis_time = find(r"TIME\s+(\d{4})", text)
    zulu = f"{atis_time[:2]}:{atis_time[2:]}" if atis_time != "---" else "---"

    lvp_tag = '<span class="lvp-alert">⚠️ LVP ACTIVE</span>' if "LVP ACTIVE" in text else ""
    
    vis_match = re.search(r"TOUCHDOWN ZONE\s+(\d+)\s+METERS", text)
    vis = f"{vis_match.group(1)}m" if vis_match else ("CAVOK" if "CAVOK" in text else "---")
    
    rvr_match = re.search(r"VISUAL RANGE.*?TOUCHDOWN ZONE\s+(\d+)", text)
    rvr = f"RVR {rvr_match.group(1)}m" if rvr_match else ""

    temp_val = find(r"TEMPERATURE\s+(\d+)", text)
    dewp_val = find(r"DEWPOINT\s+(\d+)", text)
    temp_dewp = f"{temp_val}° / {dewp_val}°"

    # Vent
    w_match = re.search(r"TOUCHDOWN ZONE\s+(\d{3})(?:\s+DEGREES)?\s+(\d+)\s+KNOTS", text)
    wind = f"{w_match.group(1)}°/{w_match.group(2)}KT" if w_match else "---"

    # 5. Injection dans le HTML (On garde ton thème !)
    html_output = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <style>
        :root {{ --bg: #000; --card: #0d0d0d; --border: #222; --text: #fff; --dim: #777; }}
        body {{ background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; padding: 25px; display: flex; justify-content: center; }}
        .container {{ width: 100%; max-width: 420px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; font-size: 0.8rem; color: var(--dim); font-weight: 800; }}
        .info-section {{ text-align: center; margin-bottom: 25px; background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 15px; }}
        .info-letter {{ font-size: 6rem; font-weight: 900; line-height: 1; margin: 0; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
        .tile {{ background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 18px; }}
        .label {{ color: var(--dim); font-size: 0.6rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 700; }}
        .val {{ font-size: 1.2rem; font-weight: 700; }}
        .lvp-alert {{ color: #ff4444; border: 1px solid #ff4444; padding: 2px 8px; border-radius: 5px; animation: blink 2s infinite; font-size: 0.7rem; }}
        @keyframes blink {{ 0% {{opacity: 1;}} 50% {{opacity: 0.3;}} 100% {{opacity: 1;}} }}
        .raw {{ margin-top: 40px; font-size: 0.7rem; color: #555; text-align: justify; text-transform: uppercase; border-top: 1px solid #222; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><span>EETN TALLINN</span> {lvp_tag} <span>{zulu}Z</span></div>
        <div class="info-section"><span style="color:var(--dim); text-transform:uppercase; font-size:0.7rem; letter-spacing:3px;">Information</span><div class="info-letter">{info}</div></div>
        <div class="grid">
            <div class="tile"><div class="label">Runway</div><div class="val">{rwy}</div></div>
            <div class="tile"><div class="label">QNH</div><div class="val">{qnh} hPa</div></div>
            <div class="tile"><div class="label">Wind (TDZ)</div><div class="val">{wind}</div></div>
            <div class="tile"><div class="label">Visibility</div><div class="val">{vis} <span style="font-size:0.7rem; color:var(--dim)">{rvr}</span></div></div>
            <div class="tile"><div class="label">Temp / Dewp</div><div class="val">{temp_dewp}</div></div>
            <div class="tile"><div class="label">RCC</div><div class="val">5/5/5</div></div>
        </div>
        <div class="raw">{text}</div>
    </div>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_output)

if __name__ == "__main__":
    run_atis_system()
