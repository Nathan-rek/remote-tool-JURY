from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

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
    app.run(debug=True)
