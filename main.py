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
        model = WhisperModel("medium", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_file, beam_size=5)
        txt = " ".join([s.text for s in segments]).upper()
        
        # Nettoyage pour l'extraction
        clean = txt.replace(",", " ").replace(".", " ").replace(":", " ")
        clean = " ".join(clean.split())

        def find(pattern, src, default="---"):
            res = re.findall(pattern, src)
            return res[-1] if res else default

        # Extraction Data
        info = find(r"INFORMATION\s+([A-Z])", clean)
        qnh = find(r"(?:QNH|HPA)\s+(\d{4})", clean)
        rwy = find(r"RUNWAY\s+(\d{2})", clean)
        
        # Vent
        w_m = re.search(r"(\d{3})\s+(?:DEGREES|DEG)\s+(\d+)", clean)
        wind = f"{w_m.group(1)}° / {w_m.group(2)}<span style='font-size:0.8rem'>KT</span>" if w_m else "---"
        
        # Température
        t_m = re.search(r"TEMPERATURE\s+(MINUS\s+)?(\d+)\s+DEWPOINT\s+(MINUS\s+)?(\d+)", clean)
        temp = f"{('-' if t_m.group(1) else '') + t_m.group(2)}° / {('-' if t_m.group(3) else '') + t_m.group(4)}°" if t_m else "-- / --"
        
        # RCC & Conditions
        rcc = f"{find(r'TOUCHDOWN\s+(\d)', clean)} {find(r'MIDPOINT\s+(\d)', clean)} {find(r'STOP END\s+(\d)', clean)}"
        cond = "DRY"
        if "SNOW" in clean: cond = "SNOW"
        if "WET" in clean: cond = "WET"
        if "ICE" in clean: cond = "ICE"

        zulu = datetime.datetime.utcnow().strftime("%H:%M")

        # HTML DESIGN RÉVERSIBLE & RESPONSIVE
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                :root {{ --bg: #0a0a0c; --card: #16161a; --accent: #ffffff; --dim: #828282; }}
                body {{ background: var(--bg); color: var(--accent); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 10px; display: flex; justify-content: center; }}
                .container {{ width: 100%; max-width: 480px; margin-top: 20px; }}
                
                /* Header Area */
                .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding: 0 5px; }}
                .airport {{ font-size: 1.2rem; font-weight: 800; letter-spacing: 1px; }}
                .zulu {{ background: #fff; color: #000; padding: 2px 8px; font-weight: 900; border-radius: 4px; font-size: 0.9rem; }}

                /* Information Letter Box */
                .info-hero {{ background: var(--card); border: 1px solid #333; border-radius: 12px; padding: 20px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }}
                .info-label {{ color: var(--dim); font-size: 0.8rem; text-transform: uppercase; font-weight: bold; }}
                .info-letter {{ font-size: 4rem; font-weight: 900; line-height: 1; }}

                /* Data Grid */
                .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
                .tile {{ background: var(--card); border: 1px solid #2a2a2a; border-radius: 12px; padding: 15px; }}
                .tile-label {{ color: var(--dim); font-size: 0.7rem; text-transform: uppercase; margin-bottom: 8px; font-weight: 600; }}
                .tile-val {{ font-size: 1.5rem; font-weight: 700; font-variant-numeric: tabular-nums; }}
                
                /* Status Badge */
                .status {{ font-size: 0.8rem; background: #222; padding: 4px 10px; border-radius: 20px; color: #fff; margin-top: 5px; display: inline-block; border: 1px solid #444; }}

                /* Footer Message */
                .raw-box {{ margin-top: 25px; background: #111; border-radius: 8px; padding: 15px; font-size: 0.75rem; color: #666; line-height: 1.4; border-left: 3px solid #333; }}
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
                        <div class="info-label">Current Information</div>
                        <div class="status">ILS APCH / RWY {rwy}</div>
                    </div>
                    <div class="info-letter">{info}</div>
                </div>

                <div class="grid">
                    <div class="tile"><div class="tile-label">Wind</div><div class="tile-val">{wind}</div></div>
                    <div class="tile"><div class="tile-label">QNH</div><div class="tile-val">{qnh}</div></div>
                    <div class="tile"><div class="tile-label">Temp / DW</div><div class="tile-val">{temp}</div></div>
                    <div class="tile">
                        <div class="tile-label">RCC / Surface</div>
                        <div class="tile-val" style="font-size:1.2rem">{rcc}</div>
                        <div style
