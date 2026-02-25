import os
from faster_whisper import WhisperModel
import dictionary

def run_atis_system():
    audio_file = "atis_recorded.wav"
    
    # 1. Vérification du fichier
    if not os.path.exists(audio_file):
        print(f"ERREUR : {audio_file} introuvable.")
        return

    # 2. Transcription avec le modèle optimisé pour GitHub
    print("Chargement du modèle IA (CPU mode)...")
    try:
        # On utilise 'small' et 'int8' pour que ça tourne vite sur le serveur gratuit
        model = WhisperModel("small", device="cpu", compute_type="int8")
        
        print("Transcription en cours...")
        segments, info = model.transcribe(audio_file, beam_size=5)
        
        full_text = ""
        for segment in segments:
            full_text += segment.text + " "
        
        full_text = full_text.upper().strip()
        print(f"Texte décodé : {full_text}")

        # 3. Traitement avec ton dictionnaire
        processed_text = full_text
        for word, replacement in dictionary.replacement_dict.items():
            processed_text = processed_text.replace(word.upper(), replacement)

        # 4. Génération de l'HTML
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
                .raw-text {{ color: #888; font-size: 0.9em; margin-top: 20px; font-style: italic; }}
                .timestamp {{ text-align: right; font-size: 0.8em; color: #555; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>TALLINN ATIS DECODER</h1>
                <p><strong>Message décodé :</strong></p>
                <p>{processed_text}</p>
                <div class="raw-text">Texte brut : {full_text}</div>
                <hr>
                <div class="timestamp">Dernière mise à jour : {os.popen('date').read()}</div>
            </div>
        </body>
        </html>
        """

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print("Succès : index.html a été mis à jour.")

    except Exception as e:
        print(f"Erreur pendant le traitement : {e}")

# IMPORTANT : Cette ligne lance le script
if __name__ == "__main__":
    run_atis_system()
