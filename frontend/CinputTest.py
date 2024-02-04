from flask import Flask, render_template
import subprocess

app = Flask(__name__,template_folder=".")
@app.route("/",methods=["GET"])
def sendData(tbd='#eb4034'):
    return render_template('cFront.html', view=[
            [2, 2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1]
        ])

app.run(debug=True)