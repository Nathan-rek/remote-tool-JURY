from flask import Flask, render_template, request, jsonify
from flask_flatpages import FlatPages
import os

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/remote-jury'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FLATPAGES_MARKDOWN_EXTENSIONS = ['extra']
FLATPAGES_EXTENSION_CONFIGS = {
    'codehilite': {
        'linenums': 'True'
    }
}

app.config.from_object(__name__)
pages = FlatPages(app)
application = app
pages.get('foo')

video_state = {
    "action": "pause",  # play/pause/none
    "seek": 0           # secondes à sauter, peut être positif ou négatif
}

@app.route("/")
def controller():
    return render_template("controller.html")

@app.route("/player")
def player():
    return render_template("player.html")

@app.route("/command", methods=["POST"])
def command():
    action = request.form.get("action")
    if action in ["play", "pause"]:
        video_state["action"] = action
    elif action == "forward":
        video_state["seek"] += 15
    elif action == "rewind":
        video_state["seek"] -= 15
    elif action == "seek_done":
        video_state["seek"] = 0
    return "", 204

@app.route("/state")
def state():
    return jsonify(video_state)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
