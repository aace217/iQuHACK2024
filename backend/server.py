from flask import Flask, redirect, url_for, render_template, abort, send_file, request, jsonify
from cgame import BoardState as cBoardState, Trait, CGate, Gate, Ops
from rgame import BoardState as rBoardState, COLORS, TRAITS
import json

c_games: dict[int,cBoardState] = dict()
unused_cgame_ids = [0]
games = {}  
unused_game_ids = [0]  


app = Flask(__name__,template_folder="../frontend")
@app.route("/")
def hello_world():
	return render_template("index.html")

@app.route("/new_c/", methods=["GET"])
def new_cgame():
	game_id = unused_cgame_ids.pop()
	unused_cgame_ids.append(game_id+1)
	c_games[game_id] = cBoardState(remaining={i:99 for i in CGate}|{i:99 for i in Gate}|{i:99 for i in Ops})
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
	

@app.route("/new_r/", methods=["GET"])
def new_game():
    game_id = unused_game_ids.pop(0)
    unused_game_ids.append(game_id + 1)
    games[game_id] = rBoardState()
    return redirect(url_for("play_r", game_id=game_id))

@app.route("/play_r/<game_id>/", methods=["GET"])
def play_r(game_id):
    game_id = int(game_id)
    if game_id not in games:
        abort(404)
    game_state = games[game_id]
    return render_template("rFront4.html", game_id=game_id, game_state=game_state, view=game_state.currentMatrix.tolist())

@app.route("/play_r/<game_id>/measure/", methods=["POST"])
def measure_trait(game_id):
    game_id = int(game_id)
    if game_id not in games:
        abort(404)
    
    data = request.get_json()
    color = COLORS.index(data.get('value'))
    attribute = TRAITS.index(data.get('value2'))
    print('Received value:', color)
    print('Received value:', attribute)
    game_state = games[game_id]
    
    updated_matrix = game_state.updateMatrix(attribute)
    
    return json.dumps({"success": True, "updated_matrix": updated_matrix}), 200, {'ContentType':'application/json'}


#Sends data to html
@app.route('/process_data/')
def receiveData():
    return render_template('rFront4.html', view=[
            [2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
        ])

if __name__ == "__main__":
	app.run(debug=True)