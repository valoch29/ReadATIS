#!/usr/bin/env python3
# update_index.py — met à jour ou crée le bloc ATIS dans index.html

from bs4 import BeautifulSoup
import json
import os

def main():
    if not os.path.exists("atis_structured.html"):
        print("❌ Fichier atis_structured.html introuvable.")
        return

    # Lire les fichiers
    with open("atis_structured.html", "r", encoding="utf-8") as f:
        atis_html = f.read()

    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            index_html = f.read()
    else:
        index_html = "<html><head><title>ATIS</title></head><body><h1>ATIS Dashboard</h1></body></html>"

    soup = BeautifulSoup(index_html, "html.parser")

    # Rechercher ou créer le bloc ATIS
    atis_block = soup.find("div", {"id": "atis-message"})
    if atis_block:
        atis_block.replace_with(BeautifulSoup(atis_html, "html.parser"))
        print("✅ Bloc ATIS mis à jour dans index.html.")
    else:
        # Ajouter le bloc à la fin du <body>
        body = soup.find("body")
        if not body:
            body = soup.new_tag("body")
            soup.append(body)

        new_block = BeautifulSoup(atis_html, "html.parser")
        body.append(new_block)
        print("🆕 Bloc ATIS ajouté à index.html.")

    # Sauvegarder le résultat
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(str(soup))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
