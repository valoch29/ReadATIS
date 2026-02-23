import datetime
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
    <title>EETN ATIS - Live AI</title>
    <style>
        body {{ font-family: sans-serif; background: #121212; color: white; padding: 40px; text-align: center; }}
        .box {{ background: #1e1e1e; padding: 25px; border-radius: 10px; border-left: 5px solid #007bff; display: inline-block; text-align: left; max-width: 80%; line-height: 1.6; }}
        .time {{ color: #888; font-size: 0.8em; margin-top: 20px; border-top: 1px solid #333; padding-top: 10px; }}
    </style>
</head>
<body>
    <h1>Tallinn Airport (EETN) - ATIS AI</h1>
    <div class="box">
        <p>{atis_text}</p>
        <p class="time">Dernière mise à jour : {now} UTC</p>
    </div>
</body>
</html>
'''
with open("index.html", "w") as f:
    f.write(html)
