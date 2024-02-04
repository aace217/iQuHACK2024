from flask import Flask, redirect, url_for, render_template, abort, send_file, request
from cgame import BoardState, Trait, CGate, Gate, Ops

c_games: dict[int,BoardState] = dict()
unused_cgame_ids = [0]

app = Flask(__name__,template_folder="../frontend")
@app.route("/")
def hello_world():
	return render_template("index.html")

@app.route("/new_c/", methods=["GET"])
def new_cgame():
	game_id = unused_cgame_ids.pop()
	unused_cgame_ids.append(game_id+1)
	c_games[game_id] = BoardState(remaining={i:99 for i in CGate}|{i:99 for i in Gate}|{i:99 for i in Ops})
	return redirect(url_for("play_c", g_id=game_id))

@app.route("/play_c/<g_id>/", methods=["GET"])
def play_c(g_id):
	g_id = int(g_id)
	if g_id not in c_games: abort(404)
	c_state = c_games[g_id]
	return render_template("cFront.html", g_id = g_id, state = c_state, view = c_state.render_probs())
	
@app.route("/play_c/<g_id>/measure/", methods=["POST"])
def c_measure(g_id):
	print(request.form)
	try:
		target = request.form.get("target")
		g_id, target = int(g_id), int(target)
	except: abort(400)
	if g_id not in c_games: abort(400)
	if target not in Trait: abort(400)
	c_state = c_games[g_id]
	c_games[g_id] = c_state.measure(target)
	return redirect(url_for("play_c", g_id=g_id)) #c_games[g_id]

@app.route("/play_c/<g_id>/gate/", methods=["POST"])
def c_gate(g_id):
	print(request.form)
	try:
		gate, target = request.form.get("gate"),request.form.get("target")
		g_id, gate, target = int(g_id), int(gate), int(target)
		gate = [Gate.H,Gate.X,Gate.Z,CGate.CX,CGate.CZ][gate]
		print(gate)
	except: abort(400)
	if g_id not in c_games:
		abort(400)
	c_state = c_games[g_id]
	if "source" in request.form:
		source = int(request.form.get("source"))
		if not isinstance(gate,CGate) or source == target: abort(400)
		c_games[g_id] = c_state.c_gate(gate,source,target)
	else:
		if not isinstance(gate,Gate): abort(400)
		c_games[g_id] = c_state.gate(gate,target)
	return redirect(url_for("play_c", g_id=g_id)) #c_games[g_id]

@app.route("/play_c/<g_id>/draw/",methods=["GET"])
def c_draw(g_id):
	g_id = int(g_id)
	if g_id not in c_games: abort(404)
	# return c_games[g_id].draw()
	c_games[g_id].draw("./ccache/"+str(g_id))
	return send_file("./ccache/"+str(g_id)+".png")

# @app.route("/play/<g_id>/query/<>", methods=["POST"])
# def 

# @app.errorhandler(404)
# def not_found(_):
# 	return redirect("/")
	


if __name__ == "__main__":
	app.run(debug=True)