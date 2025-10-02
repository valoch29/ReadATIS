from bs4 import BeautifulSoup

# Charger index.html
with open("index.html", "r") as f:
    soup = BeautifulSoup(f, "html.parser")

# Charger le nouveau contenu ATIS
with open("atis_structured.html", "r") as f:
    new_content = BeautifulSoup(f.read(), "html.parser")

# Trouver la div cible
target_div = soup.find("div", {"id": "atis-message"})

# Vider et remplacer le contenu
target_div.clear()
for elem in new_content.contents:
    target_div.append(elem)

# Réécrire index.html
with open("index.html", "w") as f:
    f.write(str(soup))
