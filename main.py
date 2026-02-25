import os
import sys
import re

# Sécurité installation
try:
    from faster_whisper import WhisperModel
except ImportError:
    os.system('pip install faster-whisper')
    from faster_whisper import WhisperModel

# Chargement du dictionnaire
replacement_dict = {}
if os.path.exists("dictionary.py"):
    try:
        with open("dictionary.py", "r", encoding="utf-8") as f:
            local_vars = {}
            exec(f.read(), {}, local_vars)
            replacement_dict = local_vars.get('replacement_dict', {})
    except Exception:
        pass

def run_atis_system():
    audio_file = "atis_recorded.wav"
    if not os.path.exists(audio_file): return

    try:
        model = WhisperModel("small", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_file, beam_size=5)
        full_text = " ".join([s.text for s in segments]).upper().strip()
        
        # Application dictionnaire
        processed_text = full_text
        for word, replacement in sorted(replacement_dict.items(), key=lambda x: len(x[0]), reverse=True):
            processed_text = processed_text.replace(word.upper(), replacement)

        # Extraction rapide de paramètres (Regex)
        info_letter = re.search(r"INFORMATION\s+([A-Z])", processed_text)
        info_letter = info_letter.group(1) if info_letter else "N/A"
        qnh = re.search(r"QNH\s+(\d+)", processed_text)
        qnh = qnh.group(1) if qnh else "N/A"

        timestamp = os.popen('date -u +"%H:%M UTC"').read().strip()

        html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ATIS TALLINN LIVE</title>
            <style>
                :root {{ --bg: #121212; --card: #1e1e1e; --text: #e0e0e0; --accent: #ffffff; --border: #333; }}
                body {{ background: var(--bg); color: var(--text); font-family: 'Inter', -apple-system, sans-serif; margin: 0; padding: 20px; display: flex; justify-content: center; }}
                .container {{ max-width: 800px; width: 100%; }}
                header {{ border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: baseline; }}
                h1 {{ font-size: 1.2rem; letter-spacing: 2px; color: var(--accent); margin: 0; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-bottom: 30px; }}
                .stat-card {{ background: var(--card); padding: 15px; border-radius: 8px; border: 1px solid var(--border); text-align: center; }}
                .stat-label {{ font-size: 0.7rem; color: #888; text-transform: uppercase; margin-bottom: 5px; }}
                .stat-value {{ font-size: 1.4rem; font-weight: bold; color: var(--accent); }}
                .main-msg {{ background: var(--card); padding: 25px; border-radius: 12px; line-height: 1.6; font-size: 1.1rem; border: 1px solid var(--border); box-shadow: 0 4px 20px rgba(0,0,0,0.3); white-space: pre-wrap; }}
                .raw-zone {{ margin-top: 30px; font-size: 0.75rem; color: #555; font-family: monospace; }}
                .footer {{ margin-top: 40px; font-size: 0.7rem; color: #444; text-align: center; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>TALLINN ATIS</h1>
                    <div style="font-size: 0.8rem; color: #888;">{timestamp}</div>
                </header>

                <div class="grid">
                    <div class="stat-card"><div class="stat-label">Information</div><div class="stat-value">{info_letter}</div></div>
                    <div class="stat-card"><div class="stat-label">QNH</div><div class="stat-value">{qnh}</div></div>
                    <div class="stat-card"><div class="stat-label">Runway</div><div class="stat-value">08</div></div>
                </div>

                <div class="main-msg">{processed_text}</div>

                <div class="raw-zone">
                    <strong>RAW DATA:</strong><br>{full_text}
                </div>

                <div class="footer">Automatic Transcription System • EETN ATIS</div>
            </div>
        </body>
        </html>
        """
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    run_atis_system()
