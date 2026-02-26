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
    if not os.path.exists(audio_file): return

    try:
        # Utilisation du modèle Medium pour ne rien rater
        model = WhisperModel("medium", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_file, beam_size=5)
        txt = " ".join([s.text for s in segments]).upper()
        
        # Nettoyage pour faciliter l'extraction (on enlève les virgules et points)
        clean_txt = txt.replace(",", " ").replace(".", " ")
        clean_txt = " ".join(clean_txt.split())

        def find(pattern, src, default="---"):
            res = re.findall(pattern, src)
            return res[-1] if res else default

        # Extraction avec regex flexibles
        info = find(r"INFORMATION\s+([A-Z])", clean_txt)
        qnh = find(r"(?:QNH|HPA)\s+(\d{4})", clean_txt)
        rwy = find(r"RUNWAY\s+(\d{2})", clean_txt)
        
        # Vent (ex: 160 DEGREES 5 KNOTS)
        w_m = re.search(r"(\d{3})\s+(?:DEGREES|DEG)\s+(\d+)", clean_txt)
        wind = f"{w_m.group(1)}° / {w_m.group(2)}KT" if w_m else "--- / --KT"
        
        # Température
        t_m = re.search(r"TEMPERATURE\s+(MINUS\s+)?(\d+)\s+DEWPOINT\s+(MINUS\s+)?(\d+)", clean_txt)
        temp = f"{('-' if t_m.group(1) else '') + t_m.group(2)}° / {('-' if t_m.group(3) else '') + t_m.group(4)}°" if t_m else "-- / --"
        
        # RCC (Basé sur ton texte : 5 MIDPOINT 5 STOP END 5)
        td = find(r"TOUCHDOWN\s+(\d)", clean_txt, "6")
        mp = find(r"MIDPOINT\s+(\d)", clean_txt, "6")
        se = find(r"STOP END\s+(\d)", clean_txt, "6")
        rcc = f"{td} / {mp} / {se}"

        zulu = datetime.datetime.utcnow().strftime("%d %b %H:%M UTC").upper()

        # HTML NOIR & BLANC
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ background: #000; color: #fff; font-family: monospace; padding: 20px; display: flex; justify-content: center; }}
                .card {{ width: 100%; max-width: 500px; border: 2px solid #fff; padding: 20px; }}
                .grid {{ display: grid; grid-template-columns: 1fr 1fr; border: 1px solid #fff; margin-top: 20px; }}
                .cell {{ border: 1px solid #fff; padding: 15px; }}
                .label {{ font-size: 0.7rem; color: #888; text-transform: uppercase; }}
                .value {{ font-size: 1.8rem; font-weight: bold; }}
                .info {{ font-size: 3rem; border: 3px solid #fff; padding: 0 10px; }}
                .raw {{ margin-top: 20px; font-size: 0.7rem; color: #444; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:1.5rem; font-weight:bold;">EETN TALLINN</span>
                    <span style="color:#888;">{zulu}</span>
                </div>
                <div class="grid">
                    <div class="cell"><div class="label">Information</div><span class="info">{info}</span></div>
                    <div class="cell"><div class="label">Runway</div><div class="value">{rwy}</div></div>
                    <div class="cell"><div class="label">Wind</div><div class="value">{wind}</div></div>
                    <div class="cell"><div class="label">QNH</div><div class="value">{qnh}</div></div>
                    <div class="cell"><div class="label">Temp/Dew</div><div class="value">{temp}</div></div>
                    <div class="cell"><div class="label">RCC</div><div class="value">{rcc}</div></div>
                </div>
                <div class="raw">RAW: {txt}</div>
            </div>
        </body>
        </html>
        """
        with open("index.html", "w", encoding="utf-8") as f: f.write(html)
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    run_atis_system()
