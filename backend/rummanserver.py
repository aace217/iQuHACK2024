from flask import Flask, redirect, url_for, render_template, abort, request
from rgame import BoardState 
import json

games = {}  
unused_game_ids = [0]  

app = Flask(__name__, template_folder="../frontend")

@app.route("/")
def hello_world():
    return "<p>Welcome to the Entangled Game!</p>"

@app.route("/new_game", methods=["GET"])
def new_game():
    game_id = unused_game_ids.pop(0)
    unused_game_ids.append(game_id + 1)
    games[game_id] = BoardState()
    return redirect(url_for("play_game", game_id=game_id))

@app.route("/game/<game_id>", methods=["GET"])
def play_game(game_id):
    game_id = int(game_id)
    if game_id not in games:
        abort(404)
    game_state = games[game_id]
    return render_template("game.html", game_id=game_id, game_state=game_state)

@app.route("/game/<game_id>/measure", methods=["POST"])
def measure_trait(game_id):
    game_id = int(game_id)
    if game_id not in games:
        abort(404)
    
    data = request.json
    trait_index = data['trait_index'] 
    game_state = games[game_id]
    
    updated_matrix = game_state.updateBoard(trait_index)
    
    return json.dumps({"success": True, "updated_matrix": updated_matrix}), 200, {'ContentType':'application/json'}

if __name__ == "__main__":
    app.run(debug=True)
