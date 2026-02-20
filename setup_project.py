import os
import shutil

def setup():
    # 1. Liste des fichiers à supprimer (ménage)
    to_delete = [
        'decode_atis.yml', 'record_atis.yml', 'transcribe_atis.yml', # Anciens workflows
        'atis.json', 'atis_decoded.txt', 'atis_structured.html', 
        'atis_transcribed.txt' # On repart sur du propre
    ]
    
    # Suppression dans la racine et dans .github/workflows
    for f in to_delete:
        paths = [f, os.path.join('.github/workflows', f)]
        for p in paths:
            if os.path.exists(p):
                os.remove(p)
                print(f"🗑️ Supprimé : {p}")

    # 2. Création de l'arborescence
    os.makedirs('.github/workflows', exist_ok=True)

    # 3. Création du WORKFLOW UNIQUE (pipeline.yml)
    pipeline_content = """name: Tallinn ATIS Pipeline
on:
  schedule:
    - cron: '25 * * * *'
    - cron: '55 * * * *'
  workflow_dispatch:

jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install FFmpeg
        run: sudo apt-get update && sudo apt-get install -y ffmpeg

      - name: Record Audio (180s)
        run: ffmpeg -i https://icecast.kobly.com/eetn2_atis -t 180 -acodec pcm_s16le -ar 16000 atis_recorded.wav -y

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install AI Tools
        run: pip install faster-whisper

      - name: Run AI & Update HTML
        run: |
          python process_atis.py
          python update_index.py

      - name: Commit & Push
        run: |
          git config --global user.name 'ATIS-Bot'
          git config --global user.email 'bot@github.com'
          git add atis_recorded.wav index.html atis_transcribed.txt
          git commit -m "Update ATIS $(date)" || exit 0
          git push
"""
    with open('.github/workflows/pipeline.yml', 'w') as f:
        f.write(pipeline_content)
    print("✅ Créé : .github/workflows/pipeline.yml")

    # 4. Création du SCRIPT IA (process_atis.py)
    process_content = """import os
from faster_whisper import WhisperModel

# Modèle Medium pour la fidélité
model = WhisperModel("medium.en", device="cpu", compute_type="int8")

def transcribe():
    prompt = "Tallinn Airport ATIS, Information, Runway, QNH, Hectopascals, Temperature, Dewpoint, NOSIG."
    segments, _ = model.transcribe("atis_recorded.wav", beam_size=5, initial_prompt=prompt)
    
    text = " ".join([s.text for s in segments])
    
    # Nettoyage simple
    text = text.replace("hecto pascals", "hectopascals").replace("Q and H", "QNH")
    
    with open("atis_transcribed.txt", "w") as f:
        f.write(text)

if __name__ == "__main__":
    if os.path.exists("atis_recorded.wav"):
        transcribe()
"""
    with open('process_atis.py', 'w') as f:
        f.write(process_content)
    print("✅ Créé : process_atis.py")

    # 5. Création du SCRIPT HTML (update_index.py)
    update_content = """import datetime
import os

atis_text = "En attente de données..."
if os.path.exists("atis_transcribed.txt"):
    with open("atis_transcribed.txt", "r") as f:
        atis_text = f.read()

now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>EETN ATIS</title>
    <style>
        body {{ font-family: sans-serif; background: #121212; color: white; padding: 40px; text-align: center; }}
        .box {{ background: #1e1e1e; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; display: inline-block; text-align: left; max-width: 80% }}
        .time {{ color: #888; font-size: 0.8em; }}
    </style>
</head>
<body>
    <h1>Tallinn Airport ATIS</h1>
    <div class="box">
        <p>{atis_text}</p>
        <p class="time">Mise à jour : {now} UTC</p>
    </div>
</body>
</html>
'''
with open("index.html", "w") as f:
    f.write(html)
"""
    with open('update_index.py', 'w') as f:
        f.write(update_content)
    print("✅ Créé : update_index.py")

if __name__ == "__main__":
    setup()
    print("\\n🚀 Ton architecture est prête ! Tu peux maintenant commit et push.")
