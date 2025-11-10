#!/usr/bin/env python3
# process_atis.py — version Mistral API

import os
import json
import sys
import requests

def ai_parse_atis(raw_text):
    """Analyse un message ATIS en utilisant l’API Mistral."""

    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    if not mistral_api_key:
        print("❌ ERREUR : clé Mistral manquante. Ajoutez MISTRAL_API_KEY dans les secrets GitHub.")
        return {}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {mistral_api_key}"
    }

    data = {
        "model": "mistral-tiny",  # ou "mistral-medium" si disponible
        "messages": [
            {"role": "system", "content": "You are an aviation assistant. Parse ATIS messages into structured JSON."},
            {"role": "user", "content": f"Extract structured ATIS data from this message:\n{raw_text}\n\nReturn JSON with fields: atis_letter, atis_time, wind, visibility, runway, rwy_cond, clouds, bird, temp_dew, qnh, tl, trend."}
        ]
    }

    try:
        response = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]

        try:
            return json.loads(content)
        except:
            print("⚠️ Réponse IA non strictement JSON — retour brut utilisé.")
            return {"raw_response": content}

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Erreur API Mistral : {e}")
        return {}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: process_atis.py <atis_raw_text_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    data = ai_parse_atis(raw_text)

    if not data:
        # Valeurs par défaut
        data = {k: "NaN" for k in ["atis_letter", "atis_time", "wind", "visibility", "runway", "rwy_cond", "clouds", "bird", "temp_dew", "qnh", "tl", "trend"]}

    with open("atis.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("✅ ATIS traité avec succès :")
    print(json.dumps(data, indent=2))
