import os
import re
import sys

# Installation automatique de faster-whisper si absent
try:
    from faster_whisper import WhisperModel
except ImportError:
    os.system('pip install faster-whisper')
    from faster_whisper import WhisperModel

def get_dict():
    """Charge le dictionnaire de corrections phonétiques."""
    if not os.path.exists("dictionary.py"):
        print("Warning: dictionary.py not found.")
        return {}
    try:
        l = {}
        with open("dictionary.py", "r", encoding="utf-8") as f:
            exec(f.read(), {}, l)
        return l.get('replacement_dict', {})
    except Exception as e:
        print(f"Error loading dictionary: {e}")
        return {}

def clean_and_deduplicate(text, d):
    """Nettoie le texte, applique le dictionnaire et isole une seule occurrence."""
    t = text.upper()
    # 1. Remplacement via dictionnaire (trié par longueur pour éviter les conflits)
    for k, v in sorted(d.items(), key=lambda x: len(x[0]), reverse=True):
        t = t.replace(k, v)
    
    # 2. Nettoyage radical des nombres (ex: 1, 0, 2, 6 -> 1026)
    t = re.sub(r'(?<=d)[,.\s]+(?=d)', '', t)
    
    # 3. Suppression des doubles espaces
    t = " ".join(t.split())

    # 4. DÉDUPLICATION : On isole le dernier message complet
    markers = ["THIS IS TALLINN", "TALLINN AIRPORT", "INFORMATION"]
    best_start = 0
    for marker in markers:
        pos = t.rfind(marker)
        if pos > best_start:
            best_start = pos
    
    return t[best_start:].strip()

def run_atis_system():
    audio_file = "atis_recorded.wav"
    
    # --- DIAGNOSTIC LOGS POUR GITHUB ACTIONS ---
    print(f"Checking for audio file: {audio_file}")
    if not os.path.exists(audio_file):
        print(f"ERROR: {audio_file} not found in {os.getcwd()}")
        print(f"Current directory content: {os.listdir('.')}")
        return

    file_size = os.path.getsize(audio_file)
    print(f"Audio file found! Size: {file_size} bytes")
    
    if file_size < 1000:
        print("ERROR: Audio file is too small (likely empty).")
        return
    # -------------------------------------------

    d = get_dict()
    
    try:
        print("Starting Whisper transcription (Medium Model)...")
        # Utilisation du CPU avec int8 pour la rapidité sur GitHub Actions
        model = WhisperModel("medium", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_file, beam_size=5)
        raw_msg = " ".join([s.text for s in segments])
        
        if not raw_msg.strip():
            print("Whisper returned empty text.")
            return

        # Traitement du texte
        txt = clean_and_deduplicate(raw_msg, d)
        
        # --- MOTEUR D'EXTRACTION ---
        def find(pattern, src, default="---"):
            res = re.findall(pattern, src)
            return res[-1] if res else default

        info = find(r"INFORMATION\s+([A-Z])", txt)
        qnh = find(r"(?:QNH|HPA)\s+(\d{4})", txt)
        rwy = find(r"RUNWAY\s+(\d{2})", txt, "08")
        
        # Vent
        w_m = re.search(r"(\d{3})\s+DEGREES\s+(\d+)", txt)
        wind = f"{w_m.group(1)}° / {w_m.group(2)}KT" if w_m else "--- / --KT"
        
        # Température / Dewpoint
        t_m = re.search(r"TEMPERATURE\s+(MINUS\s+)?(\d+)\s+DEWPOINT\s+(MINUS\s+)?(\d+)", txt)
        if t_m:
            t_v = f"{'-' if t_m.group(1) else ''}{t_m.group(2)}"
            d_v = f"{'-' if t_m.group(3) else ''}{t_m.group(4)}"
            temp = f"{t_v}° / {d_v}°"
        else:
            temp = "-- / --"

        # RCC (Condition de piste)
        td = find(r"TOUCHDOWN\s+(\d)", txt, "6")
        mp = find(r"MIDPOINT\s+(\d)", txt, "6")
        se = find(r"STOP END\s+(\d)", txt, "6")
        rcc = f"{td} / {mp} / {se}"

        # --- GÉNÉRATION HTML NOIR & BLANC (RESPONSIVE) ---
        import datetime
        timestamp = datetime.datetime.utcnow().strftime("%d %b %H:%M UTC").upper()

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EETN ATIS - PILOT VIEW</title>
            <style>
                :root {{ --bg: #000000; --text: #ffffff; --border: #ffffff; --dim: #888888; }}
                * {{ box-sizing: border-box; }}
                body {{ background: var(--bg); color: var(--text); font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, monospace; margin: 0; padding: 15px; display: flex; justify-content: center; }}
                .container {{ width: 100%; max-width: 550px; border: 2px solid var(--border); padding: 20px; }}
                .header {{ display: flex; justify-content: space-between; align-items: baseline; border-bottom: 2px solid var(--border); padding-bottom: 15px; margin-bottom: 25px; }}
                .icao {{ font-size: 1.8rem; font-weight: 900; }}
                .time {{ font-size: 0.9rem; font-weight: bold; color: var(--dim); }}
                .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 2px; background: var(--border); border: 2px solid var(--border); }}
                .item {{ background: var(--bg); padding: 20px; display: flex; flex-direction: column; }}
                .full-width {{ grid-column: span 2; }}
                .label {{ font-size: 0.7rem; font-weight: bold; color: var(--dim); text-transform: uppercase; margin-bottom: 8px; letter-spacing: 1px; }}
                .value {{ font-size: 2rem; font-weight: 800; line-height: 1; }}
                .info-box {{ font-size: 3.5rem; border: 4px solid var(--border); padding: 5px 15px; display: inline-block; line-height: 1; }}
                .raw-msg {{ margin-top: 25px; font-size: 0.8rem; line-height: 1.5; color: var(--dim); border-top: 1px solid #333; padding-top: 15px; text-transform: uppercase; }}
                @media (max-width: 480px) {{
                    .value {{ font-size: 1.4rem; }}
                    .info-box {{ font-size: 2.5rem; }}
                    .item {{ padding: 12px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="icao">EETN TALLINN</div>
                    <div class="time">{timestamp}</div>
                </div>
                <div class="grid">
                    <div class="item"><div class="label">Information</div><div><span class="info-box">{info}</span></div></div>
                    <div class="item"><div class="label">Active Rwy</div><div class="value">{rwy}</div></div>
                    <div class="item"><div class="label">Wind</div><div class="value">{wind}</div></div>
                    <div class="item"><div class="label">QNH</div><div class="value">{qnh}</div></div>
                    <div class="item"><div class="label">Temperature</div><div class="value">{temp}</div></div>
                    <div class="item"><div class="label">RCC (Codes)</div><div class="value">{rcc}</div></div>
                    <div class="item full-width"><div class="label">Visibility / Clouds</div><div class="value">CAVOK</div></div>
                </div>
                <div class="raw-msg">
                    <strong>Decoded:</strong> {txt}
                </div>
            </div>
        </body>
        </html>
        """
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Successfully updated index.html")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    run_atis_system()
