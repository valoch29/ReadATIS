#!/usr/bin/env python3
# process_atis.py
# Uses an AI model to parse ATIS raw text into structured data.
# Missing information is set to "NaN".

import sys
import json
import openai  # Assurez-vous d'avoir configuré OPENAI_API_KEY

def ai_parse_atis(raw_text):
    """
    Sends raw ATIS text to an AI model and returns structured data as dict.
    The AI is instructed to output JSON with fixed keys.
    """
    prompt = f"""
You are an expert in ATIS (Automatic Terminal Information Service) messages.
Extract all relevant parameters from the following raw ATIS text and return a JSON object.
If a value is missing, set it to "NaN".

Keys to extract:
- atis_letter
- atis_time (format HHMMZ)
- wind (e.g., 270° / 15 kt, include variability if any)
- visibility (e.g., 10 km)
- runway (comma-separated if multiple)
- rwy_cond
- clouds
- bird
- temp_dew (e.g., 7°C / 7°C)
- qnh
- tl
- trend

ATIS text:
\"\"\"{raw_text}\"\"\"
Return only valid JSON.
"""
    # Call the AI model
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    # Extract content
    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        print("⚠️ Failed to parse AI output, returning NaN defaults.")
        keys = ["atis_letter","atis_time","wind","visibility","runway","rwy_cond","clouds","bird","temp_dew","qnh","tl","trend"]
        data = {k:"NaN" for k in keys}
    
    return data

def render_html(data):
    """Render structured ATIS data into HTML format."""
    return f"""<div id="atis-message">
    <div class="atis-header">
        Information {data['atis_letter']} — <span>{data['atis_time']}Z</span>
    </div>

    <div class="atis-info">
        <div><strong>Wind:</strong> {data['wind']}</div>
        <div><strong>Visibility:</strong> {data['visibility']}</div>
        <div><strong>Runway in use:</strong> {data['runway']}</div>
        <div><strong>Runway condition:</strong> {data['rwy_cond']}</div>
        <div><strong>Cloud:</strong> {data['clouds']}</div>
        <div><strong>Bird activity:</strong> {data['bird']}</div>
        <div><strong>Temperature / Dew point:</strong> {data['temp_dew']}</div>
        <div><strong>QNH:</strong> {data['qnh']} hPa</div>
        <div><strong>Transition level:</strong> {data['tl']}</div>
        <div><strong>Trend:</strong> {data['trend']}</div>
    </div>
</div>
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: process_atis.py <atis_raw_text_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    with open(input_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # AI-based parsing
    data = ai_parse_atis(raw_text)

    # Export JSON
    with open("atis.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Export HTML
    with open("atis_structured.html", "w", encoding="utf-8") as f:
        f.write(render_html(data))

    print("✅ ATIS processed successfully:")
    print(json.dumps(data, indent=2))
