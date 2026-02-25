import os
import sys
from faster_whisper import WhisperModel

# --- CHARGEMENT SÉCURISÉ DU DICTIONNAIRE ---
replacement_dict = {}
try:
    # On ajoute le répertoire courant au chemin de recherche Python
    sys.path.append(os.getcwd())
    import dictionary
    replacement_dict = getattr(dictionary, 'replacement_dict', {})
    print("Dictionnaire chargé via import standard.")
except ImportError:
    print("Import standard échoué, lecture directe du fichier...")
    if os.path.exists("dictionary.py"):
        try:
            with open("dictionary.py", "r", encoding="utf-8") as f:
                # On exécute le contenu du fichier dans un environnement local
                local_vars = {}
                exec(f.read(), {}, local_vars)
                replacement_dict = local_vars.get('replacement_dict', {})
                print("Dictionnaire chargé via lecture directe.")
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier dictionnaire : {e}")

def run_atis_system():
    audio_file = "atis_recorded.wav"
    
    # 1. Vérification de l'existence de l'audio
    if not os.path.exists(audio_file):
        print(f"ERREUR : {audio_file} introuvable. Le workflow Record a-t-il réussi ?")
        return

    # 2. Transcription avec Whisper (Optimisé CPU)
    print("Chargement du modèle IA (small / cpu / int8)...")
    try:
        model = WhisperModel("small", device="cpu", compute_type="int8")
        
        print("Transcription en cours...")
        segments, info = model.transcribe(audio_file, beam_size=5)
        
        full_text = ""
        for segment in segments:
            full_text += segment.text + " "
        
        full_text = full_text.upper().strip()
        print(f"Texte brut IA : {full_text}")

        # 3. Application du dictionnaire de remplacement
        processed_text = full_text
        if replacement_dict:
            # On trie par longueur de mot (décroissant) pour éviter de remplacer des morceaux de mots
            sorted_words = sorted(replacement_dict.keys(), key=len, reverse=True)
            for word in sorted_words:
                replacement = replacement_dict[word]
                processed_text = processed_text.replace(word.upper(), replacement)
        else:
            print("Attention : Aucun dictionnaire de remplacement trouvé.")

        # 4. Génération du fichier HTML
        timestamp = os.popen('date -u +"%d/%m/%Y %H:%M UTC"').read().strip()
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ATIS Tallinn Dashboard</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0b0e14; color: #e0e6ed; padding: 20px; line-height: 1.6; }}
                .container {{ border: 1px solid #30363d; padding: 30px; border-radius: 12px; max-width: 900px; margin: auto; background-color: #161b22; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }}
                h1 {{ text-align: center; color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 15px; margin-top: 0; }}
                .message {{ background: #0d1117; padding: 20px; border-left: 4px solid #238636; font-family: 'Courier New', monospace; font-size: 1.3em; color: #7ee787; white-space: pre-wrap; margin: 20px 0; }}
                .raw-text {{ color: #8b949e; font-size: 0.85em; margin-top: 30px; padding: 10px; border-top: 1px dashed #30363d; }}
                .footer {{ text-align: right; font-size: 0.8em; color: #484f58; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>TALLINN ATIS LIVE</h1>
                <p><strong>Dernière transcription décodée :</strong></p>
                <div class="message">{processed_text}</div>
                <div class="raw-text">Flux brut (IA) : {full_text}</div>
                <div class="footer">Mis à jour le : {timestamp}</div>
            </div>
        </body>
        </html>
        """

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print("Succès : index.html généré avec succès.")

    except Exception as e:
        print(f"Erreur fatale pendant le traitement : {e}")

if __name__ == "__main__":
    run_atis_system()
