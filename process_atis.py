#!/usr/bin/env python3
# process_atis.py
# Décode un message ATIS avec Mistral et génère JSON + HTML.

import os
import sys
import json
from bs4 import BeautifulSoup
from mistralai import Mistral

def ai_parse_atis(raw_text):
    """Appelle Mistral via le SDK pour décoder le texte ATIS en JSON."""

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("❌ ERREUR : clé Mistral manquante. Ajoutez MISTRAL_API_KEY dans les secrets GitHub.")
        return {k: "NaN" for k in [
            "atis_letter", "atis_time", "wind", "visibility", "runway", "rwy_cond",
            "clouds", "bird", "temp_dew", "qnh", "tl", "trend"
        ]}

    model = "mistral-small-latest"
    client = Mistral(api_key=api_key)

    prompt = (
        f"Extract the ATIS information from the following text and return strictly JSON:\n"
        f"{raw_text}\n"
        "If a field is missing, use 'NaN'.\n"
        "Output JSON with keys: "
        "atis_letter, atis_time, wind, visibility, runway, rwy_cond, clouds, "
        "bird, temp_dew, qnh, tl, trend"
    )

    try:
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )

        # Le texte généré est dans response.result
        atis_json_str = response.result.strip()

        # Nettoyage si Mistral ajoute ```json ... ```
        if atis_json_str.startswith("```json"):
            atis_json_str = atis_json_str.replace("```json", "").replace("```", "").strip()

        data = json.loads(atis_json_str)
        return data
    except Exception as e:
        print(f"⚠️ Réponse IA non strictement JSON ou erreur SDK : {e}")
        # Retour par défaut pour toutes les clés
        return {k: "NaN" for k in [
            "atis_letter", "atis_time", "wind", "visibility", "runway", "rwy_cond",
            "clouds", "bird", "temp_dew", "qnh", "tl", "trend"
        ]}

def render_html(data):
    """Transforme le JSON ATIS en bloc HTML simple."""
    return f"""<div id="atis-message">
    <div class="atis-header">
        Information {data.get('atis_letter','NaN')} — <span>{data.get('atis_time','NaN')}Z</span>
    </div>

    <div class="atis-info">
        <div><strong>Wind:</strong> {data.get('wind','NaN')}</div>
        <div><strong>Visibility:</strong> {data.get('visibility','NaN')}</div>
        <div><strong>Runway in use:</strong> {data.get('runway','NaN')}</div>
        <div><strong>Runway condition:</strong> {data.get('rwy_cond','NaN')}</div>
        <div><strong>Cloud:</strong> {data.get('clouds','NaN')}</div>
        <div><strong>Bird activity:</strong> {data.get('bird','NaN')}</div>
        <div><strong>Temperature / Dew point:</strong> {data.get('temp_dew','NaN')}</div>
        <div><strong>QNH:</strong> {data.get('qnh','NaN')} hPa</div>
        <div><strong>Transition level:</strong> {data.get('tl','NaN')}</div>
        <div><strong>Trend:</strong> {data.get('trend','NaN')}</div>
    </div>
</div>
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: process_atis.py <atis_raw_text_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file, "r", encoding="utf-8") as f:
        raw = f.read()

    data = ai_parse_atis(raw)

    # Export JSON
    with open("atis.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Export HTML
    with open("atis_structured.html", "w", encoding="utf-8") as f:
        f.write(render_html(data))

    print("✅ ATIS traité avec succès")
    print(json.dumps(data, indent=2))
