from flask import Flask, render_template, request, jsonify
import subprocess
import json

#app = Flask(__name__,template_folder=".")

#@app.route("/",methods=["GET"])
#def sendData(tbd='#eb4034'):
#    return "e"

app = Flask(__name__, template_folder=".")

#Receives data from html
@app.route('process_data/', methods=['POST'])
def process_data():
    data = request.get_json()
    color = data.get('value')
    attribute = data.get('value2')
    print('Received value:', color)
    print('Received value:', attribute)
    return jsonify({'result': 'Data received successfully'})

#Sends data to html
@app.route('/')
def receiveData():
    return render_template('rFront4.html', view=[
            [2, 2, 2, 2],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1]
        ])

if __name__ == '__main__':
    app.run(debug=True)