import os
import re
import datetime
from faster_whisper import WhisperModel
from dictionary import CORRECTIONS  # On importe ton dictionnaire séparé

# --- CONFIGURATION ---
model = WhisperModel("medium.en", device="cpu", compute_type="int8")

def run_atis_system():
    if not os.path.exists("atis_recorded.wav"):
        print("Audio non trouvé.")
        return

    # 1. TRANSCRIPTION
    prompt = "Tallinn Airport ATIS, Information, Runway 08, QNH 1021, CAVOK, frost, wet."
    segments, _ = model.transcribe("atis_recorded.wav", beam_size=5, initial_prompt=prompt)
    raw_text = " ".join([s.text for s in segments]).upper()

    # 2. NETTOYAGE VIA DICTIONNAIRE
    clean_text = raw_text
    for wrong, right in CORRECTIONS.items():
        clean_text = re.sub(rf'\b{wrong}\b', right, clean_text)
    
    # Nettoyage technique (virgules, doubles espaces)
    clean_text = clean_text.replace(",", " ").replace(".", " ")
    clean_text = " ".join(clean_text.split())

    # 3. EXTRACTION DES DONNÉES
    data = {
        "info": "-", "rwy": "--", "qnh": "----", "wind": "--- / --KT",
        "vis": "---", "td": "-- / --", "rcc": "-/-/-", "surf": "UNKNOWN"
    }

    # Regex robustes (gèrent les virgules et le texte superflu)
    m_i = re.search(r"INFORMATION\s+([A-Z])", clean_text)
    if m_i: data["info"] = m_i.group(1)

    m_q = re.search(r"QNH\s*(\d{4})", clean_text)
    if m_q: data["qnh"] = m_q.group(1)

    m_r = re.search(r"RUNWAY\s*(\d{2})", clean_text)
    if m_r: data["rwy"] = m_r.group(1)

    m_w = re.search(r"(\d{3})\s*DEGREES\s*(\d+)\s*KNOTS", clean_text)
    if m_w: data["wind"] = f"{m_w.group(1)}° / {m_w.group(2).zfill(2)}KT"

    if "CAVOK" in clean_text: data["vis"] = "CAVOK"
    else:
        m_v = re.search(r"VISIBILITY.*?(\d+)\s*(?:KM|M)?", clean_text)
        if m_v: data["vis"] = m_v.group(1) + " KM"

    def get_temp(anchor):
        parts = clean_text.split(anchor)
        if len(parts) > 1:
            m = re.search(r"(MINUS\s+)?(\d+)", parts[1])
            if m: return ("-" if m.group(1) else "") + m.group(2)
        return "--"
    data["td"] = f"{get_temp('TEMPERATURE')}° / {get_temp('DEWPOINT')}°"

    r1 = re.search(r"TOUCHDOWN\s*(\d)", clean_text)
    r2 = re.search(r"MIDPOINT\s*(\d)", clean_text)
    r3 = re.search(r"STOP END\s*(\d)", clean_text)
    if r1: data["rcc"] = f"{r1.group(1)}/{r2.group(1) if r2 else r1.group(1)}/{r3.group(1) if r3 else r1.group(1)}"

    states = [s for s in ["WET", "DRY", "WATER", "ICE", "SNOW", "SLUSH", "FROST"] if s in clean_text]
    if states: data["surf"] = "/".join((states * 3)[:3])

    # 4. GÉNÉRATION HTML
    now = datetime.datetime.now().strftime("%H:%M")
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EETN ATIS</title>
        <style>
            :root {{ --bg: #121212; --card: #1a1a1a; --white: #ffffff; --dim: #777; }}
            body {{ font-family: sans-serif; background: var(--bg); color: var(--white); margin: 0; padding: 15px; display: flex; flex-direction: column; align-items: center; text-transform: uppercase; }}
            .container {{ width: 100%; max-width: 480px; }}
            .header {{ display: flex; justify-content: space-between; font-size: 0.7rem; color: var(--dim); margin: 15px 0; font-weight: bold; letter-spacing: 1px; }}
            .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 15px; }}
            .card {{ background: var(--card); padding: 18px 5px; border-radius: 10px; text-align: center; border: 1px solid #222; }}
            .label {{ font-size: 0.6rem; color: var(--dim); margin-bottom: 5px; display: block; }}
            .value {{ font-size: 1.6rem; font-weight: 800; }}
            .sec {{ background: var(--card); border-radius: 10px; padding: 5px 20px; margin-bottom: 10px; border: 1px solid #222; }}
            .row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #252525; }}
            .row:last-child {{ border: none; }}
            .row span:first-child {{ color: var(--dim); font-size: 0.75rem; font-weight: bold; }}
            .raw {{ font-size: 0.65rem; color: #333; margin-top: 25px; text-transform: none; text-align: justify; font-style: italic; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header"><span>TALLINN EETN ATIS</span><span>{now} UTC</span></div>
            <div class="grid">
                <div class="card"><span class="label">INFO</span><span class="value">{data['info']}</span></div>
                <div class="card"><span class="label">RWY</span><span class="value">{data['rwy']}</span></div>
                <div class="card"><span class="label">QNH</span><span class="value">{data['qnh']}</span></div>
            </div>
            <div class="sec">
                <div class="row"><span>WIND</span><span>{data['wind']}</span></div>
                <div class="row"><span>VISIBILITY</span><span>{data['vis']}</span></div>
                <div class="row"><span>TEMP / DEW</span><span>{data['td']}</span></div>
            </div>
            <div class="sec">
                <div class="row"><span>RWY CONDITION</span><span>{data['rcc']}</span></div>
                <div class="row"><span>SURFACE</span><span>{data['surf']}</span></div>
            </div>
            <div class="raw">ANALYZED: {clean_text}</div>
        </div>
    </body>
    </html>
    '''
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    run_atis_system()
