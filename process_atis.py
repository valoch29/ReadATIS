#!/usr/bin/env python3
# process_atis.py
# Décodage ATIS via Mistral et génération de JSON + HTML

import os
import sys
import json
import re
import requests

# 🔹 Liste des clés ATIS principales
DEFAULT_KEYS = [
    "atis_letter", "atis_time", "wind", "visibility", "runway",
    "rwy_cond", "clouds", "bird", "temp_dew", "qnh", "tl", "trend"
]

# 🔹 Fonction pour extraire le JSON du texte brut Mistral
def extract_json_from_mistral(raw_response):
    match = re.search(r"```json\s*(\{.*?\})\s*```", raw_response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            print("⚠️ Impossible de parser le JSON extrait")
            return {}
    else:
        print("⚠️ Aucun bloc JSON trouvé, retour brut utilisé")
        return {}

# 🔹 Fonction pour appeler Mistral
def call_mistral_api(prompt):
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("❌ ERREUR : clé Mistral manquante. Ajoutez MISTRAL_API_KEY dans les secrets GitHub.")
        return {}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # ✅ Endpoint officiel Mistral
    model_id = "mistral-7b-instruct"  # Remplace par le modèle exact disponible sur ton compte
    url = f"https://api.mistral.ai/models/{model_id}/completions"

    payload = {
        "prompt": prompt,
        "max_new_tokens": 500
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"⚠️ Erreur IA : {response.status_code} - {response.text}")
            return {}

        # Mistral renvoie souvent un champ "output" ou "completion"; à vérifier
        raw_text = response.json().get("completion", "") or response.json().get("output", "")
        return extract_json_from_mistral(raw_text)

    except Exception as e:
        print(f"⚠️ Exception lors de l'appel API Mistral : {e}")
        return {}

# 🔹 Fonction pour générer HTML
def render_html(data):
    def safe_get(key):
        return data.get(key, "NaN")

    wind = safe_get("wind")
    wind_str = f"{wind.get('direction', 'NaN')} / {wind.get('speed', 'NaN')}" if isinstance(wind, dict) else "NaN"

    visibility = safe_get("visibility")
    visibility_str = visibility.get("min", "NaN") if isinstance(visibility, dict) else visibility

    clouds = safe_get("clouds")
    clouds_str = clouds.get("type", "NaN") if isinstance(clouds, dict) else clouds

    temp_dew = safe_get("temp_dew")
    temp_dew_str = f"{temp_dew.get('temperature','NaN')}°C / {temp_dew.get('dew_point','NaN')}°C" if isinstance(temp_dew, dict) else temp_dew

    trend = safe_get("trend")
    trend_str = trend.get("description","NaN") if isinstance(trend, dict) else trend

    html = f"""<div id="atis-message">
    <div class="atis-header">
        Information {safe_get('atis_letter')} — <span>{safe_get('atis_time')}</span>
    </div>
    <div class="atis-info">
        <div><strong>Wind:</strong> {wind_str}</div>
        <div><strong>Visibility:</strong> {visibility_str}</div>
        <div><strong>Runway in use:</strong> {safe_get('runway')}</div>
        <div><strong>Runway condition:</strong> {safe_get('rwy_cond')}</div>
        <div><strong>Cloud:</strong> {clouds_str}</div>
        <div><strong>Bird activity:</strong> {safe_get('bird')}</div>
        <div><strong>Temperature / Dew point:</strong> {temp_dew_str}</div>
        <div><strong>QNH:</strong> {safe_get('qnh')}</div>
        <div><strong>Transition level:</strong> {safe_get('tl')}</div>
        <div><strong>Trend:</strong> {trend_str}</div>
    </div>
</div>"""
    return html

# 🔹 Main
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: process_atis.py <atis_raw_text_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Appel Mistral
    data = call_mistral_api(raw_text)

    # Remplir NaN pour les champs manquants
    for key in DEFAULT_KEYS:
        if key not in data:
            data[key] = "NaN"

    # Export JSON
    with open("atis.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Export HTML
    with open("atis_structured.html", "w", encoding="utf-8") as f:
        f.write(render_html(data))

    print("✅ ATIS traité avec succès :")
    print(json.dumps(data, indent=2))
