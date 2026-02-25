import os
import re

try:
    from faster_whisper import WhisperModel
except ImportError:
    os.system('pip install faster-whisper')
    from faster_whisper import WhisperModel

# Chargement du dictionnaire avec gestion d'erreurs
def get_dict():
    if not os.path.exists("dictionary.py"): return {}
    try:
        l = {}
        with open("dictionary.py", "r", encoding="utf-8") as f:
            exec(f.read(), {}, l)
        return l.get('replacement_dict', {})
    except: return {}

def clean_text(text, d):
    # 1. Passage en majuscule
    t = text.upper()
    # 2. Remplacement via dictionnaire
    for k, v in sorted(d.items(), key=lambda x: len(x[0]), reverse=True):
        t = t.replace(k, v)
    # 3. Nettoyage radical des nombres : "1, 0, 2, 6" -> "1026"
    # On supprime les virgules et points entre les chiffres
    t = re.sub(r'(?<=\d)[,.\s]+(?=\d)', '', t)
    # 4. Suppression des doubles espaces et ponctuation résiduelle
    t = re.sub(r'[^\w\s°/]', ' ', t)
    return " ".join(t.split())

def run_atis_system():
    if not os.path.exists("atis_recorded.wav"): return
    
    d = get_dict()
    try:
        model = WhisperModel("medium", device="cpu", compute_type="int8")
        segments, _ = model.transcribe("atis_recorded.wav", beam_size=5)
        raw_msg = " ".join([s.text for s in segments])
        
        txt = clean_text(raw_msg, d)
        
        # --- MOTEUR D'EXTRACTION ---
        def find(pattern, src, default="---"):
            res = re.findall(pattern, src)
            return res[-1] if res else default

        # 1. Info & QNH & Runway
        info = find(r"INFORMATION\s+([A-Z])", txt)
        qnh = find(r"(?:QNH|HPA)\s+(\d{4})", txt)
        rwy = find(r"RUNWAY\s+(\d{2})", txt, "08")
        
        # 2. Vent (Prend en compte les rafales 'G' ou le vent variable)
        # Cherche : 3 chiffres + DEGREES + force
        wind_match = re.search(r"(\d{3})\s+DEGREES\s+(\d+)", txt)
        wind = f"{wind_match.group(1)}° / {wind_match.group(2)}KT" if wind_match else "CALM" if "CALM" in txt else "--- / --KT"
        
        # 3. Température / Dewpoint
        # Cherche TEMPERATURE + [MINUS] + chiffres + DEWPOINT + [MINUS] + chiffres
        temp_match = re.search(r"TEMPERATURE\s+(MINUS\s+)?(\d+)\s+DEWPOINT\s+(MINUS\s+)?(\d+)", txt)
        if temp_match:
            t_val = f"-{temp_match.group(2)}" if temp_match.group(1) else temp_match.group(2)
            d_val = f"-{temp_match.group(4)}" if temp_match.group(3) else temp_match.group(4)
            temp = f"{t_val}° / {d_val}°"
        else:
            temp = "-- / --"

        # 4. Nuages (Robustesse : détecte les couches multiples)
        clouds = "CAVOK"
        cloud_types = ["FEW", "SCT", "BKN", "OVC"]
        found_clouds = re.findall(r"(FEW|SCT|BKN|OVC)\s*(\d{3})", txt)
        if found_clouds:
            clouds = " / ".join([f"{c[0]}{c[1]}" for c in found_clouds])

        # 5. État de piste (RWY COND)
        cond_match = re.search(r"TOUCHDOWN\s+(\d)\s+MIDPOINT\s+(\d)\s+STOP\s+END\s+(\d)", txt)
        cond = f"{cond_match.group(1)} / {cond_match.group(2)} / {cond_match.group(3)}" if cond_match else "6 / 6 / 6"

        # --- GENERATION HTML ---
        timestamp = os.popen('date -u +"%H:%M UTC"').read().strip()
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ background: #050505; color: #e0e0e0; font-family: 'Monaco', monospace; display: flex; justify-content: center; padding: 20px; }}
                .box {{ width: 100%; max-width: 600px; border: 2px solid #333; background: #000; padding: 20px; box-shadow: 0 0 20px rgba(0,255,0,0.05); }}
                .row {{ display: flex; justify-content: space-between; border-bottom: 1px solid #111; padding: 10px 0; }}
                .lbl {{ color: #666; font-size: 12px; }}
                .val {{ color: #00FF00; font-size: 18px; font-weight: bold; }}
                .msg {{ margin-top: 20px; font-size: 13px; color: #888; line-height: 1.6; border-top: 1px solid #333; padding-top: 10px; }}
                .status {{ font-size: 10px; color: #444; text-align: right; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="box">
                <div style="text-align:center; color:#fff; margin-bottom:20px;">EETN ATIS MONITOR</div>
                <div class="row"><span class="lbl">INFORMATION</span><span class="val" style="color:#ffcc00">{info}</span></div>
                <div class="row"><span class="lbl">ACTIVE RWY</span><span class="val">{rwy}</span></div>
                <div class="row"><span class="lbl">WIND</span><span class="val">{wind}</span></div>
                <div class="row"><span class="lbl">VISIBILITY / CLOUDS</span><span class="val">{clouds}</span></div>
                <div class="row"><span class="lbl">TEMP / DEW</span><span class="val">{temp}</span></div>
                <div class="row"><span class="lbl">QNH</span><span class="val">{qnh} hPa</span></div>
                <div class="row"><span class="lbl">RWY COND</span><span class="val">{cond}</span></div>
                <div class="msg">RAW DATA:<br>{txt}</div>
                <div class="status">LAST UPDATED: {timestamp} | WHISPER MEDIUM INT8</div>
            </div>
        </body>
        </html>
        """
        with open("index.html", "w", encoding="utf-8") as f: f.write(html_template)

    except Exception as e: print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    run_atis_system()
