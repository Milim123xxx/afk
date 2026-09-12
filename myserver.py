from flask import Flask
from threading import Thread

app = Flask("")

@app.route("/")
def home():
    return "Discord bot is running!"

def run():
    app.run(host="0.0.0.0", port=8080, use_reloader=False)

def server_on():
    t = Thread(target=run, daemon=True)
    t.start()
