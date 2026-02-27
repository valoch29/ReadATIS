replacement_dict = {
    # --- Identification & Aéroport ---
    "INFLATION": "INFORMATION",
    "INFORMAATION": "INFORMATION",
    "DARWIN AIRPORT": "TALLINN AIRPORT",
    "DARLING AIRPORT": "TALLINN AIRPORT",
    "BUSINESS TALENT": "THIS IS TALLINN",
    "STARLIN": "TALLINN",
    "TELLING": "TALLINN",
    "STALIN": "TALLINN",
    "TALIN": "TALLINN",

    # --- Piste & RCC ---
    "PATCH DOWN": "TOUCHDOWN",
    "PACHYDOWN": "TOUCHDOWN",
    "MEET POINT": "MIDPOINT",
    "STOPEND": "STOP END",
    "STOP-END": "STOP END",
    "TOP-END": "STOP END",
    "PATRICK IN USE": "RUNWAY 26 IN USE", # Erreur détectée dans l'info Delta

    # --- Météo & LVP ---
    "CAPITAL K": "CAVOK",
    "CABO K": "CAVOK",
    "DEW POINT": "DEWPOINT", # Crucial pour l'info Delta
    "VIEW POINT": "DEWPOINT",
    "ESTHER PASCAL": "HPA",   # Erreur détectée dans l'info Delta
    "EXTRA PASCAL": "HPA",
    "HECTOPASCAL": "HPA",
    "LOW VISIBILITY PROCEDURES": "LVP ACTIVE", # Pour déclencher l'alerte

    # --- Chiffres & Alphabet (Sélection indispensable) ---
    "ZERO": "0", "ONE": "1", "TWO": "2", "THREE": "3", "FOUR": "4",
    "FIVE": "5", "SIX": "6", "SEVEN": "7", "EIGHT": "8", "NINE": "9",
    "095 0": "0950", # Correction spécifique pour l'heure
    "GULF": "G", "HOTEL": "H", "DELTA": "D", "VICTOR": "V",
    "KKNOTS": "KNOTS"
}
