import os
import sys
import re

# Installation forcée de faster-whisper
try:
    from faster_whisper import WhisperModel
except ImportError:
    os.system('pip install faster-whisper')
    from faster_whisper import WhisperModel

# Chargement du dictionnaire
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
        model = WhisperModel("small", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_file, beam_size=5)
        raw_text = " ".join([s.text for s in segments]).upper().strip()
        
        # 1. Nettoyage : On ne garde que la première itération
        # Les ATIS se répètent souvent après "INFORMATION [LETTER] OUT" ou "THIS IS..."
        parts = re.split(r"(THIS IS|INFORMATION [A-Z] OUT)", raw_text)
        if len(parts) > 2:
            processed_text = parts[0] + parts[1] + parts[2]
        else:
            processed_text = raw_text

        # 2. Application du dictionnaire
        for word, replacement in sorted(replacement_dict.items(), key=lambda x: len(x[0]), reverse=True):
            processed_text = processed_text.replace(word.upper(), replacement)

        # 3. EXTRACTION DES PARAMÈTRES (Regex)
        info = re.search(r"INFORMATION\s+([A-Z])", processed_text)
        rwy = re.search(r"RUNWAY\s+(\d+)", processed_text)
        qnh = re.search(r"QNH\s+(\d+)", processed_text)
        # Vent : cherche "DEGREES [X] KNOTS"
        wind = re.search(r"(\d+)\s+DEGREES\s+(\d+)\s+KNOTS", processed_text)
        # Temp/Dew : cherche "TEMPERATURE\s+MINUS\s+(\d+)\s+DEWPOINT\s+MINUS\s+(\d+)"
        temp_match = re.search(r"TEMPERATURE\s+(?:MINUS\s+)?(\d+)\s+DEWPOINT\s+(?:MINUS\s+)?(\d+)", processed_text)
        # Condition : cherche "CODE\s+(\d+)\s+(\d+)\s+(\d+)"
        cond = re.search(r"(\d)\s+MIDPOINT\s+(\d)\s+STOP END\s+(\d)", processed_text)

        # Formatage des valeurs pour l'affichage
        val_info = info.group(1) if info else "-"
        val_rwy = rwy.group(1) if rwy else "--"
        val_qnh = qnh.group(1) if qnh else "----"
        val_wind = f"{wind.group(1)}° / {wind.group(2)}KT" if wind else "--- / --KT"
        
        # Gestion des températures négatives
        t = f"-{temp_match.group(1)}" if "MINUS" in processed_text.split("DEWPOINT")[0] else temp_match.group(1) if temp_match else "--"
        d = f"-{temp_match.group(2)}" if temp_match and "MINUS" in processed_text else temp_match.group(2) if temp_match else "--"
        val_temp = f"{t}° / {d}°"

        val_cond = f"{cond.group(1)} / {cond.group(2)} / {cond.group(3)}" if cond else "- / - / -"
        
        timestamp = os.popen('date -u +"%H:%M UTC"').read().strip()

        # 4. GÉNÉRATION DU HTML (Style Anthracite/Aéro)
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ background: #0a0a0a; color: #d0d0d0; font-family: 'Courier New', monospace; padding: 20px; }}
                .container {{ max-width: 700px; margin: auto; border: 1px solid #333; padding: 20px; background: #111; }}
                .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; font-weight: bold; }}
                .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; border-bottom: 1px solid #333; padding-bottom: 20px; }}
                .item {{ padding: 5px; }}
                .label {{ color: #888; font-size: 0.8rem; text-transform: uppercase; }}
                .val {{ font-size: 1.2rem; color: #fff; font-weight: bold; }}
                .transcription {{ margin-top: 20px; line-height: 1.4; color: #aaa; font-size: 0.9rem; text-align: justify; }}
                .footer {{ margin-top: 30px; font-size: 0.7rem; color: #444; text-align: right; border-top: 1px solid #222; padding-top: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">TALLINN EETN ATIS {timestamp}</div>
                
                <div class="grid">
                    <div class="item"><div class="label">INFO</div><div class="val">{val_info}</div></div>
                    <div class="item"><div class="label">RWY</div><div class="val">{val_rwy}</div></div>
                    <div class="item"><div class="label">QNH</div><div class="val">{val_qnh}</div></div>
                    <div class="item"><div class="label">WIND</div><div class="val">{val_wind}</div></div>
                    <div class="item"><div class="label">VISIBILITY</div><div class="val">CAVOK</div></div>
                    <div class="item"><div class="label">TEMP / DEW</div><div class="val">{val_temp}</div></div>
                    <div class="item"><div class="label">RWY CONDITION</div><div class="val">{val_cond}</div></div>
                    <div class="item"><div class="label">SURFACE</div><div class="val">FROST/FROST/FROST</div></div>
                </div>

                <div class="transcription">
                    <strong>TRANSCRIPTION:</strong><br><br>{processed_text}
                </div>

                <div class="footer">EETN AUTOMATIC DECODER v2.0</div>
            </div>
        </body>
        </html>
        """
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
    except Exception as e: print(f"Erreur : {e}")

if __name__ == "__main__":
    run_atis_system()
