from flask import Flask, redirect, url_for, render_template
from game import BoardState, Trait

games: dict[int,BoardState] = dict()
unused_game_ids = [0]

app = Flask(__name__)
@app.route("/")
def hello_world():
	return "<p>Hello, World!</p>"

@app.route("/new", methods=["GET"])
def new_game():
	game_id = unused_game_ids.pop()
	unused_game_ids.append(game_id+1)
	games[game_id] = BoardState()
	return redirect(url_for("play", g_id=game_id))

@app.route("/play/<g_id>", methods=["GET"])
def play(g_id):
	if g_id not in games: return False
	c_state = games[g_id]
	return render_template("../frontend/finalTest.html", state = c_state)
	
@app.route("/play/<g_id>/measure/<target>", methods=["POST"])
def query(g_id, target: Trait):
	if g_id not in games: return False
	if target not in Trait: return False
	c_state = games[g_id]
	games[g_id] = c_state.measure(target)
	return games[g_id]

# @app.route("/play/<g_id>/query/<>", methods=["POST"])
# def 

if __name__ == "__main__":
	app.run(debug=True)