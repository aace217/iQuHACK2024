from flask import Flask, redirect, url_for, render_template, abort
from cgame import BoardState, Trait, CGate, Gate

c_games: dict[int,BoardState] = dict()
unused_cgame_ids = [0]

app = Flask(__name__,template_folder="../frontend")
@app.route("/")
def hello_world():
	return "<p>Hello, World!</p>"

@app.route("/new_c", methods=["GET"])
def new_cgame():
	game_id = unused_cgame_ids.pop()
	unused_cgame_ids.append(game_id+1)
	c_games[game_id] = BoardState()
	return redirect(url_for("play", g_id=game_id))

@app.route("/play_c/<g_id>", methods=["GET"])
def play_c(g_id):
	g_id = int(g_id)
	if g_id not in c_games: abort(404)
	c_state = c_games[g_id]
	return render_template("finalTest.html", state = c_state, view = c_state.render_probs())
	
@app.route("/play_c/<g_id>/measure/<target>", methods=["POST"])
def c_measure(g_id, target: Trait):
	g_id, target = int(g_id), int(target)
	if g_id not in c_games: abort(500)
	if target not in Trait: abort(500)
	c_state = c_games[g_id]
	c_games[g_id] = c_state.measure(target)
	return redirect(url_for("play_c", g_id=g_id)) #c_games[g_id]

@app.route("/play_c/<g_id>/gate/<gate>/<target>", methods=["POST"])
def c_gate(g_id, gate, target):
	g_id, gate, target = int(g_id), int(gate), int(target)
	if g_id not in c_games or gate not in Gate or target not in Trait: 
		abort(500)
	c_state = c_games[g_id]
	c_games[g_id] = c_state.gate(gate,target)
	return redirect(url_for("play_c", g_id=g_id)) #c_games[g_id]

@app.route("/play_c/<g_id>/cgate/<gate>/<source>/<target>", methods=["POST"])
def c_cgate(g_id, cgate, source, target):
	g_id, cgate, source, target = int(g_id), int(cgate), int(source), int(target)
	if g_id not in c_games or cgate not in CGate or source not in Trait or target not in Trait: abort(500)
	c_state = c_games[g_id]
	c_games[g_id] = c_state.c_gate(c_gate,source,target)
	return redirect(url_for("play_c", g_id=g_id)) #c_games[g_id]

# @app.route("/play/<g_id>/query/<>", methods=["POST"])
# def 




if __name__ == "__main__":
	app.run(debug=True)