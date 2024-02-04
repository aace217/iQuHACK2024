from flask import Flask, render_template
import subprocess

app = Flask(__name__)

def hello(name='STICK_GUY'):
    return render_template('finalTest.html', name=name)