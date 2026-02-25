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
    t = re.sub(r'(?<\d)[,.\s]+(?=\d)', '', t)
    t = " ".join(t.split())
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

        info = find(r"INFORMATION\s+([A-Z])", txt)
        qnh = find(r"(?:QNH|HPA)\s+(\d{4})", txt)
        rwy = find(r"RUNWAY\s+(\d{2})", txt, "08")
        w_m = re.search(r"(\d{3})\s+DEGREES\s+(\d+)", txt)
        wind = f"{w_m.group(1)}° / {w_m.group(2)}KT" if w_m else "--- / --KT"
        t_m = re.search(r"TEMPERATURE\s+(MINUS\s+)?(\d+)\s+DEWPOINT\s+(MINUS\s+)?(\d+)", txt)
        temp = f"{('-' if t_m.group(1) else '') + t_m.group(2)}° / {('-' if t_m.group(3) else '') + t_m.group(4)}°" if t_m else "-- / --"
        
        td = find(r"TOUCHDOWN\s+(\d)", txt, "6")
        mp = find(r"MIDPOINT\s+(\d)", txt, "6")
        se = find(r"STOP END\s+(\d)", txt, "6")
        rcc = f"{td} / {mp} / {se}"

        timestamp = os.popen('date -u +"%d %b %H:%M UTC"').read().strip().upper()

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                :root {{ --bg: #000000; --border: #ffffff; --text: #ffffff; --dim: #888888; }}
                * {{ box-sizing: border-box; }}
                body {{ background: var(--bg); color: var(--text); font-family: "Inter", "Segoe UI", sans-serif; margin: 0; padding: 10px; display: flex; justify-content: center; }}
                .atis-container {{ width: 100%; max-width: 500px; border: 2px solid var(--border); padding: 15px; }}
                
                .header {{ display: flex; justify-content: space-between; align-items: baseline; border-bottom: 2px solid var(--border); padding-bottom: 10px; margin-bottom: 20px; }}
                .icao {{ font-size: 1.5rem; font-weight: 900; letter-spacing: -1px; }}
                .date {{ font-size: 0.85rem; font-weight: 600; font-family: monospace; }}

                .main-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2px; background: var(--border); border: 2px solid var(--border); }}
                .item {{ background: var(--bg); padding: 15px; display: flex; flex-direction: column; }}
                .full-width {{ grid-column: span 2; }}
                
                .label {{ font-size: 0.75rem; font-weight: 700; color: var(--dim); text-transform: uppercase; margin-bottom: 5px; }}
                .value {{ font-size: 1.8rem; font-weight: 800; font-family: monospace; line-height: 1; }}
                .info-value {{ font-size: 3rem; color: #fff; border: 2px solid #fff; display: inline-block; padding: 0 10px; text-align: center; }}

                .raw-msg {{ margin-top: 20px; font-size: 0.85rem; line-height: 1.4; border-top: 1px solid var(--dim); padding-top: 10px; color: var(--dim); text-transform: uppercase; }}
                
                @media (max-width: 450px) {{
                    .value {{ font-size: 1.4rem; }}
                    .info-value {{ font-size: 2.2rem; }}
                }}
            </style>
        </head>
        <body>
            <div class="atis-container">
                <div class="header">
                    <div class="icao">EETN TALLINN</div>
                    <div class="date">{timestamp}</div>
                </div>
                
                <div class="main-grid">
                    <div class="item"><div class="label">Information</div><div class="info-value">{info}</div></div>
                    <div class="item"><div class="label">Runway</div><div class="value">{rwy}</div></div>
                    <div class="item"><div class="label">Wind</div><div class="value">{wind}</div></div>
                    <div class="item"><div class="label">QNH</div><div class="value">{qnh}</div></div>
                    <div class="item"><div class="label">Temp / Dew</div><div class="value">{temp}</div></div>
                    <div class="item"><div class="label">RCC (Codes)</div><div class="value">{rcc}</div></div>
                    <div class="item full-width"><div class="label">Clouds / Vis</div><div class="value">CAVOK</div></div>
                </div>

                <div class="raw-msg">
                    <strong>Decoded:</strong> {txt}
                </div>
            </div>
        </body>
        </html>
        """
        with open("index.html", "w", encoding="utf-8") as f: f.write(html)

    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    run_atis_system()
