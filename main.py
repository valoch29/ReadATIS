import os
import re
import datetime

try:
    from faster_whisper import WhisperModel
except ImportError:
    os.system('pip install faster-whisper')
    from faster_whisper import WhisperModel

def run_atis_system():
    audio_file = "atis_recorded.wav"
    if not os.path.exists(audio_file):
        print("Erreur : Fichier audio introuvable.")
        return

    try:
        # Configuration de Whisper
        model = WhisperModel("medium", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_file, beam_size=5)
        txt = " ".join([s.text for s in segments]).upper()
        
        # Nettoyage pour l'extraction des données
        clean = txt.replace(",", " ").replace(".", " ").replace(":", " ")
        clean = " ".join(clean.split())

        def find(pattern, src, default="---"):
            res = re.findall(pattern, src)
            return res[-1] if res else default

        # Extraction des paramètres clés
        info = find(r"INFORMATION\s+([A-Z])", clean)
        qnh = find(r"(?:QNH|HPA)\s+(\d{4})", clean)
        rwy = find(r"RUNWAY\s+(\d{2})", clean)
        
        # Vent (Gestion des variations de Whisper)
        w_m = re.search(r"(\d{3})\s+(?:DEGREES|DEG)\s+(\d+)", clean)
        wind = f"{w_m.group(1)}° / {w_m.group(2)}KT" if w_m else "---"
        
        # Température et Point de rosée
        t_m = re.search(r"TEMPERATURE\s+(MINUS\s+)?(\d+)\s+DEWPOINT\s+(MINUS\s+)?(\d+)", clean)
        if t_m:
            t_val = f"{'-' if t_m.group(1) else ''}{t_m.group(2)}"
            d_val = f"{'-' if t_m.group(3) else ''}{t_m.group(4)}"
            temp = f"{t_val}° / {d_val}°"
        else:
            temp = "-- / --"
        
        # RCC et Conditions de surface
        rcc = f"{find(r'TOUCHDOWN\s+(\d)', clean)} {find(r'MIDPOINT\s+(\d)', clean)} {find(r'STOP END\s+(\d)', clean)}"
        cond = "DRY"
        if "SNOW" in clean: cond = "SNOW"
        elif "WET" in clean: cond = "WET"
        elif "ICE" in clean: cond = "ICE"

        zulu = datetime.datetime.utcnow().strftime("%H:%M")

        # Génération du HTML (Design Responsive & Dark)
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {{ --bg: #050505; --card: #121214; --accent: #ffffff; --dim: #808080; --border: #252525; }}
        body {{ background: var(--bg); color: var(--accent); font-family: 'Inter', -apple-system, sans-serif; margin: 0; padding: 10px; display: flex; justify-content: center; }}
        .container {{ width: 100%; max-width: 450px; margin-top: 10px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding: 0 5px; }}
        .airport {{ font-size: 1.1rem; font-weight: 800; letter-spacing: 1px; }}
        .zulu {{ background: #fff; color: #000; padding: 3px 10px; font-weight: 900; border-radius: 5px; font-size: 0.85rem; }}
        .info-hero {{ background: var(--card); border: 1px solid var(--border); border-radius: 15px; padding: 20px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }}
        .info-label {{ color: var(--dim); font-size: 0.75rem; text-transform: uppercase; font-weight: bold; }}
        .info-letter {{ font-size: 4.5rem; font-weight: 900; line-height: 1; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
        .tile {{ background: var(--card); border: 1px solid var(--border); border-radius: 15px; padding: 15px; }}
        .tile-label {{ color: var(--dim); font-size: 0.65rem; text-transform: uppercase; margin-bottom: 5px; font-weight: 600; }}
        .tile-val {{ font-size: 1.4rem; font-weight: 700; letter-spacing: -0.5px; }}
        .status {{ font-size: 0.75rem; background: #1a1a1c; padding: 5px 12px; border-radius: 50px; color: #fff; margin-top: 8px; display: inline-block; border: 1px solid #333; }}
        .raw-box {{ margin-top: 20px; background: #0a0a0a; border-radius: 10px; padding: 15px; font-size: 0.7rem; color: #444; line-height: 1.4; border: 1px dashed #222; text-transform: uppercase; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="airport">EETN TALLINN</div>
            <div class="zulu">{zulu}Z</div>
        </div>
        <div class="info-hero">
            <div>
                <div class="info-label">Information</div>
                <div class="status">RWY {rwy} IN USE</div>
            </div>
            <div class="info-letter">{info}</div>
        </div>
        <div class="grid">
            <div class="tile"><div class="tile-label">Wind</div><div class="tile-val">{wind}</div></div>
            <div class="tile"><div class="tile-label">QNH</div><div class="tile-val">{qnh}</div></div>
            <div class="tile"><div class="tile-label">Temp / Dew</div><div class="tile-val">{temp}</div></div>
            <div class="tile">
                <div class="tile-label">RCC / Surface</div>
                <div class="tile-val">{rcc}</div>
                <div style="font-size:0.7rem; color:var(--dim); margin-top:4px;">{cond}</div>
            </div>
        </div>
        <div class="raw-box">
            <strong>Whisper Transcript:</strong><br>{txt}
        </div>
    </div>
</body>
</html>
"""
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Transcription et mise à jour de la page réussies.")

    except Exception as e:
        print(f"Erreur lors du traitement : {e}")

if __name__ == "__main__":
    run_atis_system()
