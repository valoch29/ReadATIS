import datetime
import os
import re

# Valeurs par défaut
info, qnh, rwy, wind, temp_dew, vis, rcc, contamination = "-", "----", "--", "--- / --KT", "-- / --", "---", "-/-/-", "UNKNOWN"

if os.path.exists("atis_transcribed.txt"):
    with open("atis_transcribed.txt", "r", encoding="utf-8") as f:
        clean_text = f.read().upper()

    # --- EXTRACTION AMÉLIORÉE ---
    
    # 1. INFO (Gère "INFORMATION FOXTROT" ou "INFORMATION, FOXTROT")
    m_i = re.search(r"INFORMATION,?\s+([A-Z])", clean_text)
    if m_i: info = m_i.group(1)
    
    # 2. QNH
    m_q = re.search(r"QNH\s*(\d{4})", clean_text)
    if m_q: qnh = m_q.group(1)
    
    # 3. RUNWAY
    m_r = re.search(r"RUNWAY\s*(\d{2})", clean_text)
    if m_r: rwy = m_r.group(1)

    # 4. VENT (Ultra flexible pour gérer "050, DEGREES, 6 KNOTS")
    # On cherche 3 chiffres, puis du texte optionnel, puis la vitesse
    m_w = re.search(r"(\d{3}),?\s*DEGREES,?\s*(\d+)\s*KNOTS", clean_text)
    if m_w: 
        wind = f"{m_w.group(1)}° / {m_w.group(2).zfill(2)}KT"

    # 5. VISIBILITÉ (Gère "7 KM" ou "CAVOK")
    if "CAVOK" in clean_text:
        vis = "CAVOK"
    else:
        # Cherche le premier nombre (KM ou M) après le mot VISIBILITY
        m_v = re.search(r"VISIBILITY.*?(\d+)\s*(?:KM|M)?", clean_text)
        if m_v: vis = m_v.group(1) + " KM"

    # 6. TEMP / DEWPOINT
    def get_t(anchor, text):
        parts = text.split(anchor)
        if len(parts) > 1:
            m = re.search(r"(MINUS\s+)?(\d+)", parts[1])
            if m: return ("-" if m.group(1) else "") + m.group(2)
        return "--"
    temp_dew = f"{get_t('TEMPERATURE', clean_text)}° / {get_t('DEWPOINT', clean_text)}°"

    # 7. RCC (Piste)
    r1 = re.search(r"TOUCHDOWN\s*(\d)", clean_text)
    r2 = re.search(r"MIDPOINT\s*(\d)", clean_text)
    r3 = re.search(r"STOP END\s*(\d)", clean_text)
    if r1: rcc = f"{r1.group(1)}/{r2.group(1) if r2 else r1.group(1)}/{r3.group(1) if r3 else r1.group(1)}"

    # 8. CONTAMINATION
    states = [s for s in ["WET", "DRY", "WATER", "ICE", "SNOW", "SLUSH", "FROST"] if s in clean_text]
    if states: contamination = "/".join((states * 3)[:3])

now = datetime.datetime.now().strftime("%H:%M")

# --- LE RESTE DU CODE HTML (Gris & Blanc) ---
# ... (Gardez le même style CSS que précédemment) ...
