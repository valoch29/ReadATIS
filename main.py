# --- EXTRACTION SÉCURISÉE ---
        def extract(pattern, text, default="---"):
            matches = re.findall(pattern, text)
            return matches[-1] if matches else default # On prend le dernier match (le plus récent)

        # 1. Lettre d'information (Prend la dernière citée)
        val_info = extract(r"INFORMATION[\s,]+([A-Z])", processed_text)

        # 2. Runway
        val_rwy = extract(r"RUNWAY[\s,]+(\d+)", processed_text, "08")

        # 3. QNH
        val_qnh = extract(r"QNH[\s,]+(\d{4})", processed_text, "----")
        
        # 4. VENT (Gestion de KKNOTS, KNOTS et DEGREES)
        # On cherche : 3 chiffres + DEGREES + (optionnel "VARIABLE BETWEEN...") + force + KNOTS
        wind_m = re.search(r"(\d{3})[\s,]*DEGREES[\s,].*?(\d+)[\s,]*K*NOTS", processed_text)
        if "CALM" in processed_text:
            val_wind = "CALM"
        elif wind_m:
            val_wind = f"{wind_m.group(1)}° / {wind_m.group(2)}KT"
        else:
            val_wind = "--- / --KT"
        
        # 5. TEMPÉRATURES
        temp_m = re.search(r"TEMPERATURE[\s,]+(?:MINUS[\s,]+)?(\d+)[\s,]+DEW[\s,]*POINT[\s,]+(?:MINUS[\s,]+)?(\d+)", processed_text)
        if temp_m:
            # Vérification signe température
            t_text = processed_text.split("DEW")[0]
            t_sgn = "-" if "MINUS" in t_text else ""
            # Vérification signe dew point
            d_text = processed_text.split("DEW")[-1]
            d_sgn = "-" if "MINUS" in d_text else ""
            val_temp = f"{t_sgn}{temp_m.group(1)}° / {d_sgn}{temp_m.group(2)}°"
        else:
            val_temp = "-- / --"

        # 6. RUNWAY CONDITION (6/6/6)
        cond_m = re.search(r"TOUCHDOWN[\s,]+(\d)[\s,]+MIDPOINT[\s,]+(\d)[\s,]+STOP[\s,]*END[\s,]+(\d)", processed_text)
        val_cond = f"{cond_m.group(1)} / {cond_m.group(2)} / {cond_m.group(3)}" if cond_m else "6 / 6 / 6"
