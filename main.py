import os
import re

try:
    from faster_whisper import WhisperModel
except ImportError:
    os.system('pip install faster-whisper')
    from faster_whisper import WhisperModel

def get_dict():
    if not os.path.exists("dictionary.py"): return {}
    try:
        l = {}
        with open("dictionary.py", "r", encoding="utf-8") as f:
            exec(f.read(), {}, l)
        return l.get('replacement_dict', {})
    except: return {}

def clean_and_deduplicate(text, d):
    t = text.upper()
    for k, v in sorted(d.items(), key=lambda x: len(x[0]), reverse=True):
        t = t.replace(k, v)
    
    # Nettoyage agressif des nombres (1, 0, 2, 6 -> 1026)
    t = re.sub(r'(?<\d)[,.\s]+(?=\d)', '', t)
    t = " ".join(t.split())

    # Isolation d'une seule occurrence (on prend la dernière partie du stream)
    markers = ["THIS IS TALLINN", "TALLINN AIRPORT", "INFORMATION"]
    best_start = 0
    for marker in markers:
        pos = t.rfind(marker)
        if pos > best_start: best_start = pos
    
    return t[best_start:].strip()

def run_atis_system():
    if not os.path.exists("atis_recorded.wav"): return
    
    d = get_dict()
    try:
        model = WhisperModel("medium", device="cpu", compute_type="int8")
        segments, _ = model.transcribe("atis_recorded.wav", beam_size=5)
        raw_msg = " ".join([s.text for s in segments])
        
        txt = clean_and_deduplicate(raw_msg, d)
        
        def find(pattern, src, default="---"):
            res = re.findall(pattern, src)
            return res[-1] if res else default

        # Extraction des données
        info = find(r"INFORMATION\s+([A-Z])", txt)
        qnh = find(r"(?:QNH|HPA)\s+(\d{4})", txt)
        rwy = find(r"RUNWAY\s+(\d{2})", txt, "08")
        
        # Vent
        w_m = re.search(r"(\d{3})\s+DEGREES\s+(\d+)", txt)
        wind = f"{w_m.group(1)}° / {w_m.group(2)}KT" if w_m else "--- / --KT"
        
        # Température
        t_m = re.search(r"TEMPERATURE\s+(MINUS\s+)?(\d+)\s+DEWPOINT\s+(MINUS\s+)?(\d+)", txt)
        if t_m:
            t_v = f"-{t_m.group(2)}" if t_m.group(1) else t_m.group(2)
            d_v = f"-{t_m.group(4)}" if t_m.group(3) else t_m.group(4)
            temp = f"{t_v}° / {d_v}°"
        else: temp = "-- / --"

        # RCC (Touchdown / Midpoint / Stop End)
        td = find(r"TOUCHDOWN\s+(\d)", txt, "6")
        mp = find(r"MIDPOINT\s+(\d)", txt, "6")
        se = find(r"STOP END\s+(\d)", txt, "6")
        rcc = f"{td} / {mp} / {se}"

        # --- GÉNÉRATION HTML RESPONSIVE ---
        timestamp = os.popen('date -u +"%H:%M UTC"').read().strip()
        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EETN ATIS Dashboard</title>
            <style>
                :root {{ --bg: #0a0a0b; --card: #121214; --text: #e2e2e2; --accent: #00ff9d; --dim: #666; }}
                body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 1rem; display: flex; justify-content: center; }}
                .container {{ width: 100%; max-width: 600px; }}
                .card {{ background: var(--card); border: 1px solid #222; border-radius: 12px; padding: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
                .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #222; padding-bottom: 1rem; margin-bottom: 1.5rem; }}
                .title {{ font-weight: 800; letter-spacing: 1px; font-size: 1.1rem; color: #fff; }}
                .time {{ font-size: 0.8rem; color: var(--dim); font-family: monospace; }}
                .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }}
                @media (max-width: 400px) {{ .grid {{ grid-template-columns: 1fr; }} }}
                .item {{ background: #1a1a1c; padding: 1rem; border-radius: 8px; border-bottom: 2px solid #222; }}
                .label {{ font-size: 0.7rem; color: var(--dim); text-transform: uppercase; margin-bottom: 0.3rem; font-weight: 600; }}
                .value {{ font-size: 1.3rem; color: var(--accent); font-family: 'SF Mono', monospace; font-weight: bold; }}
                .transcript-box {{ margin-top: 1.5rem; background: #000; border-radius: 8px; padding: 1rem; border: 1px solid #1a1a1a; }}
                .transcript-label {{ font-size: 0.7rem; color: var(--dim); margin-bottom: 0.8rem; font-weight: 600; text-transform: uppercase; }}
                .transcript-text {{ font-size: 0.85rem; color: #999; line-height: 1.5; white-space: pre-wrap; }}
                .footer {{ text-align: center; font-size: 0.6rem; color: #333; margin-top: 1.5rem; text-transform: uppercase; letter-spacing: 1px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="card">
                    <div class="header">
                        <div class="title">EETN TALLINN ATIS</div>
                        <div class="time">{timestamp}</div>
                    </div>
                    <div class="grid">
                        <div class="item"><div class="label">Information</div><div class="value" style="color:#ffcc00">{info}</div></div>
                        <div class="item"><div class="label">Runway</div><div class="value">{rwy}</div></div>
                        <div class="item"><div class="label">Wind</div><div class="value">{wind}</div></div>
                        <div class="item"><div class="label">QNH</div><div class="value">{qnh} hPa</div></div>
                        <div class="item"><div class="label">Temperature</div><div class="value">{temp}</div></div>
                        <div class="item"><div class="label">RCC (Condition)</div><div class="value">{rcc}</div></div>
                    </div>
                    <div class="transcript-box">
                        <div class="transcript-label">Decoded Message</div>
                        <div class="transcript-text">{txt}</div>
                    </div>
                    <div class="footer">AI-Powered Decoder • Whisper Medium INT8</div>
                </div>
            </div>
        </body>
        </html>
        """
        with open("index.html", "w", encoding="utf-8") as f: f.write(html)

    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    run_atis_system()
