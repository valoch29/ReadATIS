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
    # Nettoyage des chiffres (1, 0, 2, 6 -> 1026)
    t = re.sub(r'(?<\d)[,.\s]+(?=\d)', '', t)
    t = " ".join(t.split())
    # Garder uniquement la dernière occurrence du message
    markers = ["THIS IS TALLINN", "INFORMATION"]
    best_start = 0
    for m in markers:
        pos = t.rfind(m)
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
        
        # Vent
        w_m = re.search(r"(\d{3})\s+DEGREES\s+(\d+)", txt)
        wind = f"{w_m.group(1)}° / {w_m.group(2)}KT" if w_m else "--- / --KT"
        
        # Température
        t_m = re.search(r"TEMPERATURE\s+(MINUS\s+)?(\d+)\s+DEWPOINT\s+(MINUS\s+)?(\d+)", txt)
        temp = f"{('-' if t_m.group(1) else '') + t_m.group(2)}° / {('-' if t_m.group(3) else '') + t_m.group(4)}°" if t_m else "-- / --"
        
        # RCC (Extraction robuste)
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
                :root {{ --bg: #000; --text: #fff; --border: #fff; }}
                body {{ background: var(--bg); color: var(--text); font-family: sans-serif; margin: 0; padding: 10px; display: flex; justify-content: center; }}
                .atis-box {{ width: 100%; max-width: 500px; border: 2px solid var(--border); padding: 20px; }}
                .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid var(--border); padding-bottom: 10px; margin-bottom: 20px; }}
                .header-title {{ font-size: 1.4rem; font-weight: bold; }}
                .grid {{ display: grid; grid-template-columns: 1fr 1fr; border-top: 1px solid var(--border); border-left: 1px solid var(--border); }}
                .item {{ border-right: 1px solid var(--border); border-bottom: 1px solid var(--border); padding: 15px; }}
                .full {{ grid-column: span 2; }}
                .label {{ font-size: 0.7rem; text-transform: uppercase; color: #888; margin-bottom: 5px; font-weight: bold; }}
                .value {{ font-size: 1.6rem; font-family: monospace; font-weight: bold; }}
                .info-box {{ font-size: 2.5rem; border: 3px solid var(--border); padding: 0 15px; display: inline-block; }}
                .raw {{ margin-top: 20px; font-size: 0.8rem; line-height: 1.4; color: #aaa; text-transform: uppercase; }}
                .footer {{ text-align: center; font-size: 0.6rem; margin-top: 20px; border-top: 1px solid #333; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="atis-box">
                <div class="header">
                    <div class="header-title">EETN TALLINN</div>
                    <div style="font-family:monospace; font-size:0.8rem;">{timestamp}</div>
                </div>
                <div class="grid">
                    <div class="item"><div class="label">Information</div><div class="info-box">{info}</div></div>
                    <div class="item"><div class="label">Runway</div><div class="value">{rwy}</div></div>
                    <div class="item"><div class="label">Wind</div><div class="value">{wind}</div></div>
                    <div class="item"><div class="label">QNH</div><div class="value">{qnh}</div></div>
                    <div class="item"><div class="label">Temp / Dew</div><div class="value">{temp}</div></div>
                    <div class="item"><div class="label">RCC</div><div class="value">{rcc}</div></div>
                    <div class="item full"><div class="label">Visibility / Clouds</div><div class="value">CAVOK</div></div>
                </div>
                <div class="raw"><strong>Message:</strong> {txt}</div>
                <div class="footer">STATED AT {timestamp} | WHISPER MEDIUM</div>
            </div>
        </body>
        </html>
        """
        with open("index.html", "w", encoding="utf-8") as f: f.write(html)
    except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    run_atis_system()
