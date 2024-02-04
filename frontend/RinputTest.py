from flask import Flask, render_template, request, jsonify
import subprocess
import json

app = Flask(__name__,template_folder=".")

@app.route("/",methods=["GET"])
def sendData(tbd='#eb4034'):
    return render_template('rFront.html', view=[
            [2, 2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1]
        ])

@app.route('/process_data', methods=['POST'])
def process_data():
    data = request.get_json()
    result = data.get('value')  # Assuming 'value' is the key in the sent JSON
    return jsonify({'result': result})

app.run(debug=True)