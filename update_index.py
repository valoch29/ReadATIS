#!/usr/bin/env python3
# update_index.py
# Met à jour le fichier index.html avec le contenu de atis_structured.html

import os

def update_atis_message():
    try:
        # Lire le contenu du fichier atis_structured.html
        with open("atis_structured.html", "r", encoding="utf-8") as atis_file:
            atis_content = atis_file.read().strip()

        # Lire le contenu actuel de index.html
        with open("index.html", "r", encoding="utf-8") as index_file:
            index_content = index_file.read()

        # Définir les balises de début et de fin pour la div 'atis-message'
        start_tag = '<div id="atis-message">'
        end_tag = '</div>'

        # Trouver l'index de la div 'atis-message'
        start_index = index_content.find(start_tag)
        if start_index == -1:
            raise ValueError("La balise <div id='atis-message'> n'a pas été trouvée dans index.html.")

        end_index = index_content.find(end_tag, start_index)
        if end_index == -1:
            raise ValueError("La balise </div> pour 'atis-message' n'a pas été trouvée.")

        # Remplacer TOUT le contenu entre les balises de la div
        updated_content = (
            index_content[:start_index + len(start_tag)] +
            atis_content +
            index_content[end_index:]
        )

        # Écrire le nouveau contenu dans index.html
        with open("index.html", "w", encoding="utf-8") as index_file:
            index_file.write(updated_content)

        print("Le fichier index.html a été mis à jour avec succès.")

    except FileNotFoundError as e:
        print(f"Erreur : Fichier introuvable - {e.filename}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")

if __name__ == "__main__":
    update_atis_message()
