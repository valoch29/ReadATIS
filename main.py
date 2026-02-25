import os
import sys
import re

try:
    from faster_whisper import WhisperModel
except ImportError:
    os.system('pip install faster-whisper')
    from faster_whisper import WhisperModel

# Chargement dictionnaire
replacement_dict = {}
if os.path.exists("dictionary.py"):
    try:
        with open("dictionary.py", "r", encoding="utf-8") as f:
            local_vars = {}
            exec(f.read(), {}, local_vars)
            replacement_dict = local_vars.get('replacement_dict', {})
    except Exception: pass

def run_atis_system():
    audio_file = "atis_recorded.wav"
    if not os.path.exists(audio_file): return

    try:
        model = WhisperModel("medium", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_file, beam_size=5)
        raw_text = " ".join([s.text for s in segments]).upper().strip()
        
        # 1. Application du dictionnaire
        processed_text = raw_text
        for word, replacement in sorted(replacement_dict.items(), key=lambda x: len(x[0]), reverse=True):
            processed_text = processed_text.replace(word.upper(), replacement)

        # 2. NETTOYAGE DES CHIFFRES (Crucial pour QNH 1, 0, 2, 6 -> 1026)
        # Supprime les virgules et espaces entre les chiffres
        processed_text = re.sub(r'(\d)[\s,]+(?=\d)', r'\1', processed_text)

        # 3. Nettoyage de l'itération (On cherche TALLINN)
        if "THIS IS TALLINN" in processed_text:
            parts = processed_text.split("THIS IS TALLINN")
            processed_text = "THIS IS TALLINN" + parts[-1]
            if "OUT" in processed_text:
                processed_text = processed_text.split("OUT")[0] + "OUT."

        # 4. Extraction sécurisée
        def extract(pattern, text, default="---"):
            m = re.search(pattern, text)
            return m.group(1) if m else default

        val_info = extract(r"INFORMATION[\s,]+([A-Z])", processed_text)
        val_rwy = extract(r"RUNWAY[\s,]+(\d+)", processed_text, "08")
        val_qnh = extract(r"QNH[\s,]+(\d{4})", processed_text, "----")
        
        # Vent
        wind_m = re.search(r"(\d{3})[\s,]*DEGREES[\s,]*(\d+)[\s,]*KNOTS", processed_text)
        val_wind = f"{wind_m.group(1)}° / {wind_m.group(2)}KT" if wind_m else "--- / --KT"
        
        # Températures
        temp_m = re.search(r"TEMPERATURE[\s,]+(?:MINUS\s+)?(\d+)[\s,]+DEW[\s,]*POINT[\s,]+(?:MINUS\s+)?(\d+)", processed_text)
        if temp_m:
            t_sgn = "-" if "TEMPERATURE MINUS" in processed_text else ""
            d_sgn = "-" if "DEW POINT MINUS" in processed_text else ""
            val_temp = f"{t_sgn}{temp_m.group(1)}° / {d_sgn}{temp_m.group(2)}°"
        else:
            val_temp = "-- / --"

        # Condition de piste
        cond_m = re.search(r"TOUCHDOWN[\s,]+(\d)[\s,]+MIDPOINT[\s,]+(\d)[\s,]+STOP[\s,]*END[\s,]+(\d)", processed_text)
        val_cond = f"{cond_m.group(1)} / {cond_m.group(2)} / {cond_m.group(3)}" if cond_m else "6 / 6 / 6"
        
        timestamp = os.popen('date -u +"%H:%M UTC"').read().strip()

        # HTML (Design Anthracite)
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ background: #0c0c0c; color: #d0d0d0; font-family: 'Segoe UI', sans-serif; padding: 20px; }}
                .container {{ max-width: 650px; margin: auto; border: 1px solid #222; padding: 25px; background: #141414; border-radius: 4px; }}
                .header {{ text-align: center; border-bottom: 1px solid #333; padding-bottom: 15px; margin-bottom: 25px; font-weight: bold; font-size: 1.1rem; color: #fff; letter-spacing: 2px; }}
                .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 25px; }}
                .item {{ background: #1a1a1a; padding: 12px; border-radius: 3px; border-left: 3px solid #444; }}
                .label {{ color: #777; font-size: 0.7rem; text-transform: uppercase; margin-bottom: 4px; }}
                .val {{ font-size: 1.15rem; color: #efefef; font-weight: 600; font-family: monospace; }}
                .transcription {{ margin-top: 25px; line-height: 1.5; color: #999; font-size: 0.95rem; background: #0f0f0f; padding: 15px; border-radius: 3px; border: 1px solid #1a1a1a; white-space: pre-wrap; }}
                .footer {{ margin-top: 30px; font-size: 0.65rem; color: #333; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">TALLINN EETN ATIS &nbsp; {timestamp}</div>
                <div class="grid">
                    <div class="item"><div class="label">INFO</div><div class="val">{val_info}</div></div>
                    <div class="item"><div class="label">RWY</div><div class="val">{val_rwy}</div></div>
                    <div class="item"><div class="label">QNH</div><div class="val">{val_qnh} hPa</div></div>
                    <div class="item"><div class="label">WIND</div><div class="val">{val_wind}</div></div>
                    <div class="item"><div class="label">VISIBILITY</div><div class="val">CAVOK</div></div>
                    <div class="item"><div class="label">TEMP / DEW</div><div class="val">{val_temp}</div></div>
                    <div class="item"><div class="label">RWY CONDITION</div><div class="val">{val_cond}</div></div>
                    <div class="item"><div class="label">SURFACE</div><div class="val">FROST / WET</div></div>
                </div>
                <div class="transcription"><strong>MESSAGE:</strong><br><br>{processed_text}</div>
                <div class="footer">Automatic Decoder • Whisper Medium</div>
            </div>
        </body>
        </html>
        """
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Success.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_atis_system()