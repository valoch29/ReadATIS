import os
import dictionary  # <--- IL MANQUAIT CET IMPORT
from faster_whisper import WhisperModel

def run_atis_system():
    audio_file = "atis_recorded.wav"
    
    if not os.path.exists(audio_file):
        print(f"ERREUR : {audio_file} introuvable.")
        return

    print("Chargement du modèle IA (CPU mode)...")
    try:
        # Configuration optimisée pour GitHub Actions
        model = WhisperModel("small", device="cpu", compute_type="int8")
        
        print("Transcription en cours...")
        segments, info = model.transcribe(audio_file, beam_size=5)
        
        full_text = ""
        for segment in segments:
            full_text += segment.text + " "
        
        full_text = full_text.upper().strip()
        print(f"Texte décodé : {full_text}")

        # Traitement avec le dictionnaire
        processed_text = full_text
        # On vérifie que replacement_dict existe dans dictionary.py
        if hasattr(dictionary, 'replacement_dict'):
            for word, replacement in dictionary.replacement_dict.items():
                processed_text = processed_text.replace(word.upper(), replacement)
        else:
            print("Attention : replacement_dict non trouvé dans dictionary.py")

        # Génération de l'HTML
        html_content = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ATIS Tallinn Dashboard</title>
            <style>
                body {{ font-family: 'Courier New', monospace; background-color: #121212; color: #00FF00; padding: 20px; }}
                .container {{ border: 2px solid #00FF00; padding: 20px; border-radius: 10px; max-width: 800px; margin: auto; }}
                h1 {{ text-align: center; border-bottom: 1px solid #00FF00; padding-bottom: 10px; }}
                .message {{ white-space: pre-wrap; line-height: 1.6; font-size: 1.2em; }}
                .raw-text {{ color: #888; font-size: 0.9em; margin-top: 20px; font-style: italic; border-top: 1px dashed #333; padding-top: 10px; }}
                .timestamp {{ text-align: right; font-size: 0.8em; color: #555; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>TALLINN ATIS DECODER</h1>
                <p><strong>Message décodé :</strong></p>
                <div class="message">{processed_text}</div>
                <div class="raw-text">Texte brut IA : {full_text}</div>
                <div class="timestamp">Dernière mise à jour : {os.popen('date').read()}</div>
            </div>
        </body>
        </html>
        """

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print("Succès : index.html mis à jour.")

    except Exception as e:
        print(f"Erreur pendant le traitement : {e}")

if __name__ == "__main__":
    run_atis_system()
