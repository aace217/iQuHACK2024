from flask import Flask, render_template, request, jsonify
import subprocess
import json

#app = Flask(__name__,template_folder=".")

#@app.route("/",methods=["GET"])
#def sendData(tbd='#eb4034'):
#    return "e"

app = Flask(__name__, template_folder=".")

@app.route('/process_data', methods=['POST'])
def process_data():
    data = request.get_json()
    value = data.get('value')
    print('Received value:', value)
    return jsonify({'result': 'Data received successfully'})

@app.route('/')
def index():
    return render_template('rFront4.html')

if __name__ == '__main__':
    app.run(debug=True)