import os
import sys

# On force l'installation au cas où le workflow ferait défaut (Sécurité ultime)
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
    except Exception as e:
        print(f"Erreur dictionnaire : {e}")

def run_atis_system():
    audio_file = "atis_recorded.wav"
    
    if not os.path.exists(audio_file):
        print("Audio introuvable.")
        return

    try:
        print("Initialisation IA...")
        model = WhisperModel("small", device="cpu", compute_type="int8")
        
        print("Transcription...")
        segments, info = model.transcribe(audio_file, beam_size=5)
        
        full_text = " ".join([segment.text for segment in segments]).upper().strip()
        
        # Application du dictionnaire
        processed_text = full_text
        for word, replacement in sorted(replacement_dict.items(), key=lambda x: len(x[0]), reverse=True):
            processed_text = processed_text.replace(word.upper(), replacement)

        # Génération HTML
        timestamp = os.popen('date -u +"%H:%M UTC"').read().strip()
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ATIS TALLINN</title>
            <style>
                body {{ background: #000; color: #0f0; font-family: monospace; padding: 20px; }}
                .box {{ border: 1px solid #0f0; padding: 20px; max-width: 800px; margin: auto; }}
                .msg {{ font-size: 1.5em; margin: 20px 0; color: #fff; }}
                .raw {{ color: #444; font-size: 0.8em; }}
            </style>
        </head>
        <body>
            <div class="box">
                <h1>TALLINN ATIS LIVE</h1>
                <div class="msg">{processed_text}</div>
                <div class="raw">Brut: {full_text}</div>
                <div style="text-align:right">{timestamp}</div>
            </div>
        </body>
        </html>
        """
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Terminé avec succès.")

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    run_atis_system()
