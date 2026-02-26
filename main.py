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
        return

    try:
        # 1. Transcription
        model = WhisperModel("medium", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_file, beam_size=5)
        txt = " ".join([s.text for s in segments]).upper()
        
        # 2. Nettoyage simple
        clean = txt.replace(",", " ").replace(".", " ").replace(":", " ")
        clean = " ".join(clean.split())

        # 3. Extraction (Variables isolées pour éviter les erreurs de f-string)
        def find(pattern, src):
            res = re.findall(pattern, src)
            return res[-1] if res else "---"

        info = find(r"INFORMATION\s+([A-Z])", clean)
        qnh  = find(r"QNH\s+(\d{4})", clean)
        rwy  = find(r"RUNWAY\s+(\d{2})", clean)
        
        # Vent
        w_m = re.search(r"(\d{3})\s+DEGREES\s+(\d+)", clean)
        wind = f"{w_m.group(1)} / {w_m.group(2)} KT" if w_m else "---"
        
        # Température
        t_m = re.search(r"TEMPERATURE\s+(?:MINUS\s+)?(\d+)\s+DEWPOINT", clean)
        temp = f"{t_m.group(1)}°C" if t_m else "---"
        
        zulu = datetime.datetime.utcnow().strftime("%H:%M")

        # 4. HTML Minimaliste (Ultra-lisible et robuste)
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; padding: 20px; }
        .box { border: 2px solid #fff; padding: 20px; max-width: 400px; margin: auto; }
        .header { display: flex; justify-content: space-between; font-weight: bold; border-bottom: 1px solid #444; padding-bottom: 10px; }
        .big { font-size: 5rem; text-align: center; margin: 20px 0; font-weight: 900; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center; }
        .item { background: #111; padding: 15px; border-radius: 5px; }
        .label { font-size: 0.7rem; color: #888; margin-bottom: 5px; }
        .val { font-size: 1.2rem; font-weight: bold; }
        .raw { font-size: 0.6rem; color: #333; margin-top: 20px; word-break: break-all; }
    </style>
</head>
<body>
    <div class="box">
        <div class="header"><span>EETN TALLINN</span> <span>{ZULU}Z</span></div>
        <div class="big">{INFO}</div>
        <div class="grid">
            <div class="item"><div class="label">RUNWAY</div><div class="val">{RWY}</div></div>
            <div class="item"><div class="label">WIND</div><div class="val">{WIND}</div></div>
            <div class="item"><div class="label">QNH</div><div class="val">{QNH}</div></div>
            <div class="item"><div class="label">TEMP</div><div class="val">{TEMP}</div></div>
        </div>
        <div class="raw">{RAW}</div>
    </div>
</body>
</html>
"""
        # Remplissage final sans backslashes
        final_html = html_template.format(
            ZULU=zulu, INFO=info, RWY=rwy, WIND=wind, QNH=qnh, TEMP=temp, RAW=txt
        )

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(final_html)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_atis_system()
